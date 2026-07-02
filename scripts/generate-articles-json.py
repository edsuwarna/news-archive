#!/usr/bin/env python3
"""Generate articles.json manifest with metadata from markdown files.
Run after cron jobs push new articles to keep the SPA index up to date.

Usage: python3 scripts/generate-articles-json.py
       (run from repo root, or set --repo-dir)
"""

import json
import os
import re
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

CATEGORIES = [
    "devops", "baremetal", "selfhosted", "ekonomi",
    "k8s-security", "tech-foundations", "f1", "motogp"
]

CATEGORY_INFO = {
    "devops": {"emoji": "⚙️", "name": "DevOps"},
    "baremetal": {"emoji": "🖥️", "name": "Bare Metal"},
    "selfhosted": {"emoji": "🏠", "name": "Self Hosted"},
    "ekonomi": {"emoji": "📊", "name": "Ekonomi"},
    "k8s-security": {"emoji": "🔒", "name": "K8s Security"},
    "tech-foundations": {"emoji": "🏗️", "name": "Tech Foundations"},
    "f1": {"emoji": "🏎️", "name": "F1"},
    "motogp": {"emoji": "🏍️", "name": "MotoGP"},
}


def clean_text(text: str) -> str:
    """Clean markdown formatting from text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text.strip()


def extract_metadata(md_path: Path) -> dict:
    """Extract title, excerpt, and article count from a markdown file."""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    title = ""
    excerpt = ""
    article_count = 0

    # --- Extract title ---
    # Priority: H1 > H2 (with uppercase/emoji) > bold first line > filename
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            title = stripped[2:].strip()
            break

    if not title:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") and len(stripped) > 4:
                title = stripped[3:].strip()
                break

    if not title:
        for line in lines:
            stripped = line.strip()
            # Bold text that looks like a title (not a link)
            if re.match(r"^\*\*.+\*\*$", stripped):
                title = clean_text(stripped)
                break

    if not title:
        # Try first non-empty line as title
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                title = clean_text(stripped)[:100]
                break

    if not title:
        title = md_path.stem.replace("-", "/")

    # --- Extract excerpt ---
    # Find first substantial content after the first --- separator
    # Skip: headings, empty lines, link-only lines, separator lines
    found_sep = False
    for line in lines:
        if not found_sep:
            if line.strip() == "---":
                found_sep = True
            continue

        stripped = line.strip()

        # Skip empty, headings, separators
        if not stripped:
            continue
        if stripped.startswith("#") or stripped == "---":
            continue
        if stripped.startswith("🔗") or re.match(r"^https?://", stripped):
            continue
        if re.match(r"^!\w+", stripped):
            continue

        # Take this as excerpt
        excerpt = clean_text(stripped)

        # Truncate
        if len(excerpt) > 150:
            excerpt = excerpt[:147].rstrip() + "..."

        # If excerpt is meaningful enough, stop
        if len(excerpt) > 20:
            break

        # Otherwise keep looking for longer content
        excerpt = ""

    # If no excerpt found after separator, try before it
    if not excerpt:
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped == "---":
                continue
            excerpt = clean_text(stripped)
            if len(excerpt) > 150:
                excerpt = excerpt[:147].rstrip() + "..."
            if len(excerpt) > 20:
                break

    # --- Count articles ---
    # Various formats: "## N.", "### ⚡ Title", "## 📊 TITLE"
    for line in lines:
        stripped = line.strip()
        # Count "## N. Title" or "## emoji Title" or "### emoji Title"
        if re.match(r"^#{2,3}\s+\d+\.", stripped):
            article_count += 1
        elif re.match(r"^###\s+[🏆⚡🛡️🔧💰🔓📊🇮🇩🌏]", stripped):
            article_count += 1

    # If article_count is 0 but there are H2s, count those
    if article_count == 0:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("### "):
                # Skip if it's a section header not an article
                section_headers = ["critical", "high", "medium", "low", "indonesia",
                                   "global", "agenda", "reminder", "schedule",
                                   "weekend", "friday", "saturday", "sunday",
                                   "pembukaan", "penutupan"]
                lower = stripped.lower()
                if not any(h in lower for h in section_headers):
                    article_count += 1

    return {
        "title": title,
        "excerpt": excerpt,
        "count": article_count,
    }


def filename_date_key(file: str) -> str:
    """Extract date from filename like 2026-07-02.md for sorting."""
    return file.replace(".md", "")


def main():
    repo = REPO_DIR
    if "--repo-dir" in sys.argv:
        idx = sys.argv.index("--repo-dir")
        repo = Path(sys.argv[idx + 1])

    manifest = {}
    for cat in CATEGORIES:
        cat_dir = repo / cat
        if not cat_dir.exists():
            manifest[cat] = []
            continue

        articles = []
        for md_file in sorted(
            f for f in cat_dir.iterdir()
            if f.is_file() and f.suffix == ".md"
        ):
            meta = extract_metadata(md_file)
            articles.append({
                "file": md_file.name,
                "title": meta["title"],
                "excerpt": meta["excerpt"],
                "count": meta["count"],
            })

        # Sort by filename date descending — newest first
        articles.sort(key=lambda a: a["file"], reverse=True)
        manifest[cat] = articles

    output = repo / "articles.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    total = sum(len(v) for v in manifest.values())
    print(f"✅ articles.json generated — {total} articles across {len(CATEGORIES)} categories")
    for cat in CATEGORIES:
        count = len(manifest[cat])
        if count > 0:
            print(f"   {CATEGORY_INFO[cat]['emoji']} {cat}: {count} articles")


if __name__ == "__main__":
    main()
