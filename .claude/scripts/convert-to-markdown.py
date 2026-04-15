#!/usr/bin/env python3
"""
Markdown auto-conversion utility.

Converts PDF, DOCX, HTML, TXT, and CSV files to markdown.
Output lands alongside the source file with a .md extension.

Usage:
    python3 convert-to-markdown.py <file>        # single file
    python3 convert-to-markdown.py <directory>    # batch convert all supported files
    python3 convert-to-markdown.py --check        # verify dependencies are installed
"""

import csv
import io
import os
import sys
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = VAULT_DIR / ".claude" / "logs" / "convert-debug.log"

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".html", ".htm", ".txt", ".csv"}

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

DEPENDENCIES = {
    ".pdf": ("pypdf", "pip install pypdf"),
    ".docx": ("docx", "pip install python-docx"),
    ".html": ("bs4", "pip install beautifulsoup4"),
    ".htm": ("bs4", "pip install beautifulsoup4"),
}


def check_dependency(ext: str) -> bool:
    """Check if the required package for a file type is installed."""
    if ext not in DEPENDENCIES:
        return True
    module_name, install_cmd = DEPENDENCIES[ext]
    try:
        __import__(module_name)
        return True
    except ImportError:
        print(f"Missing dependency for {ext} files: {install_cmd}")
        return False


def check_all_dependencies() -> bool:
    """Check all dependencies and report status."""
    all_ok = True
    checked = set()
    for ext, (module_name, install_cmd) in DEPENDENCIES.items():
        if module_name in checked:
            continue
        checked.add(module_name)
        try:
            __import__(module_name)
            print(f"  {module_name}: installed")
        except ImportError:
            print(f"  {module_name}: MISSING -- {install_cmd}")
            all_ok = False
    print(f"  csv: installed (stdlib)")
    return all_ok


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log_debug(msg: str):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Converters
# ---------------------------------------------------------------------------

def convert_pdf(filepath: Path) -> str:
    """Extract text from PDF pages."""
    import pypdf

    reader = pypdf.PdfReader(str(filepath))
    pages = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and text.strip():
            pages.append(f"## Page {i}\n\n{text.strip()}")

    if not pages:
        return "(No extractable text found in PDF)"

    return "\n\n---\n\n".join(pages)


def convert_docx(filepath: Path) -> str:
    """Extract text from DOCX with basic structure."""
    import docx

    doc = docx.Document(str(filepath))
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name.lower() if para.style else ""
        if "heading 1" in style:
            lines.append(f"# {text}")
        elif "heading 2" in style:
            lines.append(f"## {text}")
        elif "heading 3" in style:
            lines.append(f"### {text}")
        elif "list" in style:
            lines.append(f"- {text}")
        else:
            lines.append(text)
        lines.append("")

    return "\n".join(lines).strip() or "(No text found in DOCX)"


def convert_html(filepath: Path) -> str:
    """Extract text from HTML, preserving basic structure."""
    from bs4 import BeautifulSoup

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    lines = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "code"]):
        text = element.get_text(strip=True)
        if not text:
            continue
        tag = element.name
        if tag == "h1":
            lines.append(f"# {text}")
        elif tag == "h2":
            lines.append(f"## {text}")
        elif tag == "h3":
            lines.append(f"### {text}")
        elif tag == "h4":
            lines.append(f"#### {text}")
        elif tag == "li":
            lines.append(f"- {text}")
        elif tag in ("pre", "code"):
            lines.append(f"```\n{text}\n```")
        else:
            lines.append(text)
        lines.append("")

    return "\n".join(lines).strip() or "(No extractable text found in HTML)"


def convert_txt(filepath: Path) -> str:
    """Pass through text files as-is."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def convert_csv(filepath: Path) -> str:
    """Convert CSV to a markdown table."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return "(Empty CSV file)"

    header = rows[0]
    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join("---" for _ in header) + " |")
    for row in rows[1:]:
        # Pad or truncate to match header width
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded[:len(header)]) + " |")

    return "\n".join(lines)


CONVERTERS = {
    ".pdf": convert_pdf,
    ".docx": convert_docx,
    ".html": convert_html,
    ".htm": convert_html,
    ".txt": convert_txt,
    ".csv": convert_csv,
}


# ---------------------------------------------------------------------------
# Main conversion logic
# ---------------------------------------------------------------------------

def convert_file(filepath: Path) -> Path | None:
    """Convert a single file to markdown. Returns output path or None on failure."""
    ext = filepath.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        log_debug(f"Skipping unsupported file type: {filepath} ({ext})")
        return None

    if not check_dependency(ext):
        log_debug(f"Missing dependency for {ext}, skipping: {filepath}")
        return None

    output_path = filepath.with_suffix(".md")

    # Skip if markdown output already exists and is newer than source
    if output_path.exists() and output_path.stat().st_mtime >= filepath.stat().st_mtime:
        log_debug(f"Skipping (up-to-date): {filepath}")
        print(f"  skip (up-to-date): {filepath.name}")
        return output_path

    converter = CONVERTERS.get(ext)
    if not converter:
        log_debug(f"No converter for {ext}")
        return None

    try:
        log_debug(f"Converting: {filepath}")
        content = converter(filepath)

        # Add source metadata header
        header = (
            f"---\n"
            f"source: {filepath.name}\n"
            f"converted: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"type: converted\n"
            f"---\n\n"
            f"# {filepath.stem}\n\n"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content + "\n")

        log_debug(f"Wrote: {output_path} ({len(content)} chars)")
        print(f"  converted: {filepath.name} -> {output_path.name}")
        return output_path

    except Exception as e:
        log_debug(f"Failed to convert {filepath}: {e}")
        print(f"  FAILED: {filepath.name} -- {e}")
        return None


def convert_directory(dirpath: Path) -> list[Path]:
    """Convert all supported files in a directory. Not recursive."""
    results = []
    files = sorted(f for f in dirpath.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS)

    if not files:
        print(f"No supported files found in {dirpath}")
        return results

    print(f"Found {len(files)} file(s) to convert in {dirpath}")
    for filepath in files:
        result = convert_file(filepath)
        if result:
            results.append(result)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 convert-to-markdown.py <file>")
        print("  python3 convert-to-markdown.py <directory>")
        print("  python3 convert-to-markdown.py --check")
        print(f"\nSupported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--check":
        print("Dependency check:")
        ok = check_all_dependencies()
        sys.exit(0 if ok else 1)

    target = Path(arg).resolve()

    if not target.exists():
        print(f"Not found: {target}")
        sys.exit(1)

    if target.is_dir():
        results = convert_directory(target)
        print(f"\nDone: {len(results)} file(s) converted.")
    elif target.is_file():
        result = convert_file(target)
        if result:
            print(f"\nDone: {result}")
        else:
            print("\nNo output produced.")
            sys.exit(1)
    else:
        print(f"Not a file or directory: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
