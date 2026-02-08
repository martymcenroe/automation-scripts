# Runbook: license_audit.py

## Description
Scans all non-forked repositories in the `~/Projects` directory for missing `LICENSE` files. For each identified repository, it creates a PR to add the MIT LICENSE.

## Prerequisites
- **GitHub CLI (gh):** Must be installed and authenticated.
- **Git:** Must be installed.
- **Python 3.x:** Must be installed.

## Usage
### Dry Run (Preview Changes)
```bash
python license_audit.py --dry-run
```

### Execute (Create PRs)
```bash
python license_audit.py
```

## Workflow
- Iterates through directories in `~/Projects`.
- Checks if a `LICENSE` or `LICENSE.md` file exists.
- Creates a feature branch.
- Adds MIT LICENSE file.
- Commits, pushes, and creates a PR with auto-merge enabled.
