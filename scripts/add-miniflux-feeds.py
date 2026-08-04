#!/usr/bin/env python3
"""Add all verified RSS feeds to Miniflux via REST API."""

import json
import subprocess
import sys
import urllib.request
import time

BASE_URL = "http://localhost:8081"
TOKEN = ""

# Get token from pass store
try:
    result = subprocess.run(["pass", "show", "dokploy/miniflux/api-token"], capture_output=True, text=True)
    if result.returncode == 0:
        TOKEN = result.stdout.strip()
    else:
        print(f"❌ Failed to get token from pass!")
        sys.exit(1)
except FileNotFoundError:
    # Fallback to hardcoded token
    TOKEN = "8b42484bad9b8a8ece7b5f6c1c35c2ddcb0060396964d656c0e3359058da430b"
    print("⚠️ Using hardcoded token as fallback")

# Daftar feed yang sudah diverifikasi valid dari riset sebelumnya
FEEDS = [
    # DevOps/SRE/Cloud (9 sources)
    {"name": "InfoQ",               "url": "https://www.infoq.com/feed/"},
    {"name": "GitHub Blog",         "url": "https://github.blog/feed/"},
    {"name": "Cloudflare Blog",     "url": "https://blog.cloudflare.com/rss/"},
    {"name": "ArsTechnica Tech",    "url": "https://feeds.arstechnica.com/arstechnica/technology-lab"},
    {"name": "AWS News Blog",       "url": "https://aws.amazon.com/blogs/aws/feed/"},
    {"name": "ServeTheHome",        "url": "https://servethehome.com/feed/"},
    {"name": "The New Stack",       "url": "https://thenewstack.io/feed/"},
    {"name": "Google Cloud Blog",   "url": "https://cloud.google.com/blog/topics/cloud-engineering/feed/"},
    {"name": "TechCrunch",          "url": "https://techcrunch.com/feed/"},
    
    # Bare-Metal/Hardware (2 sources)
    {"name": "Tom's Hardware News",         "url": "https://www.tomshardware.com/news/rss"},
    {"name": "Data Center Knowledge",       "url": "https://www.datacenterknowledge.com/rss"},
    
    # Ekonomi Indo & Global (3 sources)
    {"name": "Bloomberg Markets",           "url": "https://feeds.bloomberg.com/markets/news.rss"},
    {"name": "Reuters Finance",             "url": "https://www.reutersagency.com/feed/?best-topics=finance-markets&post_type=best&keywords="},
    {"name": "Kontan.co.id",                "url": "https://www.kontan.co.id/rss"},
    
    # K8s Security (2 sources)
    {"name": "The Hacker News",             "url": "https://thehackernews.com/feeds/posts/default"},
    {"name": "Aqua Security Blog",          "url": "https://blog.aquasec.com/rss"},
    
    # Tech/OpenSource Foundations (3 sources)
    {"name": "Linux Foundation",            "url": "https://www.linuxfoundation.org/blog/feed/"},
    {"name": "OpenInfra",                   "url": "https://www.openinfra.dev/feed/"},
    {"name": "opensourced.com",             "url": "https://opensource.com/feed"},
    
    # F1/Motorsport (4 sources)
    {"name": "The Guardian F1",             "url": "https://www.theguardian.com/sport/formulaone/rss"},
    {"name": "RaceFans.net",                "url": "https://www.racefans.net/feed/"},
    {"name": "F1 Fanatic",                  "url": "https://f1fanatic.co.uk/feed/"},
    {"name": "Google News F1",              "url": "https://news.google.com/rss/search?q=Formula+1&hl=en-US&gl=US&ceid=US:en"},
]

print(f"[+] Adding {len(FEEDS)} feeds to Miniflux via API...\n")

HEADERS = {"X-Auth-Token": TOKEN}
added = 0
failed = 0

for i, feed in enumerate(FEEDS):
    name, url = feed["name"], feed["url"]
    try:
        data = json.dumps({"feed_url": url, "category_id": 1}).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/v1/feeds",
            data=data,
            headers={**HEADERS, "Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            response = json.loads(resp.read().decode('utf-8'))
            
            if "feed_id" in response:
                added += 1
                print(f"✅ [{i+1}] {name:<30s} → ID: {response['feed_id']}")
            elif response.get("message"):
                failed += 1
                msg = response.get('error_message', 'Unknown error')
                print(f"❌ [{failed}] {name:<30s} → Error: {msg}")
                
    except Exception as e:
        failed += 1
        err_msg = str(e).splitlines()[0] if isinstance(e, Exception) else str(e)
        print(f"❌ [{failed}] {name:<30s} → {err_msg[:80]}")
    
    # Small delay to avoid rate limiting
    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"🎉 Added:  {added}")
print(f"⚠️ Failed: {failed}")
print(f"Total:    {len(FEEDS)}")
