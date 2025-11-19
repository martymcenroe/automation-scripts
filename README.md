# Automation Scripts

Collection of utility scripts for personal workflow automation, gaming analysis, and development operations.

## Repository Management

# Repository Management


### add_sponsorship.py
Automates the addition of GitHub Sponsorship to any repository. Creates the .github/FUNDING.yml file, creates a feature branch, commits, pushes, and auto-merges a PR to enable the Sponsor button.

**Usage:**
```bash
# Run from the root of the target repository
python ~/Projects/automation-scripts/add_sponsorship.py
```

**Requirements:** GitHub CLI (gh), git, Python 3.x

### license_audit.py
Automated LICENSE file management for GitHub repositories. Scans all non-forked repositories in ~/Projects directory, identifies repos missing a LICENSE file, and automatically creates pull requests to add the MIT LICENSE. The script creates a feature branch, commits the LICENSE file, pushes to remote, creates a PR, auto-merges, and cleans up the branch. Supports `--dry-run` flag to preview changes without execution.

**Usage:**
```bash
# Preview repos that need LICENSE files
python license_audit.py --dry-run

# Execute: create PRs and add LICENSE files
python license_audit.py
```

**Requirements:** GitHub CLI (gh), git, Python 3.x

---

## Gaming & Analysis Tools

### get_battle_star_collection
Board game scoring automation for "2 Star, No Touch" variant tracking. Analyzes game state and calculates achievement progress without manual scorekeeping interference.

### probs_for_cant_stop
Probability calculator and decision support tool for the dice game "Can't Stop". Computes optimal stopping strategies based on current board state.

### terraforming_mars_epic_png_edit
Image processing utility for Terraforming Mars game components. Automates card layout editing and custom component generation.

---

## Media Processing

### convert-to-mp3
Batch audio format converter. Converts various audio formats to MP3 with configurable bitrate and quality settings.

### pdf_page_stripper
PDF manipulation tool for extracting, removing, or reordering pages from PDF documents. Useful for documentation cleanup and report generation.

---

## Development Status

Scripts marked with `*` are executable. Some tools are in active development with additional features planned.

## License

All scripts in this repository are licensed under the MIT License. See LICENSE file for details.
EOF
