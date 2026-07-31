#!/usr/bin/env python3
"""Fetch detailed content of K8s advisory articles."""
import urllib.request, ssl, re, sys, json, html

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=hdr)
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

# Critical articles to fetch details from
articles = [
    ("Argo CD unpatched flaw", "https://thehackernews.com/2026/07/unpatched-argo-cd-repo-server-flaw.html"),
    ("Docker CVE-2026-34040", "https://thehackernews.com/2026/04/docker-cve-2026-34040-lets-attackers.html"),
    ("Trivy supply chain", "https://thehackernews.com/2026/03/trivy-hack-spreads-infostealer-via.html"),
    ("PCPJack", "https://thehackernews.com/2026/05/pcpjack-credential-stealer-exploits-5.html"),
    ("LiteLLM backdoor", "https://thehackernews.com/2026/03/teampcp-backdoors-litellm-versions.html"),
    ("K8s Azure Cosmos Escape", "https://thehackernews.com/2026/07/azure-cosmos-db-flaw-exposed-platform.html"),
]

for name, url in articles:
    print(f"\n{'='*60}")
    print(f"=== {name} ===")
    print(f"URL: {url}")
    content = fetch(url)
    # Extract paragraphs
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
    for p in paragraphs[:10]:
        text = re.sub(r'<[^>]+>', '', p).strip()
        text = html.unescape(text)
        if len(text) > 50:
            print(f"  {text[:500]}")
            print()
