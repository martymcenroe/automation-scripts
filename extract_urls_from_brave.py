import json
from pathlib import Path

# 1) EDIT THESE TWO LINES
BOOKMARKS_PATH = Path("local/brave/Bookmarks")  # or macOS path
TARGET_FOLDER_NAME = "OReilly playlists"  # exactly as it appears in Brave

def find_folder(node, name):
    """Depth-first search for a folder by name."""
    if isinstance(node, dict):
        if node.get("type") == "folder" and node.get("name") == name:
            return node
        for child in node.get("children", []):
            found = find_folder(child, name)
            if found:
                return found
    return None

def collect_urls(node, urls):
    """Collect all URL entries inside this folder (recursively)."""
    if not isinstance(node, dict):
        return
    if node.get("type") == "url":
        url = node.get("url")
        if url:
            urls.append(url)
    for child in node.get("children", []):
        collect_urls(child, urls)

def main():
    data = json.loads(BOOKMARKS_PATH.read_text(encoding="utf-8"))
    roots = data.get("roots", {})

    target_folder = None
    for root in roots.values():
        if isinstance(root, dict):
            target_folder = find_folder(root, TARGET_FOLDER_NAME) or target_folder

    if target_folder is None:
        raise SystemExit(f"Folder '{TARGET_FOLDER_NAME}' not found in bookmarks JSON")

    urls = []
    collect_urls(target_folder, urls)

    if not urls:
        raise SystemExit("No URLs found in that folder")

    out_path = Path("urls.txt")
    out_path.write_text("\n".join(urls), encoding="utf-8")
    print(f"Wrote {len(urls)} URLs to {out_path.resolve()}")

if __name__ == "__main__":
    main()
