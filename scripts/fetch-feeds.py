#!/usr/bin/env python3
"""Fetch news feeds from ServeTheHome, Phoronix, The Register, DCK, Tom's Hardware."""
import subprocess, sys, html as h

def curl(url, max_time=20):
    r = subprocess.run(['curl','-s',f'--max-time {max_time}',url], capture_output=True, text=True)
    return r.stdout

def parse_feeds():
    import xml.etree.ElementTree as ET
    
    sources = {
        'serve-the-home': 'https://www.servethehome.com/feed/',
        'phoronix': 'https://www.phoronix.com/feeds/all',
        'theregister': 'https://www.theregister.com/headlines/feed/',
        'dck': 'https://www.datacenterknowledge.com/feed',
    }
    
    for name, url in sources.items():
        print(f"=== FETCHING {name} ===", flush=True)
        data = curl(url)
        if not data:
            print(f"  EMPTY RESPONSE from {url}", flush=True)
            continue
        try:
            root = ET.fromstring(data)
            ns_dc = '{http://purl.org/dc/elements/1.1/}'
            ns_content = '{http://purl.org/rss/1.0/modules/content/}'
            ns_atom = '{http://www.w3.org/2005/Atom}'
            
            if name == 'theregister':
                items = root.findall(f'{ns_atom}entry')
            else:
                items = root.findall('.//item')
            
            count = 0
            for item in items[:10]:
                t_el = item.find(f'{ns_dc}title')
                l_el = item.find('link')
                d_el = item.find(f'{ns_dc}description')
                if t_el is None or l_el is None:
                    continue
                title = h.unescape(t_el.text.strip()) if t_el.text else ''
                link = l_el.text.strip() if l_el.text else ''
                brief = ''
                if d_el is not None and d_el.text:
                    import re
                    cleaned = re.sub(r'<[^>]+>', '', d_el.text)
                    brief = re.sub(r'\s+', ' ', cleaned).strip()[:250]
                print(f'T|{name}|{title}|{link}|{brief}')
                count += 1
            print(f"  Got {count} items from {name}", flush=True)
        except Exception as e:
            print(f"  ERROR parsing {name}: {e}", flush=True)
            # Try dumping first 500 chars
            print(f"  RAW preview: {data[:500]}", flush=True)

if __name__ == '__main__':
    parse_feeds()
