from pathlib import Path
import trafilatura
from weasyprint import HTML

URLS_FILE = Path("urls.txt")
OUTPUT_DIR = Path("saved_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

def make_safe_filename(index, url):
    # Short, simple filenames: 01.pdf, 02.pdf, ...
    return f"{index:02d}.pdf"

def main():
    if not URLS_FILE.exists():
        raise SystemExit(f"{URLS_FILE} not found. Run the bookmarks extraction script first.")

    urls = [line.strip() for line in URLS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Processing {len(urls)} URLs...")

    for idx, url in enumerate(urls, start=1):
        print(f"[{idx}/{len(urls)}] Fetching {url}")
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            print(f"  ! Skipping (download failed)")
            continue

        # Extract main content as HTML
        html_content = trafilatura.extract(
            downloaded,
            output_format="html",
            include_comments=False,
            favor_precision=True,
        )

        if not html_content:
            print(f"  ! Skipping (no main content extracted)")
            continue

        pdf_name = make_safe_filename(idx, url)
        pdf_path = OUTPUT_DIR / pdf_name

        # Convert simplified HTML to PDF
        HTML(string=html_content, base_url=url).write_pdf(str(pdf_path))
        print(f"  ✓ Saved {pdf_path}")

    print("Done.")

if __name__ == "__main__":
    main()
