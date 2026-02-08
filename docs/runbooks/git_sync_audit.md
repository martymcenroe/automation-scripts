# Runbook: git_sync_audit.sh

## Description
A dashboard for syncing Git repositories across the machine. It audits `~/dotfiles` and repositories in `~/Projects`, reporting their status (Clean, Dirty, Ahead, Diverged) and auto-syncing clean ones.

## Prerequisites
- **Bash:** Must be installed (WSL or Linux).
- **Git:** Must be installed.

## Usage
Run the script from its location:
```bash
./git_sync_audit.sh
```

## Status Meanings
- **Clean:** Repository is in sync with remote.
- **Dirty:** Uncommitted changes present.
- **Ahead:** Local commits not yet pushed to remote.
- **Diverged:** Both local and remote have unique commits.

## Workflow
- Fast-forwards repositories that are "Clean" (behind remote).
- Skips "Dirty" or "Diverged" repositories to avoid merge conflicts or data loss.
