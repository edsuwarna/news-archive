#!/usr/bin/env python3
"""Fetch full article content from The Hacker News for K8s security advisories."""
import urllib.request, ssl, re, html as hmod, sys

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
        print(f"  Error: {e}", file=sys.stderr)
        return ''

urls = [
    ('ArgoCD', 'https://thehackernews.com/2026/07/unpatched-argo-cd-repo-server-flaw.html'),
    ('DockerCVE', 'https://thehackernews.com/2026/04/docker-cve-2026-34040-lets-attackers.html'),
    ('Trivy', 'https://thehackernews.com/2026/03/trivy-hack-spreads-infostealer-via.html'),
    ('PCPJack', 'https://thehackernews.com/2026/05/pcpjack-credential-stealer-exploits-5.html'),
    ('LiteLLM', 'https://thehackernews.com/2026/03/teampcp-backdoors-litellm-versions.html'),
]

for name, url in urls:
    content = fetch(url)
    paras = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
    text_parts = []
    for p in paras:
        t = re.sub(r'<[^>]+>', '', p).strip()
        t = hmod.unescape(t)
        if len(t) > 60:
            text_parts.append(t)
    full = ' | '.join(text_parts[:8])
    with open(f'/tmp/{name}.txt', 'w') as f:
        f.write(full)
    print(f'Done {name}: {len(full)} chars')
