#!/usr/bin/env python3
"""Comprehensive scraper for bare-metal/server/hardware news from multiple websites."""
import urllib.request, re, html as h, json, os
from urllib.request import Request, urlopen

def make_request(url):
    """Fetch URL with good headers."""
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    resp = urlopen(req, timeout=20)
    return resp.read().decode('utf-8', errors='replace')


def score_article(title):
    """Score how relevant a title is to bare-metal/server/hardware."""
    combined = (title + ' server hardware infrastructure').lower()
    strong = ['bare metal', 'server', 'data center', 'rack mount', 'infrastructure']
    medium = ['cpu', 'gpu', 'nvidia', 'amd', 'intel', 'xeon', 'storage', 'ssd',
             'pcie', 'memory', 'ram', 'network', 'switch', 'raid', 'blade',
             'cluster', 'compute', 'supermicro', 'dell', 'hp', 'lenovo']
    weak = ['processor', 'graphics', 'chip', 'hardware', 'technology',
            'benchmark', 'performance', 'review', 'launch', 'new']
    
    s = sum(1 for k in strong if k in combined) * 5
    m = sum(1 for k in medium if k in combined) * 2
    w = sum(1 for k in weak if k in combined)
    return s + m + w


def extract_phoronix(page):
    """Extract articles from Phoronix homepage."""
    results = []
    
    # Phoronix uses article-title class or h2/h3 with links
    patterns = [
        # Main pattern: article-title divs
        r'<article[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>\s*<div[^>]*class="article-title"[^>]*>([^<]+)</div>',
        # Alternative: just href links in article blocks  
        r'<a[^>]*href="(https://www\.phoronix\.com/[^"]+)"[^>]*>\s*<strong[^>]*>([^<]+)</strong>',
        r'<a[^>]*href="(https://www\.phoronix\.com/[^"]+)"[^>]*>\s*<h[23][^>]*>([^<]+)</h[23]>',
    ]
    
    seen = set()
    for pat in patterns:
        for match in re.finditer(pat, page, re.DOTALL | re.IGNORECASE):
            link = match.group(1)
            title = h.unescape(match.group(2).strip())
            if title not in seen and len(title) > 15:
                seen.add(title)
                results.append((link, title))
    
    # Also try simpler link extraction - find all phoronix.com article links near top of page
    if len(results) < 5:
        link_titles = re.findall(r'href="(https://www\.phoronix\.com/\S+?)"[^>]*>(.*?)</a>', page[:30000], re.DOTALL)
        for link, title_block in link_titles:
            title = re.sub(r'<[^>]+>', '', title_block).strip()
            title = re.sub(r'\s+', ' ', title)
            title = h.unescape(title)
            if title not in seen and len(title) > 15:
                seen.add(title)
                results.append((link, title))
    
    return results


def extract_tomshardware(page):
    """Extract articles from Tom's Hardware news page."""
    results = []
    seen = set()
    
    # TH has various patterns for news cards
    patterns = [
        # News card links with titles
        r'class="[^"]*title[^"]*"[^>]*>\s*<[^>]*a[^>]*href="(/news/[^"]*)"[^>]*>([^<]+)</a>',
        r'href="(/news/[^\"]+)"[^>]*>\s*(.+?)</',
        # More generic - find /news/ URLs
        r'href="(https://www\.tomshardware\.com/news/[^\"]*)"',
    ]
    
    # Try to find H3 title + anchor pairs
    title_link_pairs = re.findall(
        r'<h[23][^>]*>\s*(?:<span[^>]*>)?\s*(?:<a[^>]*href="([^"]*)"[^>]*>)?(.+?)</(?:a></(?:span)?|span>?|h[23])>',
        page[:200000], re.DOTALL
    )
    
    for groups in title_link_pairs:
        if len(groups) == 2:
            link, title = groups
            if '/news/' not in link and 'tomshardware.com' not in link:
                continue
            if not link.startswith('http'):
                link = 'https://www.tomshardware.com' + link
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            title_clean = re.sub(r'\s+', ' ', title_clean)
            if len(title_clean) > 15 and title_clean not in seen:
                seen.add(title_clean)
                results.append((link, title_clean))
    
    # If still few, try extracting all /news/ links with surrounding text
    if len(results) < 5:
        news_links = re.findall(r'href="(https://www\.tomshardware\.com/news/[^\"]+)"', page[:200000])
        for nl in news_links:
            if nl not in seen:
                seen.add(nl)
                # Find nearby title text
                idx = page.find(nl)
                if idx > 0:
                    context = page[max(0,idx-200):idx+200]
                    title_match = re.search(r'(?:class="[^"]*title[^"]*"[^>]*>|<h[23][^>]*>)\s*(.+?)</(?:h[23]|span)', context, re.DOTALL)
                    if title_match:
                        t = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        t = re.sub(r'\s+', ' ', h.unescape(t))
                        results.append((nl, t))
    
    return results


