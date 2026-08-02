#!/usr/bin/env python3
"""Fetch bare-metal/hardware news from multiple sources via DDG searches + STH feed."""
import subprocess, sys, html as h, re, urllib.parse, json

def curl(url, max_time=15):
    r = subprocess.run(
        ['curl','-s','--compressed',f'--max-time {max_time}',
         '-H','User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
         url], capture_output=True, text=True)
    return r.stdout

def parse_sth_feed():
    """Parse ServeTheHome RSS feed."""
    data = curl('https://www.servethehome.com/feed/')
    if not data or 'xml' not in data[:200]:
        print("STH FEED EMPTY", flush=True)
        return []
    
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(data)
        ns_dc = '{http://purl.org/dc/elements/1.1/}'
        items = root.findall('.//item')
        results = []
        for item in items[:12]:
            t_el = item.find(f'{ns_dc}title')
            l_el = item.find('link')
            d_el = item.find(f'{ns_dc}description')
            if t_el is None or l_el is None:
                continue
            title = h.unescape(t_el.text.strip()) if t_el.text else ''
            link = l_el.text.strip() if l_el.text else ''
            brief = ''
            if d_el is not None and d_el.text:
                cleaned = re.sub(r'<[^>]+>', '', d_el.text)
                brief = re.sub(r'\s+', ' ', cleaned).strip()[:300]
            results.append(('serve-the-home', title, link, brief))
        return results
    except Exception as e:
        print(f"STH PARSE ERROR: {e}", flush=True)
        return []

def ddg_search(query, count=12):
    """Search via DuckDuckGo HTML."""
    encoded = urllib.parse.quote(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded}'
    data = curl(url)
    if not data:
        return []
    
    results = []
    # Extract organic result links and snippets
    # DDG format: <a class="result__a" href="...">...</a> then <a class="result__snippet" ...>...</a>
    links = re.findall(r'rel="ugc">(https?://[^\"]+)</a>', data)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', data)
    
    seen = set()
    for i, raw_link in enumerate(links):
        # Decode duckduckgo redirect URL
        actual = raw_link.replace('//duckduckgo.com/l/?uddg=', '').split('&')[0]
        actual = urllib.parse.unquote(actual)
        if actual in seen:
            continue
        seen.add(actual)
        
        snippet = snippets[i].strip() if i < len(snippets) else ''
        snippet = re.sub(r'<[^>]+>', '', snippet)
        
        # Clean domain for source identification
        src_name = 'other'
        dl = actual.lower()
        if 'servethehome.com' in dl:
            src_name = 'serve-the-home'
        elif 'phoronix.com' in dl:
            src_name = 'phoronix'
        elif 'tomshardware.com' in dl:
            src_name = "tom's hardware"
        elif 'theregister.com' in dl:
            src_name = 'the register'
        elif 'datacenterknowledge.com' in dl:
            src_name = 'data center knowledge'
        elif 'serve-the-home.com' in dl:
            src_name = 'serve-the-home'
        elif 'forums.servethehome.com' in dl:
            src_name = 'serve-the-home'
        
        results.append((src_name, '', actual, snippet))
    return results

def main():
    all_results = []
    
    # 1. Parse STH feed directly
    print("=== Fetching ServeTheHome Feed ===", flush=True)
    sth_items = parse_sth_feed()
    all_results.extend(sth_items)
    print(f"  Got {len(sth_items)} from STH feed", flush=True)
    
    # 2-5. DDG searches with different queries
    queries = [
        'bare metal server hardware infrastructure news site:servethehome.com OR site:phoronix.com OR site:theregister.com OR site:tomshardware.com OR site:datacenterknowledge.com 2025',
        'server CPU GPU hardware rack deployment latest news site:thefirehose.net OR site:serve-the-home.com',
        'data center server news hardware procurement 2025',
        'bare metal cloud server provisioning latest',
    ]
    
    for qi, query in enumerate(queries):
        print(f"=== Search {qi+1}: {query[:60]}... ===", flush=True)
        results = ddg_search(query)
        new_count = 0
        for src, title, link, snippet in results:
            # Check if already have this URL
            already = any(r[2] == link for r in all_results)
            if not already and title:  # Feed items may have empty title initially
                all_results.append((src, title, link, snippet))
                new_count += 1
        print(f"  Found {new_count} new items (total: {len(all_results)})", flush=True)
    
    # Print all collected
    print(f"\n=== TOTAL COLLECTED: {len(all_results)} ===", flush=True)
    for i, (src, title, link, snippet) in enumerate(all_results):
        print(f"{i}|{src}|{title}|{link}|{snippet}")

if __name__ == '__main__':
    main()
