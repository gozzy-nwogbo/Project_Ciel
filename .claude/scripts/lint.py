#!/usr/bin/env python3
"""
Vault health check / lint process.

Scans the second-brain vault and reports issues in four categories:
  1. Gaps         - under-connected concepts, unextracted daily logs
  2. Stale data   - old knowledge files referencing active projects
  3. Raw-to-wiki  - unprocessed inbox files older than 24 hours
  4. Broken links - [[wiki-links]] pointing to nonexistent files

Outputs a lint-report.md to .claude/logs/ and a summary to stdout.

Usage:
    python3 lint.py           # full report written to file + stdout summary
    python3 lint.py --quick   # stdout summary only, no file written
"""

import argparse
import os
import re
import time
from datetime import datetime

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
KNOWLEDGE_DIR = os.path.join(VAULT_DIR, "02-knowledge")
CONCEPTS_DIR = os.path.join(KNOWLEDGE_DIR, "concepts")
CONNECTIONS_DIR = os.path.join(KNOWLEDGE_DIR, "connections")
DAILY_DIR = os.path.join(VAULT_DIR, "05-daily")
INBOX_RAW = os.path.join(VAULT_DIR, "00-inbox", "raw")
PROJECTS_DIR = os.path.join(VAULT_DIR, "01-projects")
REPORT_PATH = os.path.join(VAULT_DIR, ".claude", "logs", "lint-report.md")

DAY = 86400  # seconds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_frontmatter(filepath: str) -> dict:
    """Read YAML-like frontmatter into a dict (simple key: value parsing)."""
    fm = {}
    try:
        with open(filepath, "r") as f:
            first = f.readline().strip()
            if first != "---":
                return fm
            for line in f:
                line = line.strip()
                if line == "---":
                    break
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
    except Exception:
        pass
    return fm


def _md_files_in(directory: str) -> list[str]:
    """Return absolute paths of all .md files in a directory (non-recursive)."""
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".md")
    )


def _all_md_files(root: str) -> list[str]:
    """Return all .md files under root, recursively."""
    results = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".md"):
                results.append(os.path.join(dirpath, f))
    return sorted(results)


def _slug(filepath: str) -> str:
    """Filename without extension, lowercased."""
    return os.path.splitext(os.path.basename(filepath))[0].lower()


def _active_project_names() -> set[str]:
    """Return folder names of active projects."""
    if not os.path.isdir(PROJECTS_DIR):
        return set()
    return {
        d.lower()
        for d in os.listdir(PROJECTS_DIR)
        if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith(".")
    }


# ---------------------------------------------------------------------------
# 1. Gaps
# ---------------------------------------------------------------------------

def check_gaps(now: float) -> list[dict]:
    findings = []

    # Concepts with fewer than 2 connections
    concept_slugs = {_slug(p) for p in _md_files_in(CONCEPTS_DIR)}
    connection_files = _md_files_in(CONNECTIONS_DIR)

    # Count how many connections reference each concept
    concept_refs: dict[str, int] = {s: 0 for s in concept_slugs}
    for cpath in connection_files:
        fm = _read_frontmatter(cpath)
        content = ""
        try:
            with open(cpath, "r") as f:
                content = f.read().lower()
        except Exception:
            pass
        for slug in concept_slugs:
            from_val = fm.get("from", "").lower()
            to_val = fm.get("to", "").lower()
            if slug in from_val or slug in to_val or slug in content:
                concept_refs[slug] += 1

    for slug, count in sorted(concept_refs.items()):
        if count < 2:
            findings.append({
                "category": "gaps",
                "severity": "warning",
                "message": f"Concept '{slug}' has only {count} connection(s) (minimum: 2)",
                "action": f"Add connections linking '{slug}' to related concepts or projects",
            })

    # Daily logs older than 7 days with no concepts extracted
    seven_days_ago = now - (7 * DAY)
    flush_marker = "flush_processed: true"
    for dpath in _md_files_in(DAILY_DIR):
        mtime = os.path.getmtime(dpath)
        if mtime > seven_days_ago:
            continue
        try:
            with open(dpath, "r") as f:
                head = f.read(500)
        except Exception:
            continue
        if flush_marker not in head:
            fname = os.path.basename(dpath)
            findings.append({
                "category": "gaps",
                "severity": "warning",
                "message": f"Daily log '{fname}' is older than 7 days and was never flushed",
                "action": f"Run flush.py to extract concepts from '{fname}'",
            })

    return findings


# ---------------------------------------------------------------------------
# 2. Stale data
# ---------------------------------------------------------------------------

