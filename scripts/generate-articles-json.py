#!/usr/bin/env python3
"""Generate articles.json manifest from news-archive markdown files.
Run after cron jobs push new articles to keep the SPA index up to date.

Usage: python3 scripts/generate-articles-json.py
       (run from repo root, or set --repo-dir)
"""

import json
import os
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

CATEGORIES = [
    "devops", "baremetal", "selfhosted", "ekonomi",
    "k8s-security", "tech-foundations", "f1", "motogp"
]

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
        files = sorted(
            f.name for f in cat_dir.iterdir()
            if f.is_file() and f.suffix == ".md"
        )
        manifest[cat] = files

    output = repo / "articles.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    total = sum(len(v) for v in manifest.values())
    print(f"✅ articles.json generated — {total} articles across {len(CATEGORIES)} categories")

if __name__ == "__main__":
    main()
