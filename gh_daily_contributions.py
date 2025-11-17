"""
Get today's GitHub contribution count using GraphQL API.
Matches the green square contribution logic on GitHub profiles.
"""
import json
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


def get_contributions_today(username: str, timezone: str = "America/Chicago") -> dict:
    """
    Query GitHub GraphQL API for today's contributions.
    
    Args:
        username: GitHub username
        timezone: Timezone string (default: America/Chicago for CST/CDT)
    
    Returns:
        dict with contribution details
    """
    # Get today's date in the specified timezone
    tz = ZoneInfo(timezone)
    today = datetime.now(tz).date()
    from_date = today.isoformat()
    to_date = today.isoformat()
    
    # GraphQL query for contribution calendar
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoryContributions
        }
      }
    }
    """
    
    # Prepare variables - GitHub API expects RFC3339 format with time
    variables = {
        "username": username,
        "from": f"{from_date}T00:00:00Z",
        "to": f"{from_date}T23:59:59Z"
    }
    
    # Execute query using gh CLI
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}", "-F", f"username={username}",
             "-F", f"from={variables['from']}", "-F", f"to={variables['to']}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
            return None
            
        collection = data["data"]["user"]["contributionsCollection"]
        
        # Get today's specific contribution count from calendar
        today_count = 0
        for week in collection["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                if day["date"] == from_date:
                    today_count = day["contributionCount"]
                    break
        
        return {
            "date": from_date,
            "total_contributions": today_count,
            "commits": collection["totalCommitContributions"],
            "issues": collection["totalIssueContributions"],
            "pull_requests": collection["totalPullRequestContributions"],
            "reviews": collection["totalPullRequestReviewContributions"],
            "repositories": collection["totalRepositoryContributions"]
        }
        
    except subprocess.CalledProcessError as e:
        print(f"Error calling gh API: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return None


def main():
    """Main entry point."""
    # Get username from gh CLI
    try:
        result = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True,
            text=True,
            check=True
        )
        username = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not get GitHub username. Is gh CLI authenticated?", file=sys.stderr)
        sys.exit(1)
    
    # Get contributions
    contributions = get_contributions_today(username)
    
    if contributions is None:
        sys.exit(1)
    
    # Output results
    print(f"GitHub Contributions for {contributions['date']}:")
    print(f"Total: {contributions['total_contributions']}")
    print(f"  Commits: {contributions['commits']}")
    print(f"  Issues: {contributions['issues']}")
    print(f"  Pull Requests: {contributions['pull_requests']}")
    print(f"  Reviews: {contributions['reviews']}")
    print(f"  Repositories: {contributions['repositories']}")


if __name__ == "__main__":
    main()