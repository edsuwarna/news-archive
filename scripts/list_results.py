#!/usr/bin/env python3
import json
with open('/tmp/k8s_v2.json') as f:
    data = json.load(f)
print(f'Total items: {len(data)}')
for i, item in enumerate(data):
    title = item.get('title','')[:120].replace('\n',' ').strip()
    src = item.get('source','')
    cvss = item.get('cvss','?')
    sev = item.get('severity','?')
    url = item.get('url','')[:80]
    print(f'{i+1}. [{src}] CVSS:{cvss} Sev:{sev} | {title}')
    print(f'   URL: {url}')
    print()
