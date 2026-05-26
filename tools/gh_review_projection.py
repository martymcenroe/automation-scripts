"""GitHub code-review projection -- "how close am I to the 1% graph spoke."

Reports the actionable wedge math:
  - Where you are: 12mo review ratio vs the 0.5% rounding threshold
  - What it takes TODAY: reviews-to-add to flip the displayed %, plus the
    available fuel (open dependabot PRs across the fleet waiting to be reviewed)
  - Will it stick: 30d pace check
  - Do-nothing projection: days to cross at current organic pace

Default output is ~15 lines. `--verbose` re-enables the full contribution
breakdowns, all-time review count, and widget cross-check block (useful for
debugging the math but noisy for daily operational use).

Denominator: contributionCalendar.totalContributions -- the all-types,
all-restrictions count over the window. This matches what the GitHub widget
uses; summing the four public spoke values understates the denominator by
excluding private contributions (see automation-scripts#51 for the bug
this corrected, and AssemblyZero runbook 0937 for the canonical math).

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


def reviews_to_flip(reviews: int, total: int) -> int:
    """Min R such that (reviews + R) / (total + R) >= TIP_FRACTION.

    Algebra: R * (1 - TIP) >= TIP*total - reviews
    Returns 0 if already at/above threshold.
    """
    if total == 0:
        return 0
    needed = TIP_FRACTION * total - reviews
    if needed <= 0:
        return 0
    r = needed / (1 - TIP_FRACTION)
    # Ceiling: any fractional R means we need the next whole review
    return int(r) + (0 if r == int(r) else 1)


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


def project_optimistic_days(R: int, T: int, r: float, t: float) -> int | None:
    # Solve smallest d such that (R + r*d) / (T + t*d) >= TIP_FRACTION.
    # → d * (r - TIP*t) >= TIP*T - R
    numer = TIP_FRACTION * T - R
    if numer <= 0:
        return 0
    denom = r - TIP_FRACTION * t
    if denom <= 0:
        return None
    return int(numer / denom) + 1


def fmt_days(days: int | None) -> str:
    if days is None:
        return "never (rate too low to overcome dilution)"
    if days == 0:
        return "already at or above threshold"
    target = (datetime.now(TZ) + timedelta(days=days)).date()
    return f"~{days} days (around {target.isoformat()})"


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
          f"includes any private reviews)")
    print(f"  private:       {restricted:>5}  (restricted, no type breakdown via API)")
    print(f"  TOTAL:         {total:>5}  (widget denominator)")


def main(verbose: bool = False) -> int:
    username = gh_user_login()
    now = datetime.now(TZ)
    year_start = now - timedelta(days=WINDOW_DAYS)
    recent_start = now - timedelta(days=RECENT_DAYS)

    y = contributions_collection(username, year_start, now)
    Y_total = widget_denominator(y)
    Y_reviews = y["totalPullRequestReviewContributions"]

    m = contributions_collection(username, recent_start, now)
    m_total = widget_denominator(m)
    m_reviews = m["totalPullRequestReviewContributions"]

    print(f"GitHub review-projection for @{username}  ({now.date().isoformat()})")

    _hr("WHERE YOU ARE")
    if Y_total:
        ratio = 100 * Y_reviews / Y_total
        displayed = round(ratio)
        print(f"  12-month ratio:  {Y_reviews} reviews / {Y_total:,} total = {ratio:.2f}%  ->  graph: {displayed}%")
        widget = fetch_widget_percentages(username) if verbose else None
        if verbose and widget is not None:
            actual = widget.get("Code review")
            tag = "match" if actual == displayed else f"DRIFT (widget shows {actual}%)"
            print(f"  widget cross-check: {actual}%  ({tag})")
    else:
        print("  No 12-month contributions yet -- cannot project.")
        return 0
    print(f"  Threshold:       >= {100*TIP_FRACTION:.2f}% to display 1%")

    _hr("WHAT IT TAKES TODAY")
    r_needed = reviews_to_flip(Y_reviews, Y_total)
    if r_needed == 0:
        print(f"  Already at/above threshold ({ratio:.2f}%). Nothing required today.")
    else:
        print(f"  Reviews to add:  {r_needed}   (instantly flips the displayed % from 0 to 1)")
    fuel_total, fuel_by_repo = fleet_open_dependabot_prs(username)
    print(f"  Fuel available:  {fuel_total} open dependabot PRs across {len(fuel_by_repo)} repos")
    if fuel_total:
        for repo, count in fuel_by_repo.most_common(TOP_N_FUEL_REPOS):
            print(f"                   {repo:<35} {count}")
        if len(fuel_by_repo) > TOP_N_FUEL_REPOS:
            print(f"                   ... +{len(fuel_by_repo) - TOP_N_FUEL_REPOS} more repos")
    print("  Harvest path:    Start-ScheduledTask Claude-DependabotFleet  (or manual review)")

    _hr("WILL IT STICK")
    if m_total:
        m_ratio = 100 * m_reviews / m_total
        print(f"  Last-{RECENT_DAYS}d pace:   {m_reviews} reviews / {m_total:,} total = {m_ratio:.2f}%")
        threshold_pct = 100 * TIP_FRACTION
        if m_ratio >= threshold_pct:
            print(f"  Verdict:         YES -- sustained above {threshold_pct:.2f}% at current pace")
        else:
            gap = threshold_pct - m_ratio
            print(f"  Verdict:         NO -- short by {gap:.2f}pp; flip will decay back below threshold")
    else:
        print(f"  No activity in last {RECENT_DAYS} days; cannot assess pace.")

    _hr("DO-NOTHING PROJECTION")
    r_per_day = m_reviews / RECENT_DAYS
    t_per_day = m_total / RECENT_DAYS
    days = project_optimistic_days(Y_reviews, Y_total, r_per_day, t_per_day)
    print(f"  At current {r_per_day:.2f} reviews/day pace: cross threshold {fmt_days(days)}")
    print(f"  (Optimistic model -- ignores {WINDOW_DAYS}-day sliding-window falloff.)")

    if verbose:
        _hr("VERBOSE: ALL-TIME + PER-WINDOW BREAKDOWN")
        print(f"  all-time reviews:  {all_time_review_count(username)} unique PRs reviewed")
        print()
        print(f"  Trailing {WINDOW_DAYS} days:")
        _print_full_breakdown(y, "12mo")
        print()
        print(f"  Last {RECENT_DAYS} days:")
        _print_full_breakdown(m, f"{RECENT_DAYS}d")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="show all-time count, full per-window contribution breakdowns, and widget cross-check",
    )
    args = parser.parse_args()
    sys.exit(main(verbose=args.verbose))
