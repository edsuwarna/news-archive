#!/usr/bin/env python3
"""Safety-net: detect unpushed article .md files and push them.
Run every 30m via cron. Auto-regenerate articles.json + git push."""
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_DIR = Path("/home/ubuntu/projects-repo/news-archive")
CATEGORIES = ["devops/", "baremetal/", "selfhosted/", "ekonomi/", 
              "k8s-security/", "tech-foundations/", "ai/"]

def run(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or str(REPO_DIR))
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def main():
    # Check if there are new article .md files in commits ahead of origin/main
    rc, out, _ = run("git diff --name-only HEAD origin/main -- '*.md'", str(REPO_DIR))
    if rc != 0 or not out:
        print("[silent] No new article files")
        return
    
    # Only care about category dirs, not scripts/index.html etc
    new_articles = [f for f in out.split('\n') if any(c in f for c in CATEGORIES)]
    if not new_articles:
        print("[silent] No new article files in category dirs")
        return
    
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Safety-net found {len(new_articles)} new article(s):")
    for f in new_articles[:5]:
        print(f"  - {f}")
    
    # Regenerate articles.json
    rc1, _, err1 = run("python3 scripts/generate-articles-json.py", str(REPO_DIR))
    if rc1 != 0:
        print(f"FAIL: generate-articles-json: {err1}")
        sys.exit(1)
    
    # Commit & push
    run("git add -A", str(REPO_DIR))
    rc2, _, _ = run('git commit -m "safety-net: regenerate articles.json"', str(REPO_DIR))
    if rc2 == 0:
        rc3, _, err3 = run("git push origin main", str(REPO_DIR))
        if rc3 != 0:
            print(f"PUSH ERROR: {err3}")
            sys.exit(1)
        print("Pushed ✅")
    else:
        print("Nothing to commit")

if __name__ == "__main__":
    main()
