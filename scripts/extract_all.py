#!/usr/bin/env python3
"""Extract all articles from saved HTML dumps, score relevance, output Top 20."""
import re, html as h, json, os
from urllib.request import Request, urlopen
from datetime import datetime
from collections import Counter

def get_text(node_text):
    if not node_text: return ''
    t = re.sub(r'<[^>]+>', '', node_text)
    t = re.sub(r'\s+', ' ', t).strip()
    return h.unescape(t)

def score_article(title):
    combined = title.lower()
    strong = ['bare metal', 'server', 'data center', 'rack mount', 'infrastructure']
    medium = ['cpu', 'gpu', 'nvidia', 'amd', 'intel', 'xeon', 'storage', 'ssd',
             'pcie', 'memory', 'ram', 'network', 'switch', 'raid', 'blade',
             'cluster', 'compute', 'supermicro', 'dell', 'hp', 'lenovo',
             'hardware', 'benchmark', 'performance', 'linux kernel', 'arm server',
             'rdma', 'infiniband', 'nvme', 'tcp offload', 'virtualization',
             'hypervisor', 'kvm', 'proxmox', 'esxi', 'power supply', 'cooling']
    s = sum(1 for k in strong if k in combined) * 5
    m = sum(1 for k in medium if k in combined) * 2
    return max(s + m, 1)

# ============================================================
# PHORONIX - parse from /tmp/phor.html
# ============================================================
print("=== EXTRACTING PHORONIX ===")
with open('/tmp/phor.html') as f:
    phor_data = f.read()

phor_articles = []
date_pattern = r'<h([1-6])[^>]*>(.*?)</h[1-6]>'
dates = list(re.finditer(date_pattern, phor_data))

for di, d in enumerate(dates[:10]):
    idx_start = d.end()
    idx_end = dates[di+1].start() if di+1 < len(dates) else min(len(phor_data), idx_start + 8000)
    block = phor_data[idx_start:idx_end][:8000]
    
    link_pairs = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', block, re.DOTALL)
    for href, title_html in link_pairs:
        title = get_text(title_html)
        if not href.startswith('http'):
            href = 'https://www.phoronix.com' + href
        if len(title) > 15 and score_article(title) >= 2:
            phor_articles.append((href, title, score_article(title)))

phor_articles.sort(key=lambda x: -x[2])
print(f"  Got {len(phor_articles)} relevant articles")

# ============================================================
# DATA CENTER KNOWLEDGE - parse from /tmp/dck.html  
# ============================================================
print("\n=== EXTRACTING DATA CENTER KNOWLEDGE ===")
with open('/tmp/dck.html') as f:
    dck_data = f.read()

dck_articles = []
blocks = re.findall(r'<div[^>]*ContentPreview[^>]*>.*?</div>\s*</div>\s*</div>', dck_data, re.DOTALL | re.IGNORECASE)
print(f"  Found {len(blocks)} ContentPreview blocks")

for bi, block in enumerate(blocks[:80]):
    title_links = re.findall(
        r'class="VerticalCard-Title"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        block, re.DOTALL
    )
    for href, title_html in title_links:
        title = get_text(title_html)
        if not href.startswith('http'):
            href = 'https://www.datacenterknowledge.com' + href
        if len(title) > 15:
            sc = score_article(title)
            dck_articles.append((href, title, sc))

dck_articles.sort(key=lambda x: -x[2])
print(f"  Got {len(dck_articles)} relevant articles")

# ============================================================
# TOM'S HARDWARE - parse from /tmp/th.html
# ============================================================
print("\n=== EXTRACTING TOM'S HARDWARE ===")
with open('/tmp/th.html') as f:
    th_data = f.read()

th_articles = []
seen_th_titles = set()

news_href_blocks = re.findall(
    r'<a[^>]*href="(https?://www\.tomshardware\.com/news/[^\"]+)"[^>]*>(.*?)</a>',
    th_data, re.DOTALL | re.IGNORECASE
)

for href, title_html in news_href_blocks:
    title = get_text(title_html)
    if len(title) > 15 and title not in seen_th_titles:
        seen_th_titles.add(title)
        sc = score_article(title)
        if sc >= 2:
            th_articles.append((href, title, sc))

if len(th_articles) < 5:
    article_divs = re.findall(r'<article[^>]*>.*?</article>', th_data, re.DOTALL | re.IGNORECASE)
    print(f"  Also checking {len(article_divs)} article blocks...")
    for ad in article_divs[:15]:
        href_m = re.search(r'href="(https?://www\.tomshardware\.com/news/[^\"]*)"', ad)
        title_m = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]', ad, re.DOTALL)
        if href_m and title_m:
            href = href_m.group(1)
            title = get_text(title_m.group(1))
            if title and len(title) > 15 and title not in seen_th_titles:
                seen_th_titles.add(title)
                sc = score_article(title)
                if sc >= 2:
                    th_articles.append((href, title, sc))

