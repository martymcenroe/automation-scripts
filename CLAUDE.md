# CLAUDE.md - automation-scripts Project

You are a team member on the automation-scripts project, not a tool.

## Project Identifiers

- **Repository:** `martymcenroe/automation-scripts`
- **Project Root (Windows):** `C:\Users\mcwiz\Projects\automation-scripts`
- **Project Root (Unix):** `/c/Users/mcwiz/Projects/automation-scripts`
- **Worktree Pattern:** `automation-scripts-{IssueID}` (e.g., `automation-scripts-45`)

## Project-Specific Context

**Stack:** Python (Poetry) + `gh` CLI for most scripts. No central entry
point — each script is standalone and invoked individually via
`poetry run python {script}.py [args]`.

**Layout:** unusual for a Python project — this is a **collection of
standalone utility scripts**, not a single package. Two locations:

- `tools/` — newer scripts (e.g., `gh_review_projection.py`)
- repo root — older one-off scripts (e.g., `add_sponsorship.py`,
  `toggle_visibility.py`, `license_audit.py`)

There is **no `src/automation_scripts/` package**. Scripts share the
project's Poetry venv but don't import each other (most are flat scripts
with their own argparse + `if __name__ == "__main__"`).

**Cross-fleet consumers** worth knowing about when editing here:

- `gh_review_projection.py` — referenced from
  `dependabot-honeypot#10` (5%-wedge monitoring) and the 2026-05-25
  AssemblyZero wiki audit
- `add_sponsorship.py`, `toggle_visibility.py`, `license_audit.py` —
  fleet-wide tools the operator runs ad-hoc

**When adding a new script:** put it under `tools/` (the newer pattern).
Don't restructure the existing root scripts into a package — they work
as-is and the layout is intentionally flat.

**Test convention:** `tests/` exists; per-script tests live there as
`tests/test_{script_name}.py` when tests exist. Not every script is
tested — these are personal-automation tools, not a library.
