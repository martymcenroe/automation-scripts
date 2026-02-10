# Runbook: toggle_visibility.py

## Description
Bulk toggles the visibility (public/private) of GitHub repositories. It uses the GitHub CLI to modify repository settings with a safety confirmation prompt.

## Prerequisites
- **GitHub CLI (gh):** Must be installed and authenticated.
- **Python 3.x:** Must be installed.

## Usage
### Make repositories private
```bash
python tools/toggle_visibility.py repo1 repo2 --private
```

### Make repositories public
```bash
python tools/toggle_visibility.py repo1 --public
```

## Safety Features
- Prompts for confirmation before making changes.
- Validates repository names before execution.
