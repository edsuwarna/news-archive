#!/usr/bin/env python3
"""Parse NVD results and output sorted."""
import json, sys
with open('/tmp/nvd_full.json') as f:
    data = json.load(f)
data.sort(key=lambda x: float(x['cvss']) if x['cvss'] not in ['', 'N/A'] else 0, reverse=True)
for item in data:
    print(f"{item['id']} | CVSS:{item['cvss']} ({item['severity']}) | AV:{item['attackVector']} | {item['published']}")
    print(f"  {item['description'][:200]}")
    print()
