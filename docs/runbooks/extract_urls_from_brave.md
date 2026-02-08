# Runbook: extract_urls_from_brave.py

## Description
Extracts URLs from a specific Brave bookmarks folder. This is the first step in a bookmarks-to-PDF archiving pipeline.

## Prerequisites
- **Python 3.x:** Must be installed.
- **Brave Browser Bookmarks:** You must manually copy your Brave `Bookmarks` file (JSON) to `local/brave/Bookmarks`.

## Configuration
- Open `extract_urls_from_brave.py`.
- Edit the `TARGET_FOLDER_NAME` constant to match the name of the folder you want to extract from.

## Usage
1. Copy your Brave Bookmarks file:
   ```bash
   cp "C:/Users/<User>/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Bookmarks" local/brave/Bookmarks
   ```
2. Run the script:
   ```bash
   python extract_urls_from_brave.py
   ```
3. Extracted URLs will be written to `local/brave/urls.txt`.
