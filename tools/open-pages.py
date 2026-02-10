#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
import os
import time
import urllib.request
from pathlib import Path

def find_urls(file_path):
    """Extracts URLs starting with http or https from a file."""
    url_pattern = re.compile(r"https?://[^\s()<>]+[^\s()<>.,:;?!\"'\s]")
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                urls.extend(url_pattern.findall(line))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    return urls

def check_validity(urls):
    """Checks each URL for 200 OK responses."""
    print(f"Checking validity of {len(urls)} URLs...")
    invalid_urls = []
    for url in urls:
        try:
            # We use a User-Agent to avoid being blocked by sites that reject basic scripts
            req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    invalid_urls.append((url, f"Status {response.status}"))
        except urllib.error.HTTPError as e:
            invalid_urls.append((url, f"HTTP Error {e.code}"))
        except Exception as e:
            # Connection errors, timeouts, etc.
            invalid_urls.append((url, f"Error: {type(e).__name__}"))
    
    if invalid_urls:
        print("\nIssues Found (Non-200 Responses):")
        for url, reason in invalid_urls:
            print(f"  [FAIL] {reason}: {url}")
    else:
        print("\nAll URLs returned a successful 200 OK response.")

def open_in_firefox(urls):
    """Opens a list of URLs in a new Firefox window."""
    if not urls:
        print("No URLs found in the specified file.")
        return

    # Standard Firefox paths on Windows
    firefox_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
    ]
    
    firefox_cmd = "firefox" # Default if in PATH
    for path in firefox_paths:
        if os.path.exists(path):
            firefox_cmd = path
            break

    try:
        print(f"Opening {urls[0]} in a new window...")
        subprocess.Popen([firefox_cmd, "-new-window", urls[0]])
        
        # Pause to allow the new window to initialize before adding tabs
        time.sleep(3) 

        # Open subsequent URLs in new tabs
        for url in urls[1:]:
            subprocess.Popen([firefox_cmd, "-new-tab", url])
        print(f"Successfully sent {len(urls)} URLs to Firefox.")
    except Exception as e:
        print(f"Error launching Firefox: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Extracts URLs from a Markdown file and opens them in Firefox (max 50 tabs)."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input Markdown file (relative, absolute, or ~/path)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List discovered URLs without opening them."
    )
    parser.add_argument(
        "--valid",
        action="store_true",
        help="Check URLs for 404 Not Found errors without opening them."
    )

    args = parser.parse_args()

    # Handle path expansion (~ and absolute/relative)
    input_path = Path(os.path.expanduser(args.input)).resolve()

    if not input_path.is_file():
        print(f"Error: File not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    urls = find_urls(input_path)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = [x for x in urls if not (x in seen or seen.add(x))]
    
    total_found = len(unique_urls)
    
    if args.dry_run:
        print(f"Dry Run: Found {total_found} unique URLs:")
        for url in unique_urls:
            print(f"  {url}")
        return

    if args.valid:
        check_validity(unique_urls)
        return

    if total_found > 50:
        print(f"Warning: Found {total_found} unique URLs.")
        confirm = input(f"Do you want to open the first 50 tabs? (y/n): ").strip().lower()
        if confirm == 'y':
            open_in_firefox(unique_urls[:50])
        else:
            print("Operation cancelled.")
    else:
        open_in_firefox(unique_urls)

if __name__ == "__main__":
    main()
