#!/bin/bash
# push-news.sh — Regenerate index & feed, then git commit & push
# Called by cron jobs after writing news markdown files.
# Usage: push-news.sh CATEGORY YYYY-MM-DD
# Example: push-news.sh devops 2026-07-31

set -e
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

CATEGORY="${1:-news}"
DATE="${2:-$(date -u +%Y-%m-%d)}"

# Generate index files
python3 scripts/generate-articles-json.py
python3 scripts/generate-feed.py

# Git commit & push
git add -A
git commit -m "${CATEGORY} ${DATE}"
git push origin main