th_articles.sort(key=lambda x: -x[2])
print(f"  Got {len(th_articles)} relevant articles")

# ============================================================
# SERVE-THE-HOME (from feed)
# ============================================================
print("\n=== EXTRACTION COMPLETE ===")
all_news = []

sth_articles = [
    ('serve-the-home', 'ServeTheHome', 
     'ASRock Rack 4U16X-GNR2 NVIDIA HGX B300 8-GPU Server Review',
     'https://www.servethehome.com/asrock-rack-4u16x-gnr2-nvidia-hgx-b300-8-gpu-server-intel-zutacore-review/',
     'Review of the ASRock Rack 4U16X-GNR2, an 8x NVIDIA HGX B300 server with enormous network bandwidth and liquid-cooling options.',
     9),
    ('serve-the-home', 'ServeTheHome',
     'Kioxia CM10 Series Launched for the PCIe Gen6 Generation of SSDs',
     'https://www.servethehome.com/kioxia-cm10-series-launched-for-the-pcie-gen6-generation-of-ssds/',
     'The new Kioxia CM10 series spans 2.5" and EDSFF form factors, PCIe Gen5 and Gen6, air-cooled and liquid-cooled.',
     7),
    ('serve-the-home', 'ServeTheHome',
     'PCIe Gen6 and Gen5 Will Both Matter for AI Storage',
     'https://www.servethehome.com/pcie-gen6-and-gen5-will-both-matter-for-ai-storage/',
     'Analysis of why both PCIe Gen5 and PCIe Gen6 will matter for AI storage as the industry builds at incredible pace.',
     7),
    ('serve-the-home', 'ServeTheHome',
     "AMD's Physical AI Plans Come Into Focus as Company Launches Ryzen Embedded AI X100",
     'https://www.servethehome.com/amds-physical-ai-plans-come-into-focus-as-company-launches-ryzen-embedded-ai-x100/',
     'At Advancing AI 2026, AMD laid out plans for comprehensive physical AI hardware product stack from SoCs to modules.',
     7),
    ('serve-the-home', 'ServeTheHome',
     'Dell VEP4600 Review The System I Have Lusted After for Years',
     'https://www.servethehome.com/dell-vep4600-review-the-system-i-have-lusted-after-for-years/',
     'Low-cost Dell VEP4600 platform review - a 1GbE/10GbE network appliance taken for a spin.',
     5),
    ('serve-the-home', 'ServeTheHome',
     'Omada Fusion Gateway 2.5G Ecosystem and Software Overview',
     'https://www.servethehome.com/omada-fusion-gateway-2-5gbe-ecosystem-and-software-overview/',
     'Checkout of Omada Fusion Gateway 2.5G ecosystem including PoE+ switch and Wi-Fi 7 BE1100 APs.',
     4),
]

for src_key, display, title, link, brief, score in sth_articles:
    all_news.append({
        'source_key': src_key,
        'display_name': display,
        'title': title,
        'url': link,
        'brief': brief,
        'score': score,
        'source_type': 'feed'
    })

for link, title, score in phor_articles[:12]:
    all_news.append({
        'source_key': 'phoronix',
        'display_name': 'Phoronix',
        'title': title,
        'url': link,
        'brief': '',
        'score': score,
        'source_type': 'scrape'
    })

for link, title, score in dck_articles[:12]:
    all_news.append({
        'source_key': 'data-center-knowledge',
        'display_name': 'Data Center Knowledge',
        'title': title,
        'url': link,
        'brief': '',
        'score': score,
        'source_type': 'scrape'
    })

for link, title, score in th_articles[:12]:
    all_news.append({
        'source_key': 'tomshardware',
        'display_name': "Tom's Hardware",
        'title': title,
        'url': link,
        'brief': '',
        'score': score,
        'source_type': 'scrape'
    })

all_news.sort(key=lambda x: -x['score'])
top25 = all_news[:25]

print(f"\n{'='*70}")
print(f"TOTAL COLLECTED: {len(all_news)} | TOP {min(25, len(top25))}")
print(f"{'='*70}")

for i, item in enumerate(top25):
    icon_map = {'serve-the-home': ':desktop:', 'phoronix': ':penguin:', 
                'data-center-knowledge': ':office:', 'tomshardware': ':laptop:'}
    icon = icon_map.get(item['source_key'], ':newspaper:')
    print(f"{i+1:2d}. [{item['score']:2d}] {icon} {item['display_name']}")
    print(f"    {item['title']}")
    print(f"    {item['url']}")
    if item['brief']:
        print(f"    Summary: {item['brief'][:120]}")
    print()

os.makedirs('/tmp', exist_ok=True)
with open('/tmp/baremetal_top25.json', 'w') as f:
    json.dump(top25, f, indent=2)
print(f"Saved to /tmp/baremetal_top25.json")

src_counts = Counter(n['display_name'] for n in top25)
print(f"\nSource distribution:")
for src, count in src_counts.most_common():
    print(f"  {src}: {count}")
