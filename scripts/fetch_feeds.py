#!/usr/bin/env python3
"""Fetch K8s CVE feed, NVD, and GitHub advisories."""
import urllib.request, ssl, json, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

# 1. K8s CVE feed
print("=== K8s Official CVE Feed ===")
try:
    req = urllib.request.Request('https://kubernetes.io/docs/reference/issues-security/official-cve-feed/index.xml', headers=hdr)
    data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
    print(f"Downloaded: {len(data)} bytes")
    # Extract entries
    import re
    entries = re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL)
    print(f"Entries: {len(entries)}")
    for e in entries[-20:]:
        title_m = re.search(r'<title[^>]*>(.*?)</title>', e, re.DOTALL)
        link_m = re.search(r'<link[^>]*href="([^"]+)"', e)
        desc_m = re.search(r'<content[^>]*>(.*?)</content>', e, re.DOTALL)
        title = title_m.group(1).strip() if title_m else ''
        link = link_m.group(1).strip() if link_m else ''
        desc = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()[:200] if desc_m else ''
        print(f"  {title}")
        print(f"    URL: {link}")
        print(f"    DESC: {desc}")
        print()
except Exception as e:
    print(f"Error: {e}")

# 2. NVD
print("\n=== NVD API ===")
try:
    req = urllib.request.Request('https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=kubernetes&pubStartDate=2026-06-01T00:00:00.000&pubEndDate=2026-07-31T23:59:59.000&resultsPerPage=15', headers=hdr)
    data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
    results = json.loads(data)
    print(f"Total: {results.get('totalResults', 0)}")
    for vuln in results.get('vulnerabilities', []):
        cve = vuln.get('cve', {})
        id_ = cve.get('id', '')
        desc = ''
        for d in cve.get('descriptions', []):
            if d.get('lang') == 'en':
                desc = d.get('value', '')[:150]
                break
        metrics = cve.get('metrics', {})
        cvss = ''
        for k in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
            if k in metrics and metrics[k]:
                cvss = str(metrics[k][0].get('cvssData', {}).get('baseScore', ''))
                break
        print(f"  {id_} | CVSS: {cvss} | {desc}")
except Exception as e:
    print(f"Error: {e}")

# 3. GitHub Advisory DB
print("\n=== GitHub Advisories ===")
try:
    req = urllib.request.Request('https://api.github.com/advisories?ecosystem=go&keywords=kubernetes&per_page=10', headers={**hdr, 'Accept': 'application/vnd.github+json'})
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
            else:
                cvss = '?'
            desc = adv.get('description', '')[:200]
            url = adv.get('html_url', adv.get('permalink', ''))
            print(f"  {ghsa}: {summary[:80]}")
            print(f"    CVSS: {cvss} | {url}")
            print(f"    {desc}")
            print()
except Exception as e:
    print(f"Error: {e}")