def extract_dck(page):
    """Extract articles from Data Center Knowledge."""
    results = []
    seen = set()
    
    # DCK uses WordPress/Gutenberg patterns
    patterns = [
        r'class="entry-title"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
        r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
        r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
    ]
    
    for pat in patterns:
        matches = re.finditer(pat, page, re.DOTALL | re.IGNORECASE)
        for m in matches:
            link = m.group(1)
            title = re.sub(r'\s+', ' ', h.unescape(m.group(2).strip()))
            if len(title) > 15 and link not in seen:
                seen.add(link)
                results.append((link, title))
    
    # Extract all http links with dck domain
    if len(results) < 5:
        dck_links = re.findall(r'href="(https://www\.datacenterknowledge\.com/[^"]+)"', page)
        for dl in dck_links:
            if 'wp-json' in dl or '#respond' in dl or '/feed' in dl:
                continue
            if dl not in seen:
                seen.add(dl)
                idx = page.find(dl)
                if idx > 0:
                    context = page[max(0,idx-200):idx+200]
                    tm = re.search(r'<h[23][^>]*>(.+?)</h[23]>', context, re.DOTALL)
                    if tm:
                        t = re.sub(r'<[^>]+>', '', tm.group(1)).strip()
                        t = re.sub(r'\s+', ' ', h.unescape(t))
                        results.append((dl, t))
    
    return results


