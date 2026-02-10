# Runbook: gh_daily_contributions.py

## Description
Fetches the current day's GitHub contribution count using the GraphQL API. It matches the "green square" logic seen on GitHub profiles, providing a breakdown of commits, issues, PRs, and reviews.

## Prerequisites
- **GitHub CLI (gh):** Must be installed and authenticated.
- **Python 3.x:** Must be installed.
- **Timezone Support:** Requires `tzdata` (included in `pyproject.toml`).

## Usage
Run the script:
```bash
python tools/gh_daily_contributions.py
```

## Details
- Queries the `contributionsCollection` via GraphQL.
- Automatically detects the authenticated user via `gh api user`.
- Defaults to `America/Chicago` timezone for calculating day boundaries (can be edited in the script).
- Outputs total count plus specific types (Commits, Issues, PRs, etc.).
