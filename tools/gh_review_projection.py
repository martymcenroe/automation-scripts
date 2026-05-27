"""GitHub code-review projection -- "how close am I to the 1% graph spoke."

Default output is three load-bearing lines + a command:

    TODAY      N merged · ratio X% (above/below 0.50% threshold)
    BACKLOG    M open dependabot PRs (top-3 repos, +K more)
    ACTION     DRAIN NOW (below) | Optional drain (above)
               -> Start-ScheduledTask -TaskName 'Claude-DependabotFleet'

`--verbose` adds a DETAIL block with the per-window math, widget/API scale,
all-time count, and full backlog breakdown. See automation-scripts#62 for
the redesign rationale (the previous WHERE YOU ARE / WHAT IT TAKES /
WILL IT STICK / DO-NOTHING layout was contradictory and not actionable).

Denominator: contributionCalendar.totalContributions -- the all-types,
all-restrictions count over the window. This matches what the GitHub widget
uses; summing the four public spoke values understates the denominator by
excluding private contributions (see automation-scripts#51 for the bug
this corrected, and AssemblyZero runbook 0937 for the canonical math).

Numerator: scraped from the activity-overview widget's data-percentages
attribute (`Code review` field) when available. The GraphQL
totalPullRequestReviewContributions field empirically counts only a subset
of reviews (approves on closed PRs); the widget counts every review
submission including COMMENTED on open PRs, which is what GitHub's
displayed graph spoke reflects. See automation-scripts#60.

Stdlib + gh CLI only. Mirrors gh_daily_contributions.py.

Invocation: `gh gh-reviews` (operator-local `gh` CLI alias). The alias
name carries the `gh-` prefix to match the existing `gh-count` pattern;
the visible invocation is therefore `gh gh-reviews`. See
AssemblyZero/docs/runbooks/0936-gh-cli-aliases.md for the alias inventory
and 0937-gh-cli-scripts.md for the script-side pattern + math.

Issues: martymcenroe/automation-scripts#49 (original) + #51 (denominator
fix) + #53 (docstring) + #57 (this streamlined layout + fleet fuel count).
Predecessor: martymcenroe/automation-scripts#42 (operator-filed spec
this tool partially satisfies; remaining scope tracked there)
Parent: martymcenroe/AssemblyZero#1244
Math reference: martymcenroe/AssemblyZero/docs/runbooks/0937-gh-cli-scripts.md
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Chicago")
TIP_FRACTION = 0.005  # rounding boundary that flips the graph spoke from 0% to 1%
WINDOW_DAYS = 365
RECENT_DAYS = 30
TOP_N_FUEL_REPOS = 5

WIDGET_FRAGMENT_URL = (
    "https://github.com/{user}"
    "?action=show&controller=profiles&tab=contributions&user_id={user}"
)

GRAPHQL_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""


def gh_user_login() -> str:
    r = subprocess.run(
        ["gh", "api", "user", "-q", ".login"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def all_time_review_count(username: str) -> int:
    r = subprocess.run(
        ["gh", "api",
         f"search/issues?q=reviewed-by:{username}+type:pr",
         "--jq", ".total_count"],
        capture_output=True, text=True, check=True,
    )
    return int(r.stdout.strip())


def contributions_collection(username: str, frm: datetime, to: datetime) -> dict:
    utc_from = frm.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
    utc_to = to.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = subprocess.run(
        ["gh", "api", "graphql",
         "-f", f"query={GRAPHQL_QUERY}",
         "-F", f"username={username}",
         "-F", f"from={utc_from}",
         "-F", f"to={utc_to}"],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(r.stdout)
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
        sys.exit(1)
    return data["data"]["user"]["contributionsCollection"]


def widget_denominator(c: dict) -> int:
    """Match the GitHub activity-overview widget's denominator.

    Uses contributionCalendar.totalContributions, the all-types
    all-restrictions count over the window. The four-spoke public sum
    (commits + issues + PRs + reviews) is NOT correct -- it excludes
    private contributions and understates the denominator. See
    automation-scripts#51 for the bug this corrected.
    """
    return c["contributionCalendar"]["totalContributions"]


def fetch_widget_percentages(username: str) -> dict | None:
    """Best-effort cross-check: fetch the rendered activity-overview fragment
    and parse the data-percentages attribute. Returns None on any failure;
    cross-check is informational, never fatal.
    """
    url = WIDGET_FRAGMENT_URL.format(user=username)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "text/fragment+html, text/html",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "gh_review_projection/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    m = re.search(r'data-percentages="([^"]+)"', html)
    if not m:
        return None
    raw = m.group(1).replace("&quot;", '"')
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def todays_shipped(username: str) -> int:
    """Count dependabot PRs merged today (US Central) across user-owned repos."""
    today_central = datetime.now(TZ).strftime("%Y-%m-%d")
    try:
        r = subprocess.run(
            ["gh", "search", "prs",
             "--author", "app/dependabot",
             "--owner", username,
             "--merged",
             "--closed", f">={today_central}",
             "--limit", "200",
             "--json", "number",
             "--jq", "length"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        return int(r.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        return 0


def fleet_open_dependabot_prs(username: str) -> tuple[int, Counter]:
    """Count open dependabot PRs across all user-owned repos.

    Single search call returns all PRs; group by repo for top-N reporting.
    Returns (total_count, Counter[repo_name -> count]).

    Note: search/issues q-param uses `+` between tokens, not spaces. gh's
    URL handling is inconsistent enough that pre-encoding here is safer.
    """
    q = f"is:pr+is:open+user:{username}+author:app/dependabot"
    try:
        r = subprocess.run(
            ["gh", "api", "--paginate",
             f"search/issues?q={q}&per_page=100",
             "--jq", ".items[] | .repository_url"],
            capture_output=True, text=True, check=True, timeout=30,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return 0, Counter()
    repos = Counter()
    for line in r.stdout.strip().splitlines():
        if not line:
            continue
        # repository_url is like https://api.github.com/repos/{user}/{repo}
        repo = line.rstrip("/").split("/")[-1]
        repos[repo] += 1
    return sum(repos.values()), repos


def _hr(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def _print_full_breakdown(c: dict, denom_label: str) -> None:
    total = widget_denominator(c)
    restricted = c["restrictedContributionsCount"]
    reviews = c["totalPullRequestReviewContributions"]
    pct = 100 * reviews / total if total else 0
    print(f"  commits:       {c['totalCommitContributions']:>5}  (public)")
    print(f"  issues:        {c['totalIssueContributions']:>5}  (public)")
    print(f"  pull requests: {c['totalPullRequestContributions']:>5}  (public)")
    print(f"  code review:   {reviews:>5}  ({pct:.2f}% of {denom_label} -- "
          f"API approves-only lower bound; widget counts more)")
    print(f"  private:       {restricted:>5}  (restricted, no type breakdown via API)")
    print(f"  TOTAL:         {total:>5}  (widget denominator)")


def main(verbose: bool = False) -> int:
    username = gh_user_login()
    now = datetime.now(TZ)
    year_start = now - timedelta(days=WINDOW_DAYS)
    recent_start = now - timedelta(days=RECENT_DAYS)

    y = contributions_collection(username, year_start, now)
    Y_total = widget_denominator(y)
    Y_reviews_api = y["totalPullRequestReviewContributions"]

    m = contributions_collection(username, recent_start, now)
    m_total = widget_denominator(m)
    m_reviews_api = m["totalPullRequestReviewContributions"]

    widget = fetch_widget_percentages(username)
    widget_pct = widget.get("Code review") if widget else None

    if widget_pct is not None and Y_total:
        Y_reviews_effective = widget_pct / 100 * Y_total
        displayed = widget_pct
        widget_source = "live activity-overview widget"
    elif Y_total:
        api_ratio = 100 * Y_reviews_api / Y_total
        displayed = round(api_ratio)
        Y_reviews_effective = Y_reviews_api
        widget_source = "API fallback (widget fetch failed)"
    else:
        print(f"GitHub review-projection for @{username} ({now.date().isoformat()} Central)")
        print("No 12-month contributions yet — cannot project.")
        return 0

    threshold_met = displayed >= 1
    threshold_pct = 100 * TIP_FRACTION
    widget_scale = (Y_reviews_effective / Y_reviews_api
                    if Y_reviews_api > 0 and Y_reviews_effective > Y_reviews_api else 1.0)

    shipped_today = todays_shipped(username)
    fuel_total, fuel_by_repo = fleet_open_dependabot_prs(username)

    print(f"GitHub review-projection for @{username} ({now.date().isoformat()} Central)")
    print()

    state_tag = (f"above {threshold_pct:.2f}% threshold" if threshold_met
                 else f"below {threshold_pct:.2f}% threshold")
    print(f"TODAY      {shipped_today} merged | ratio {displayed}% ({state_tag})")

    top = fuel_by_repo.most_common(3)
    top_str = ", ".join(f"{repo} {count}" for repo, count in top)
    more = max(0, len(fuel_by_repo) - 3)
    tail = f", +{more} more" if more > 0 else ""
    detail = f" ({top_str}{tail})" if top else ""
    print(f"BACKLOG    {fuel_total} open dependabot PRs{detail}")

    if threshold_met:
        print(f"ACTION     Optional drain (banks events for tomorrow)")
    else:
        print(f"ACTION     DRAIN NOW to flip ratio")
    print(f"           -> Start-ScheduledTask -TaskName 'Claude-DependabotFleet'")

    if verbose:
        _hr("DETAIL")
        print(f"  Ratio source: {widget_source}")
        print(f"  Year ({WINDOW_DAYS}d):  {Y_reviews_api} API approves, "
              f"~{int(Y_reviews_effective)} widget-implied of {Y_total:,} total = {displayed}%")
        if m_total:
            m_scaled = m_reviews_api * widget_scale
            m_ratio_scaled = 100 * m_scaled / m_total
            print(f"  30d window:    {m_reviews_api} API approves, "
                  f"~{int(m_scaled)} scaled of {m_total:,} = {m_ratio_scaled:.2f}%")
        print(f"  Widget/API:    {widget_scale:.2f}x (API approves-only; widget counts comments)")
        print(f"  All-time:      {all_time_review_count(username)} unique PRs reviewed")
        print()
        print("  Backlog by repo:")
        for repo, count in fuel_by_repo.most_common(TOP_N_FUEL_REPOS):
            print(f"    {repo:<35} {count}")
        if len(fuel_by_repo) > TOP_N_FUEL_REPOS:
            print(f"    ... +{len(fuel_by_repo) - TOP_N_FUEL_REPOS} more repos")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="show all-time count, full per-window contribution breakdowns, and widget cross-check",
    )
    args = parser.parse_args()
    sys.exit(main(verbose=args.verbose))