def main():
    all_news = []
    seen_urls = set()
    
    # === ServeTheHome Feed (confirmed working) ===
    print("=== ServeTheHome Feed ===")
    data = make_request('https://www.servethehome.com/feed/')
    import xml.etree.ElementTree as ET
    root = ET.fromstring(data)
    items = root.findall('.//item')
    for item in items[:15]:
        title_el = item.find('title')
        link_el = item.find('link')
        desc_el = item.find('description')
        if title_el is None or link_el is None:
            continue
        title = h.unescape((title_el.text or '').strip())
        link = (link_el.text or '').strip()
        brief = ''
        if desc_el is not None and desc_el.text:
            clean = re.sub(r'<[^>]+>', '', desc_el.text)
            brief = re.sub(r'\s+', ' ', clean).strip()[:300]
        if title and link:
            score = score_article(title)
            if score >= 2:
                all_news.append(('serve-the-home', 'ServeTheHome', title, link, brief, score))
                seen_urls.add(link)
    print(f"  Got {sum(1 for n in all_news if n[0]=='serve-the-home')} relevant articles")
    
    # === Additional STH pages ===
    print("\n=== ServeTheHome Homepage ===")
    sth_page = make_request('https://www.servethehome.com/')
    # Find "latest posts" or article links on homepage
    sth_links = re.findall(r'href="(https://www\.servethehome\.com/[^"]+)"', sth_page)
    for sl in sth_links:
        if '/feed' in sl or '/api' in sl or '/wp-' in sl:
            continue
        if sl not in seen_urls:
            seen_urls.add(sl)
            # Try to find title near link
            idx = sth_page.find(sl)
            if idx > 0:
                ctx = sth_page[max(0,idx-300):idx+100]
                tm = re.search(r'<h[23][^>]*>(.*?)</h[23]>', ctx, re.DOTALL)
                if tm:
                    t = re.sub(r'<[^>]+>', '', tm.group(1)).strip()
                    t = re.sub(r'\s+', ' ', h.unescape(t))
                    score = score_article(t)
                    if score >= 1:
                        all_news.append(('serve-the-home', 'ServeTheHome', t, sl, '', score))
    
    # === Phoronix ===
    print("\n=== Phoronix ===")
    try:
        phor_page = make_request('https://www.phoronix.com/')
        phor_articles = extract_phoronix(phor_page)
        for link, title in phor_articles:
            score = score_article(title)
            if score >= 1:
                if link not in seen_urls:
                    all_news.append(('phoronix', 'Phoronix', title, link, '', score))
                    seen_urls.add(link)
        print(f"  Found {len(phor_articles)} articles total, {sum(1 for n in all_news if n[0]=='phoronix')} relevant")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # === The Register (might be behind Cloudflare) ===
    print("\n=== The Register ===")
    try:
        reg_page = make_request('https://www.theregister.com/')
        # Look for article links with titles
        reg_titles = re.findall(r'href="(https://theregister\.com/[^\"]+)"', reg_page[:50000])
        for rl in reg_titles:
            if '/rss' in rl or '/atom' in rl or '/feeds' in rl:
                continue
            if rl not in seen_urls:
                seen_urls.add(rl)
                idx = reg_page.find(rl)
                if idx > 0:
                    ctx = reg_page[max(0,idx-400):idx+100]
                    tm = re.search(r'<(?:h|h2|h3)[^>]*>(.*?)</(?:h|h2|h3)>', ctx, re.DOTALL)
                    if tm:
                        t = re.sub(r'<[^>]+>', '', tm.group(1)).strip()
                        t = re.sub(r'\s+', ' ', h.unescape(t))
                        score = score_article(t)
                        if score >= 2:
                            all_news.append(('register', 'The Register', t, rl, '', score))
        print(f"  Found {sum(1 for n in all_news if n[0]=='register')} articles")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # === Data Center Knowledge ===
    print("\n=== Data Center Knowledge ===")
    try:
        dck_page = make_request('https://www.datacenterknowledge.com/')
        dck_articles = extract_dck(dck_page)
        for link, title in dck_articles:
            score = score_article(title)
            if score >= 2:
                if link not in seen_urls:
                    all_news.append(('dck', 'Data Center Knowledge', title, link, '', score))
                    seen_urls.add(link)
        print(f"  Found {len(dck_articles)} articles total, {sum(1 for n in all_news if n[0]=='dck')} relevant")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # === Tom's Hardware ===
    print("\n=== Tom's Hardware ===")
    try:
        th_page = make_request('https://www.tomshardware.com/news')
        th_articles = extract_tomshardware(th_page)
        for link, title in th_articles:
            score = score_article(title)
            if score >= 2:
                if link not in seen_urls:
                    all_news.append(("tomshardware", "Tom's Hardware", title, link, '', score))
                    seen_urls.add(link)
        print(f"  Found {len(th_articles)} articles total, {sum(1 for n in all_news if n[0]=='tomshardware')} relevant")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Sort by score descending
    all_news.sort(key=lambda x: -x[5])
    
    print(f"\n{'='*60}")
    print(f"TOTAL COLLECTED: {len(all_news)} articles")
    print(f"{'='*60}")
    
    for i, (src_key, display, title, link, brief, score) in enumerate(all_news[:25]):
        print(f"{i:2d}. [{score:2d}] {display}")
        print(f"     {title}")
        print(f"     {link}")
        if brief:
            print(f"     Brief: {brief[:150]}")
        print()
    
    # Save to JSON
    output = []
    for src_key, display, title, link, brief, score in all_news:
        output.append({
            'source': src_key,
            'display_name': display,
            'title': title,
            'url': link,
            'brief': brief,
            'score': score
        })
    
    os.makedirs('/tmp', exist_ok=True)
    with open('/tmp/baremetal_news.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to /tmp/baremetal_news.json ({len(output)} articles)")


if __name__ == '__main__':
    main()
