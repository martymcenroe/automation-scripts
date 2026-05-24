"""GitHub code-review projection.

Reports current state of the operator's code-review fraction (the spoke on the
GitHub profile activity-overview graph) and projects when the 12-month review
percentage will cross the 0.5% rounding boundary that flips the displayed
spoke from 0% to 1%.

Outputs:
1. All-time review count (search/issues, no time bound).
2. Trailing-12-month contribution breakdown -- matches the profile graph window.
   Includes a cross-check against the widget's actual rendered data-percentages
   so drift between this tool's math and GitHub's displayed value is visible.
3. Last-30-day contribution rate (current pace).
4. Projection to the 1%-spoke threshold under two models:
   - Steady-state: if last-30-day pace is sustained, eventual 12-month
     fraction = last_30d_reviews / last_30d_total.
   - Optimistic: days until (R + r*d) / (T + t*d) crosses 0.5%, treating
     the window as additive (ignoring sliding-window falloff).

Denominator: contributionCalendar.totalContributions -- the all-types,
all-restrictions count over the window. This matches what the GitHub widget
uses; summing the four public spoke values understates the denominator by
excluding private contributions (see automation-scripts#51 for the bug
this corrected, and AssemblyZero runbook 0937 for the canonical math).

Stdlib + gh CLI only. Mirrors gh_daily_contributions.py.

Issues: martymcenroe/automation-scripts#49 (original) + #51 (denominator fix)
Parent: martymcenroe/AssemblyZero#1244
Math reference: martymcenroe/AssemblyZero/docs/runbooks/0937-gh-cli-scripts.md
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Chicago")
TIP_FRACTION = 0.005  # rounding boundary that flips the graph spoke from 0% to 1%
WINDOW_DAYS = 365
RECENT_DAYS = 30

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


def _section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def _print_breakdown(c: dict, denom_label: str) -> None:
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


def main() -> int:
    username = gh_user_login()
    now = datetime.now(TZ)
    year_start = now - timedelta(days=WINDOW_DAYS)
    recent_start = now - timedelta(days=RECENT_DAYS)

    print(f"GitHub review-projection for @{username}  (as of {now.date().isoformat()})")

    _section("1. ALL-TIME REVIEW COUNT")
    print(f"  {all_time_review_count(username)}  unique PRs reviewed (no time bound)")

    _section(f"2. TRAILING {WINDOW_DAYS} DAYS  (matches profile activity-overview graph)")
    y = contributions_collection(username, year_start, now)
    Y_total = widget_denominator(y)
    Y_reviews = y["totalPullRequestReviewContributions"]
    _print_breakdown(y, "12mo")
    if Y_total:
        computed = round(100 * Y_reviews / Y_total)
        print(f"  computed code-review %:        {computed}%")
        widget = fetch_widget_percentages(username)
        if widget is not None:
            actual = widget.get("Code review")
            label = "match" if actual == computed else f"DRIFT (widget {actual}%)"
            print(f"  widget displays:               {actual}%  ({label})")
        else:
            print("  widget cross-check unavailable (HTML fetch failed)")

    _section(f"3. LAST {RECENT_DAYS} DAYS  (current pace)")
    m = contributions_collection(username, recent_start, now)
    m_total = widget_denominator(m)
    m_reviews = m["totalPullRequestReviewContributions"]
    _print_breakdown(m, f"{RECENT_DAYS}d")

    _section("4. PROJECTION TO 1% GRAPH SPOKE  (threshold: cumulative fraction >= 0.5%)")
    if Y_total == 0:
        print("  No 12-month contributions yet -- cannot project.")
        return 0

    current_pct = 100 * Y_reviews / Y_total
    if current_pct >= 100 * TIP_FRACTION:
        print(f"  Already at threshold -- 12-month review fraction is {current_pct:.2f}%.")
        return 0

    r_per_day = m_reviews / RECENT_DAYS
    t_per_day = m_total / RECENT_DAYS
    print(f"  Last-{RECENT_DAYS}-day review rate: {r_per_day:.2f}/day")
    print(f"  Last-{RECENT_DAYS}-day total rate:  {t_per_day:.2f}/day")

    if t_per_day > 0:
        eventual = 100 * r_per_day / t_per_day
        print(f"  Steady-state 12-month fraction at current pace: {eventual:.2f}%")
        if eventual < 100 * TIP_FRACTION:
            gap = 100 * TIP_FRACTION - eventual
            print(f"  Current pace WILL NOT tip the spoke "
                  f"(short by {gap:.2f} percentage points).")
            print("  Either increase review velocity or decrease other contribution rate.")
        else:
            print("  Current pace WILL tip the spoke if sustained.")

    days = project_optimistic_days(Y_reviews, Y_total, r_per_day, t_per_day)
    print(f"  Optimistic days to threshold (no falloff): {fmt_days(days)}")
    print(f"  Caveat: optimistic model ignores the {WINDOW_DAYS}-day sliding-window")
    print("  falloff. Real date depends on the historical distribution.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
