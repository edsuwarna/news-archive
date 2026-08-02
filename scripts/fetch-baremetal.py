#!/usr/bin/env python3
"""
Fetch bare-metal/hardware news from ServeTheHome, Phoronix, The Register,
Data Center Knowledge, Tom's Hardware via RSS/feeds + web scraping.
Output format: SRC<TAB>TITLE<TAB>LINK<TAB>BRIEF
"""
import sys, json, os, re, html as h
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError
import xml.etree.ElementTree as ET

def fetch_feed(url):
    """Fetch an RSS/Atom feed and return list of (title, link, description)."""
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; NewsCronBot/1.0; +https://news-archive.local)',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })
        resp = urlopen(req, timeout=20)
        data = resp.read().decode('utf-8', errors='replace')
        root = ET.fromstring(data)
    except Exception as e:
        print(f"  FETCH ERROR {url}: {e}", file=sys.stderr, flush=True)
        return []

    results = []
    ns_dc = '{http://purl.org/dc/elements/1.1/}'
    ns_content = '{http://purl.org/rss/1.0/modules/content/}'
    ns_atom = '{http://www.w3.org/2005/Atom}'

    # Atom feed entries (The Register)
    items = root.findall(f'{ns_atom}entry')
    if len(items) > 0:
        source_name = "atom"
    else:
        items = root.findall('.//item')
        source_name = "rss"

    for item in items[:15]:
        t_el = item.find('title')
        l_el = item.find('link')
        
        # For RSS with DC namespace, also try dc:title
        if t_el is None:
            t_el = item.find(f'{ns_dc}title')
        if l_el is None:
            l_el = item.find('link')

        if t_el is None or l_el is None:
            continue
            
        title_text = (t_el.text or '').strip()
        link = (l_el.text or '').strip()
        if not title_text or not link:
            continue
        
        # Get description/body
        body = ''
        desc_el = item.find(f'{ns_content}encoded')
        if desc_el is None:
            desc_el = item.find(f'{ns_dc}description')
        if desc_el is None:
            desc_el = item.find('description')
        if desc_el is not None and desc_el.text:
            cleaned = re.sub(r'<[^>]+>', '', desc_el.text)
            body = re.sub(r'\s+', ' ', cleaned).strip()[:400]

        results.append((title_text, link, body))

    return results


def search_web(query, max_results=8):
    """Search via Google News-style approach using Bing/DuckDuckGo alternatives."""
    # Try to scrape pages directly instead of search engines
    return []


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    all_news = []
    seen_urls = set()

    feeds = [
        ('serve-the-home', 'https://www.servethehome.com/feed/', 'ServeTheHome'),
        ('phoronix', 'https://www.phoronix.com/feeds/all', 'Phoronix'),
        ('the-register', 'https://www.theregister.com/headlines/feed/', 'The Register'),
        ('data-center-knowledge', 'https://www.datacenterknowledge.com/feed', 'Data Center Knowledge'),
    ]

    for src_key, url, display_name in feeds:
        print(f"Fetching {display_name}...", flush=True)
        results = fetch_feed(url)
        for title, link, brief in results:
            # Check relevance to bare-metal/server/hardware
            combined = (title + ' ' + brief).lower()
            keywords = ['server', 'bare metal', 'hardware', 'cpu', 'gpu', 
                       'rack', 'data center', 'storage', 'ssd', 'nvidia', 
                       'amd', 'intel', 'xeon', 'power supply', 'networking',
                       'switch', 'ethernet', ' infiniband', 'pcie', 'compute',
                       'supermicro', 'dell', 'hp', 'lenovo']
            
            match_count = sum(1 for kw in keywords if kw in combined)
            if match_count >= 1:
                if link not in seen_urls:
                    all_news.append((src_key, display_name, title, link, brief))
                    seen_urls.add(link)
        print(f"  Got {len(results)} items from {display_name}", flush=True)

    # Filter to just server/bare-metal related
    final = []
    for src_key, display_name, title, link, brief in all_news:
        combined = (title + ' ' + brief).lower()
        strong_kw = ['bare metal', 'server', 'data center', 'rack', 'infrastructure',
                     'xeon', 'cuda', 'infiniband', 'nvme', 'raid', 'blade', 'cluster']
        weak_kw = ['cpu', 'gpu', 'pci', 'ssd', 'ram', 'network', 'switch',
                   'amd', 'nvidia', 'intel', 'supermicro', 'dell', 'storage']
        score = sum(1 for kw in strong_kw if kw in combined) * 3
        score += sum(1 for kw in weak_kw if kw in combined)
        if score >= 2:
            final.append((src_key, display_name, title, link, brief, score))

    # Sort by relevance score, keep top 25
    final.sort(key=lambda x: -x[5])
    final = final[:25]

    print(f"\n=== Collected {len(final)} relevant articles ===", flush=True)
    for i, (sk, dn, title, link, brief, score) in enumerate(final):
        print(f"{i}|{sk}|{dn}|{title}|{link}|{brief[:80]}|score={score}")

    # Also try getting more from additional searches
    # Use Bing Web Search fallback
    if len(final) < 20:
        print("\nNeed more articles, trying supplementary sources...", flush=True)
        more_sources = get_additional_sources()
        for sk, dn, title, link, brief, score in more_sources:
            if link not in seen_urls and len(final) < 25:
                all_keywords = ['server', 'bare metal', 'hardware', 'data center',
                               'cpu', 'gpu', 'rack', 'storage', 'infrastructure']
                combined = (title + ' ' + brief).lower()
                has_kw = any(kw in combined for kw in all_keywords)
                if has_kw:
                    final.append((sk, dn, title, link, brief, score))
                    seen_urls.add(link)

    return final


