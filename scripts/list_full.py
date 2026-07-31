#!/usr/bin/env python3
import json
with open('/tmp/k8s_v2.json') as f:
    data = json.load(f)
for i, item in enumerate(data):
    title = item.get('title','')[:200].replace('\n',' ').strip()
    src = item.get('source','')
    url = item.get('url','')
    print(f'{i+1}. [{src}] {title}')
    print(f'   {url}')
    print()
