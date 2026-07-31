#!/usr/bin/env python3
"""Fetch GitHub advisories for K8s."""
import urllib.request, ssl, json, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', 'Accept': 'application/vnd.github+json'}

print("=== GitHub Advisories (Go ecosystem, K8s) ===")
try:
    req = urllib.request.Request('https://api.github.com/advisories?ecosystem=go&keywords=kubernetes&per_page=15', headers=hdr)
    data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
    advisories = json.loads(data)
    if isinstance(advisories, list):
        print(f"Results: {len(advisories)}")
        for adv in advisories:
            ghsa = adv.get('ghsa_id', '?')
            summary = adv.get('summary', '')
            sev = adv.get('severity', {})
            if isinstance(sev, dict):
                cvss = sev.get('score', '?')
                severity = sev.get('severity', '?')
            else:
                cvss = '?'
                severity = str(sev)
            desc = adv.get('description', '')[:300]
            url = adv.get('html_url', adv.get('permalink', ''))
            identifiers = ', '.join(adv.get('identifiers', [])) if isinstance(adv.get('identifiers'), list) else ''
            print(f"  ID: {ghsa} | {identifiers}")
            print(f"  Summary: {summary}")
            print(f"  Severity: {severity} | CVSS: {cvss}")
            print(f"  URL: {url}")
            print(f"  DESC: {desc}")
            print()
except Exception as e:
    print(f"Error: {e}")

print("\n=== GitHub Advisories (all, keyword kubernetes) ===")
try:
    req = urllib.request.Request('https://api.github.com/advisories?keywords=kubernetes&per_page=15', headers=hdr)
    data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
    advisories = json.loads(data)
    if isinstance(advisories, list):
        print(f"Results: {len(advisories)}")
        for adv in advisories:
            ghsa = adv.get('ghsa_id', '?')
            summary = adv.get('summary', '')
            sev = adv.get('severity', {})
            if isinstance(sev, dict):
                cvss = sev.get('score', '?')
                severity = sev.get('severity', '?')
            else:
                cvss = '?'
                severity = str(sev)
            url = adv.get('html_url', adv.get('permalink', ''))
            print(f"  {ghsa}: {summary[:100]}")
            print(f"    {severity} | CVSS: {cvss} | {url}")
            print()
except Exception as e:
    print(f"Error: {e}")
