"""GitHub code-review projection.

Reports current state of the operator's code-review fraction (the spoke on the
GitHub profile activity-overview graph) and projects when the 12-month review
percentage will cross the 0.5% rounding boundary that flips the displayed
spoke from 0% to 1%.

Outputs:
1. All-time review count (search/issues, no time bound).
2. Trailing-12-month contribution breakdown (matches the profile graph window).
3. Last-30-day contribution rate (current pace).
4. Projection to the 1%-spoke threshold under two models:
   - Steady-state: if last-30-day pace is sustained, eventual 12-month
     fraction = last_30d_reviews / last_30d_total.
   - Optimistic: days until (R + r*d) / (T + t*d) crosses 0.5%, treating
     the window as additive (ignoring sliding-window falloff).

Stdlib + gh CLI only. Mirrors gh_daily_contributions.py.

Issue: martymcenroe/automation-scripts#49
Parent: martymcenroe/AssemblyZero#1244
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Chicago")
TIP_FRACTION = 0.005  # rounding boundary that flips the graph spoke from 0% to 1%
WINDOW_DAYS = 365
RECENT_DAYS = 30

GRAPHQL_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
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


def graph_total(c: dict) -> int:
    # The activity-overview graph normalizes across these four spokes only;
    # repositories are reported by the API but not shown on the graph.
    return (c["totalCommitContributions"]
            + c["totalIssueContributions"]
            + c["totalPullRequestContributions"]
            + c["totalPullRequestReviewContributions"])


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
    total = graph_total(c)
    reviews = c["totalPullRequestReviewContributions"]
    pct = 100 * reviews / total if total else 0
    print(f"  commits:       {c['totalCommitContributions']:>5}")
    print(f"  issues:        {c['totalIssueContributions']:>5}")
    print(f"  pull requests: {c['totalPullRequestContributions']:>5}")
    print(f"  code review:   {reviews:>5}  ({pct:.2f}% of {denom_label})")
    print(f"  total:         {total:>5}")


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
    Y_total = graph_total(y)
    Y_reviews = y["totalPullRequestReviewContributions"]
    _print_breakdown(y, "12mo")
    if Y_total:
        graph_display = round(100 * Y_reviews / Y_total)
        print(f"  graph displays code review at: {graph_display}%")

    _section(f"3. LAST {RECENT_DAYS} DAYS  (current pace)")
    m = contributions_collection(username, recent_start, now)
    m_total = graph_total(m)
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