def get_additional_sources():
    """Try to get more articles from additional approaches."""
    results = []
    
    # Try Phoronix HTML scraping (their feed is behind Cloudflare)
    try:
        req = Request(
            'https://www.phoronix.com/',
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
        )
        resp = urlopen(req, timeout=15)
        page = resp.read().decode('utf-8', errors='replace')
        
        # Find article links
        articles = re.findall(r'class="article-title"[^>]*href="([^"]+)"[^>]*>([^<]+)<', page)
        hw_keywords = ['server', 'cpu', 'gpu', 'intel', 'amd', 'nvidia', 'linux', 'kernel', 'driver',
                       'hardware', 'pcie', 'ram', 'memory', 'storage', 'network', 'benchmark', 'performance']
        
        for link, title in articles[:10]:
            title = title.strip()
            if not link.startswith('http'):
                link = 'https://www.phoronix.com' + link
            combined = (title + ' hardware').lower()
            matches = sum(1 for kw in hw_keywords if kw in combined)
            if matches >= 2:
                results.append(('phoronix', 'Phoronix', title, link, '', matches))
                
        print(f"  Phoronix page scraped: found {len(results)} hardware-relevant articles", flush=True)
    except Exception as e:
        print(f"  Phoronix scraping failed: {e}", file=sys.stderr, flush=True)

    # Try Tom's Hardware news page
    try:
        req = Request(
            'https://www.tomshardware.com/news',
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
        )
        resp = urlopen(req, timeout=15)
        page = resp.read().decode('utf-8', errors='replace')
        
        titles_links = re.findall(r'<h3[^>]*>.*?<a[^>]*href="(/news/[^"]+)"[^>]*>([^<]+)</a>', page, re.DOTALL)
        th_keywords = ['server', 'cpu', 'gpu', 'intel', 'amd', 'nvidia', 'hardware',
                       'pcie', 'storage', 'ssd', 'memory', 'network', 'benchmark', 'gaming']
        
        for link, title in titles_links[:10]:
            title = title.strip()
            full_link = f'https://www.tomshardware.com{link}'
            combined = (title + ' tech').lower()
            matches = sum(1 for kw in th_keywords if kw in combined)
            if matches >= 2:
                results.append(("tom's hardware", "Tom's Hardware", title, full_link, '', matches))
                
        print(f"  Tom's Hardware scraped: found {len(results)} articles", flush=True)
    except Exception as e:
        print(f"  Tom's Hardware scraping failed: {e}", file=sys.stderr, flush=True)

    return results


if __name__ == '__main__':
    news = main()
    # Output as JSON for the creator script
    output = []
    for src_key, display_name, title, link, brief, score in news:
        output.append({
            'source_key': src_key,
            'display_name': display_name,
            'title': title,
            'url': link,
            'brief': brief,
            'relevance_score': score
        })
    with open('/tmp/news_baremetal.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved {len(output)} articles to /tmp/news_baremetal.json", flush=True)
