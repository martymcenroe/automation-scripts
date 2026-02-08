# Runbook: get_battle_star_collection

## Description
Automates the downloading of Star Battle puzzle PDFs from krazydad.com. It specifically targets the R2 10x10 series.

## Prerequisites
- **Python 3.x:** Must be installed.
- **Requests Library:** Must be installed (`pip install requests`).

## Usage
1. Execute the script:
   ```bash
   python get_battle_star_collection
   ```
2. The PDFs will be downloaded into a local folder named `star_battle_pdfs`.

## Notes
- The script is currently configured to download puzzles in the range 54 to 100.
- Output directory: `star_battle_pdfs/`
