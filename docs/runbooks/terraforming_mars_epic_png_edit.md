# Runbook: terraforming_mars_epic_png_edit

## Description
Image processing utility for Terraforming Mars game components. It adds a 50-pixel border to all PNG images in a directory, which is useful for preparing custom cards or components.

## Prerequisites
- **Python 3.x:** Must be installed.
- **Pillow Library:** Must be installed (`pip install Pillow`).

## Usage
1. Ensure your source images are in `~/Mars`.
2. Run the script:
   ```bash
   python terraforming_mars_epic_png_edit
   ```
3. Modified images will be saved to `~/Mars_modified`.

## Logic
- Recursively processes all subdirectories.
- Adds 50 pixels of padding to all four sides of each PNG image.
- Maintains the original image mode.
