# Runbook: add_sponsorship.py

## Description
Automates the addition of GitHub Sponsorship to a repository. It creates the `.github/FUNDING.yml` file, sets up a feature branch, commits, pushes, and creates/auto-merges a PR to enable the Sponsor button.

## Prerequisites
- **GitHub CLI (gh):** Must be installed and authenticated.
- **Git:** Must be installed.
- **Python 3.x:** Must be installed.

## Usage
1. Navigate to the root of the target repository where you want to add sponsorship.
2. Run the script:
   ```bash
   python ~/Projects/automation-scripts/add_sponsorship.py
   ```

## Workflow
- Checks for existing `.github/FUNDING.yml`.
- Creates a new branch `add-sponsorship`.
- Generates the funding configuration.
- Pushes and creates a PR via `gh`.
- Attempts to auto-merge the PR.
