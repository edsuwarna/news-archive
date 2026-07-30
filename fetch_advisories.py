#!/usr/bin/env python3
"""Fetch K8s security advisories - simpler approach."""
import json
import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Mozilla/5.0'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        text = r.read().decode('utf-8')
        return json.loads(text)

# Test: just fetch one page
try:
    data = fetch_json("https://api.github.com/advisories?per_page=20&sort=published&order=desc")
    print(f"Got {len(data)} results on page 1")
    for adv in data[:5]:
        print(f"  {adv.get('cve_id','?'):20s} {adv.get('severity','?'):10s} {adv.get('summary','')[:80]}")
except Exception as e:
    print(f"Error: {e}")

# Now try with a search query
try:
    import urllib.parse
    q = urllib.parse.quote("kubernetes")
    data2 = fetch_json(f"https://api.github.com/advisories?query={q}&per_page=20&sort=published&order=desc")
    print(f"\nKuery query: got {len(data2)} results")
    for adv in data2:
        print(json.dumps({
            'cve': adv.get('cve_id'),
            'ghsa': adv.get('ghsa_id'),
            'summary': adv.get('summary'),
            'severity': adv.get('severity'),
            'cvss': adv.get('cvss',{}).get('score') if adv.get('cvss') else None,
            'url': adv.get('html_url'),
            'published': adv.get('published_at'),
            'desc': re.sub(r'<[^>]*>', '', adv.get('description',''))[:300],
            'vulns': [{'pkg': v.get('package',{}).get('name'), 
                      'range': v.get('vulnerable_version_range'),
                      'fix': v.get('first_patched_version',{}).get('identifier') if v.get('first_patched_version') else None}
                     for v in adv.get('vulnerabilities',[])]
        }))
        print("---")
except Exception as e:
    print(f"Search Error: {e}")
