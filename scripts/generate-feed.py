#!/usr/bin/env python3
"""Generate RSS 2.0 feed from news-archive markdown content.
Outputs feed.xml to repo root. Designed to run after cron pushes new articles.

Usage: python3 scripts/generate-feed.py
       (run from repo root, or set --repo-dir)
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

REPO_DIR = Path(__file__).resolve().parent.parent

SITE_URL = "https://news.edsuwarna.id"
FEED_DESC = "Automated news aggregation archive — DevOps, Economy, Security and more"

CATEGORY_INFO = {
    "devops": {"emoji": "⚙️", "name": "DevOps"},
    "baremetal": {"emoji": "🖥️", "name": "Bare Metal"},
    "selfhosted": {"emoji": "🏠", "name": "Self Hosted"},
    "ekonomi": {"emoji": "📊", "name": "Ekonomi"},
    "k8s-security": {"emoji": "🔒", "name": "K8s Security"},
    "tech-foundations": {"emoji": "🏗️", "name": "Tech Foundations"},
}


def clean_text(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text.strip()


def extract_news_items(md_text: str) -> list[dict]:
    """Extract individual news items from a markdown article."""
    # Remove frontmatter
    text = re.sub(r"^---[\s\S]*?---\n*", "", md_text)

    items = []
    current_meta = None
    current_lines = []

    for line in text.split("\n"):
        m = re.match(r"^##\s+(\d+)\.\s*(.*)", line)
        if m:
            if current_meta:
                items.append((current_meta, "\n".join(current_lines).strip()))
            current_meta = {"num": m.group(1), "title": m.group(2).strip()}
            current_lines = []
        elif current_meta is not None:
            current_lines.append(line)

    if current_meta:
        items.append((current_meta, "\n".join(current_lines).strip()))

    parsed = []
    for meta, content in items:
        num = meta["num"]
        title_line = meta["title"]

        # Extract emoji from title (any high-unicode / emoji character at start)
        first_char = title_line.strip()[:1] if title_line.strip() else ""
        if first_char and not first_char.isascii():
            emoji = first_char
            title = title_line.strip()[len(emoji):].strip()
        else:
            emoji = "📄"
            title = title_line.strip()

        # Clean content: remove **Source:** and **Summary:** markers, extract link
        content_clean = content.strip()

        # Extract link from **Source:** or 🔗 pattern
        link = ""
        link_match = re.search(r'\*\*Source:\*\*\s*(https?://\S+)', content_clean)
        if link_match:
            link = link_match.group(1)
        else:
            link_match = re.search(r'🔗\s*(https?://\S+)', content_clean)
            if link_match:
                link = link_match.group(1)

        # Clean up: remove **Summary:** and **Source:** lines
        content_clean = re.sub(r'\*\*Summary:\*\*\s*', '', content_clean)
        content_clean = re.sub(r'\*\*Source:\*\*\s*https?://\S+', '', content_clean)
        content_clean = re.sub(r'🔗\s*https?://\S+', '', content_clean)
        content_clean = clean_text(content_clean)

        if len(content_clean) > 250:
            content_clean = content_clean[:247].rstrip() + "..."

        parsed.append({
            "num": num,
            "emoji": emoji,
            "title": title,
            "description": content_clean,
            "link": link,
        })

    return parsed


def build_rss(entries: list) -> str:
    """Build RSS 2.0 XML string."""
    now_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">',
        "  <channel>",
        f"    <title>News Archive</title>",
        f"    <link>{SITE_URL}</link>",
        f"    <description>{escape(FEED_DESC)}</description>",
        f"    <language>en</language>",
        f"    <lastBuildDate>{now_str}</lastBuildDate>",
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>',
    ]

    for entry in entries[:50]:  # Max 50 entries
        title = escape(entry["title"])
        desc = escape(entry["description"])
        link = escape(entry.get("link") or SITE_URL)
        article_link = escape(entry["article_url"])
        pub_date = entry.get("pub_date", now_str)
        cat_name = escape(entry["category_name"])
        cat_emoji = entry["category_emoji"]

        lines.append("    <item>")
        lines.append(f"      <title>{cat_emoji} {title}</title>")
        lines.append(f"      <link>{article_link}</link>")
        lines.append(f"      <guid isPermaLink=\"true\">{article_link}</guid>")
        lines.append(f"      <description>{desc}</description>")
        lines.append(f"      <category>{cat_name}</category>")
        lines.append(f"      <pubDate>{pub_date}</pubDate>")
        if entry.get("link"):
            lines.append(f"      <source url=\"{link}\">{title}</source>")
        lines.append("    </item>")

    lines.append("  </channel>")
    lines.append("</rss>")

    return "\n".join(lines)


def main():
    repo = REPO_DIR
    if "--repo-dir" in sys.argv:
        idx = sys.argv.index("--repo-dir")
        repo = Path(sys.argv[idx + 1])

    manifest_path = repo / "articles.json"
    if not manifest_path.exists():
        print("❌ articles.json not found. Run generate-articles-json.py first.")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    entries = []

    for cat, articles in manifest.items():
        if not articles:
            continue
        info = CATEGORY_INFO.get(cat, {"emoji": "📄", "name": cat})

        for article in articles:
            file_name = article["file"]
            article_title = article.get("title", "")
            md_path = repo / cat / file_name

            if not md_path.exists():
                continue

            md_text = md_path.read_text(encoding="utf-8")
            items = extract_news_items(md_text)

            # Date for pubDate
            date_str = file_name.replace(".md", "")
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                pub_date = dt.strftime("%a, %d %b %Y 00:00:00 +0000")
            except ValueError:
                pub_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

            article_url = f"{SITE_URL}/#/{cat}/{file_name}"

            if items:
                # Use each news item as a separate RSS entry
                for item in items:
                    entries.append({
                        "title": f"{article_title} — {item['title']}",
                        "description": item["description"],
                        "link": item["link"],
                        "article_url": article_url,
                        "category_name": info["name"],
                        "category_emoji": info["emoji"],
                        "pub_date": pub_date,
                    })
            else:
                # Fallback: article itself is the entry
                excerpt = article.get("excerpt", article_title)
                entries.append({
                    "title": article_title or f"{info['name']} — {date_str}",
                    "description": excerpt,
                    "link": article_url,
                    "article_url": article_url,
                    "category_name": info["name"],
                    "category_emoji": info["emoji"],
                    "pub_date": pub_date,
                })

    # Sort by date descending
    entries.sort(key=lambda e: e.get("pub_date", ""), reverse=True)

    rss_xml = build_rss(entries)

    output = repo / "feed.xml"
    output.write_text(rss_xml, encoding="utf-8")

    print(f"✅ feed.xml generated — {len(entries)} RSS entries ({sum(len(manifest.get(c,[])) for c in manifest)} articles across {len([c for c in manifest if manifest[c]])} categories)")


if __name__ == "__main__":
    main()
