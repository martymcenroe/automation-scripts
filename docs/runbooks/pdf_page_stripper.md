# Runbook: pdf_page_stripper

## Description
Extracts pages from PDF documents. Specifically, it removes the 7th page from every PDF in a source directory.

## Prerequisites
- **Python 3.x:** Must be installed.
- **PyPDF2 Library:** Must be installed (`pip install PyPDF2`).

## Usage
1. Place source PDFs in `~/programming/original_pdfs`.
2. Run the script:
   ```bash
   python tools/pdf_page_stripper
   ```
3. Modified PDFs will be saved in `~/programming/original_pdfs/modified_pdfs`.

## Logic
- Scans for `.pdf` files in the input folder.
- If a file has 7 or more pages, it creates a new version excluding the 7th page (index 6).
- Skips files with fewer than 7 pages.