def check_stale(now: float) -> list[dict]:
    findings = []
    thirty_days_ago = now - (30 * DAY)
    active_projects = _active_project_names()

    for directory in [CONCEPTS_DIR, CONNECTIONS_DIR]:
        for fpath in _md_files_in(directory):
            mtime = os.path.getmtime(fpath)
            if mtime > thirty_days_ago:
                continue
            try:
                with open(fpath, "r") as f:
                    content = f.read().lower()
            except Exception:
                continue
            referenced = [p for p in active_projects if p in content]
            if referenced:
                fname = os.path.basename(fpath)
                age_days = int((now - mtime) / DAY)
                findings.append({
                    "category": "stale_data",
                    "severity": "warning",
                    "message": f"'{fname}' references active project(s) {referenced} but hasn't been updated in {age_days} days",
                    "action": f"Review and update '{fname}' or confirm it is still accurate",
                })

    return findings


# ---------------------------------------------------------------------------
# 3. Raw-to-wiki discrepancies
# ---------------------------------------------------------------------------

def check_raw_to_wiki(now: float) -> list[dict]:
    findings = []
    one_day_ago = now - DAY

    if not os.path.isdir(INBOX_RAW):
        return findings

    for fname in os.listdir(INBOX_RAW):
        fpath = os.path.join(INBOX_RAW, fname)
        if not os.path.isfile(fpath):
            continue
        if fname.startswith("."):
            continue
        mtime = os.path.getmtime(fpath)
        if mtime < one_day_ago:
            age_hours = int((now - mtime) / 3600)
            findings.append({
                "category": "raw_to_wiki",
                "severity": "error" if age_hours > 72 else "warning",
                "message": f"'{fname}' has been in 00-inbox/raw/ for {age_hours} hours without processing",
                "action": f"Process '{fname}' through the compile pipeline or delete if not needed",
            })

    return findings


# ---------------------------------------------------------------------------
# 4. Broken links
# ---------------------------------------------------------------------------

WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")


def check_broken_links() -> list[dict]:
    findings = []

    # Build index of all .md file slugs in the vault
    all_files = _all_md_files(VAULT_DIR)
    known_slugs = {_slug(f) for f in all_files}
    # Also index by relative path stem for nested references
    known_names = set()
    for f in all_files:
        name = os.path.splitext(os.path.basename(f))[0].lower()
        known_names.add(name)

    for fpath in all_files:
        try:
            with open(fpath, "r") as f:
                content = f.read()
        except Exception:
            continue

        links = WIKI_LINK_RE.findall(content)
        for link in links:
            target = link.strip().lower()
            # Normalize: strip path components, just match the note name
            target_slug = os.path.splitext(os.path.basename(target))[0]
            target_slug = re.sub(r"[^a-z0-9-]", "-", target_slug).strip("-")

            if target_slug not in known_names and target.lower() not in known_names:
                rel = os.path.relpath(fpath, VAULT_DIR)
                findings.append({
                    "category": "broken_links",
                    "severity": "error",
                    "message": f"Broken wiki-link [[{link}]] in '{rel}'",
                    "action": f"Create '{link}.md' or fix the link in '{rel}'",
                })

    return findings


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def build_report(findings: list[dict]) -> str:
    """Build the lint-report.md content."""
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")

    lines = [
        "# Vault Lint Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Summary:** {errors} error(s), {warnings} warning(s)",
        "",
    ]

    if not findings:
        lines.append("No issues found. Vault is healthy.")
        return "\n".join(lines)

    categories = [
        ("gaps", "Gaps"),
        ("stale_data", "Stale Data"),
        ("raw_to_wiki", "Raw-to-Wiki Discrepancies"),
        ("broken_links", "Broken Links"),
    ]

    for cat_key, cat_name in categories:
        cat_findings = [f for f in findings if f["category"] == cat_key]
        if not cat_findings:
            continue

        lines.append(f"## {cat_name}")
        lines.append("")
        for f in cat_findings:
            icon = "x" if f["severity"] == "error" else "!"
            lines.append(f"- [{icon}] **{f['severity'].upper()}**: {f['message']}")
            lines.append(f"  - Action: {f['action']}")
        lines.append("")

    return "\n".join(lines)


def summary_line(findings: list[dict]) -> str:
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    return f"{errors} error(s), {warnings} warning(s) found."


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Vault health check / lint")
    parser.add_argument("--quick", action="store_true",
                        help="Stdout summary only, no report file written")
    args = parser.parse_args()

    now = time.time()

    findings = []
    findings.extend(check_gaps(now))
    findings.extend(check_stale(now))
    findings.extend(check_raw_to_wiki(now))
    findings.extend(check_broken_links())

    print(summary_line(findings))

    if not args.quick:
        report = build_report(findings)
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w") as f:
            f.write(report)
        print(f"Full report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
