# Automation Scripts

Collection of utility scripts for personal workflow automation, gaming analysis, and development operations.

This repository uses Poetry for dependency management. After cloning, run `poetry install` once, then invoke scripts with `poetry run python ...` so they run inside the project virtual environment.


## Repository Management

### add_sponsorship.py
Automates the addition of GitHub Sponsorship to any repository. Creates the .github/FUNDING.yml file, creates a feature branch, commits, pushes, and auto-merges a PR to enable the Sponsor button.

**Usage:**
```bash
# Run from the root of the target repository
python ~/Projects/automation-scripts/add_sponsorship.py
```

**Requirements:** GitHub CLI (gh), git, Python 3.x

### toggle_visibility.py
Bulk toggles the visibility (public/private) of repositories. Wraps the GitHub CLI to safely modify single repos or lists of repos, with a safety confirmation prompt. Useful for rapidly curating your public profile.

**Usage:**
```bash
# Make repos private
python toggle_visibility.py repo1 repo2 --private

# Make repos public
python toggle_visibility.py repo1 --public
```

**Requirements:** GitHub CLI (gh), Python 3.x

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

### toggle_visibility.py
Bulk toggles the visibility (public/private) of repositories. Wraps the GitHub CLI to safely modify single repos or lists of repos, with a safety confirmation prompt. Useful for rapidly curating your public profile.

**Usage:**
```bash
# Make repos private
python toggle_visibility.py repo1 repo2 --private

# Make repos public
python toggle_visibility.py repo1 --public
```

**Requirements:** GitHub CLI (gh), Python 3.x

---

### git_sync_audit.sh
A comprehensive dashboard for syncing Git repositories across the machine. Audits `~/dotfiles` and all repositories in `~/Projects`, providing a "Traffic Light" status report (Clean, Dirty, Ahead, Diverged). Auto-fast-forwards clean repos and skips dirty ones to prevent data loss.

**Usage:**
```bash
./git_sync_audit.sh
```

**Requirements:** Bash, git


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

## Web Archiving

### extract_urls_from_brave.py
Extracts all URLs from a specific Brave bookmarks folder. Reads a copied Brave `Bookmarks` JSON file, searches for the named folder, and writes one URL per line to `local/brave/urls.txt`. Intended as the first step in a bookmarks-to-PDF pipeline.

**Usage:**
```bash
# From the repo root, after copying your Brave Bookmarks file to local/brave/Bookmarks
python extract_urls_from_brave.py
```

**Notes:**
- Edit the `TARGET_FOLDER_NAME` constant in the script to match the name of your Brave bookmarks folder.
- Output is written to `local/brave/urls.txt`.

**Requirements:** Python 3.x

### save_urls_as_clean_pdfs.py
Converts each URL in `local/brave/urls.txt` into a simplified, reader-mode PDF. Fetches each page, extracts the main article content, and writes PDFs to `local/brave/pdfs/`. Designed to archive the substantive content of saved pages without ads or navigation chrome.

**Usage:**
```bash
# From the repo root, after running extract_urls_from_brave.py
python save_urls_as_clean_pdfs.py
```

**Output:**
- Simplified PDFs saved under `local/brave/pdfs/`.

**Requirements:** Python 3.x, `trafilatura`, `weasyprint`

---

## Development Status

Scripts marked with `*` are executable. Some tools are in active development with additional features planned.

## License

All scripts in this repository are licensed under the PolyForm Noncommercial 1.0.0. See LICENSE file for details.
