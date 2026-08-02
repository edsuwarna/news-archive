#!/usr/bin/env python3
"""Generate the Top 20 Bare-Metal Server News markdown report."""
import json, os
from datetime import datetime

def load_json(path):
    with open(path) as f:
        return json.load(f)

# Load extracted articles
top25 = load_json('/tmp/baremetal_top25.json')

# Filter duplicates (same URL)
seen = set()
unique = []
for item in top25:
    if item['url'] not in seen:
        seen.add(item['url'])
        unique.append(item)

# Filter for bare-metal/server/hardware/relevance >= 3 minimum, 
# plus any clearly server-related regardless of score
server_keywords = ['server', 'bare metal', 'data center', 'rack', 'infrastructure',
                   'nvidia', 'amd', 'intel', 'gpu', 'cpu', 'storage', 'hypervisor',
                   'virtualization', 'kvm', 'xilinx', 'epyc', 'xeon', 'cluster',
                   'compute', 'ai infrastructure', 'raid', 'ssd', 'pcie']

final = []
for item in unique:
    combined = (item['title'] + ' ' + item.get('brief','')).lower()
    score = item['score']
    match_count = sum(1 for kw in server_keywords if kw in combined)
    
    # Keep high-score or multi-match items
    if score >= 5 or match_count >= 3 or (score >= 2 and match_count >= 2):
        final.append(item)

# If still under 20, include items with ANY server keyword hit
if len(final) < 20:
    for item in unique:
        if item not in final:
            combined = (item['title'] + ' ' + item.get('brief','')).lower()
            match_count = sum(1 for kw in server_keywords if kw in combined)
            if match_count >= 2 and len(final) < 20:
                final.append(item)

# Sort by score descending, take top 20
final.sort(key=lambda x: -x['score'])
top20 = final[:20]

print(f"\nFinal Top 20 ({len(top20)} items):")
for i, item in enumerate(top20):
    print(f"  {i+1}. [{item['score']:2d}] {item['display_name']}")
    print(f"     {item['title']}")
    print(f"     → {item['url']}")
    brief = item.get('brief', '')
    if not brief:
        combined = (item['title']).lower()
        kw_server = ['bare metal', 'server', 'data center', 'infrastructure']
        kw_hw = ['nvidia', 'amd', 'intel', 'gpu', 'cpu', 'pcie', 'storage',
                 'hypervisor', 'virtualization', 'kvm', 'cluster', 'compute']
        hits = [f'{kw}→{combined}' for kw in kw_server + kw_hw if kw in combined]
        if hits:
            tags = ', '.join(h.split('→')[0] for h in hits[:5])
            brief = f"Covering {tags}."
    if brief and len(brief) > 100:
        brief = brief[:100] + '...'
    print(f"     Summary: {brief}")
    print()

# ============================================================
# WRITE MARKDOWN FILE
# ============================================================
date_str = datetime.now().strftime('%Y-%m-%d')
month_year = datetime.now().strftime('%B %d, %Y')
output_path = f'/home/ubuntu/projects-repo/news-archive/baremetal/{date_str}.md'

os.makedirs(os.path.dirname(output_path), exist_ok=True)

emoji_map = {'serve-the-home': '🖥️', 'phoronix': '🐧',
             'data-center-knowledge': '🏢', 'tomshardware': '💻'}

lines = []
lines.append(f'# Bare-Metal Server News — {month_year}')
lines.append('')

for i, item in enumerate(top20):
    idx = i + 1
    emoji = emoji_map.get(item['source_key'], '📰')
    title = item['title']
    url = item['url']
    display_name = item['display_name']
    
    # Generate summary from brief
    brief = item.get('brief', '')
    if not brief:
        combined = item['title'].lower()
        keywords_mentioned = []
        for kw in ['bare metal', 'server', 'data center', 'infrastructure',
                    'NVIDIA', 'AMD', 'Intel', 'GPU', 'CPU', 'PCIe', 'storage',
                    'hypervisor', 'virtualization', 'KVM', 'cluster', 'compute',
                    'SSD', 'AI']:
            if kw.lower() in combined:
                keywords_mentioned.append(kw)
        
        # Build a concise one-line summary
        if keywords_mentioned:
            brief = f"Covers {'/'.join(keywords_mentioned[:3])} topic."
        else:
            brief = f"Latest development on this hardware/platform topic."
    
    lines.append(f'## {idx}. {emoji} {title}')
    lines.append(f'**Summary:** {brief}')
    lines.append(f'**Source:** {display_name}(<{url}>)')
    lines.append('')

# Determine top themes
all_titles_lower = [item['title'].lower() for item in top20]
themes = []
theme_counts = {}

for theme_kw, theme_label in [
    ('nvidia gpu amd intel cpu xeons epyc', 'Next-Gen CPU/GPU Hardware & AI Accelerators'),
    ('linux kernel driver patch release', 'Linux Kernel & Driver Advancements'),
    ('server storage p ss raid nvme pcie gen', 'Storage & High-Speed Interconnect Innovation'),
    ('virtualization kvm hypervisor xen', 'Virtualization & Cloud Infrastructure'),
    ('benchmark review performance testing', 'Performance Benchmarking & Reviews'),
    ('network switch ethernet firewall router', 'Networking & Edge Infrastructure'),
    ('cooling power liquid thermal ai', 'AI Power & Thermal Infrastructure'),
]:
    count = sum(1 for t in all_titles_lower if any(kw in t for kw in theme_kw.split()))
    if count >= 2:
        themes.append((count, theme_label))

# Pick top 3 by count
themes.sort(key=lambda x: -x[0])
top_themes = themes[:3]

lines.append('## 📊 Summary Themes')
lines.append('')
for ti, (count, label) in enumerate(top_themes, 1):
    lines.append(f'{ti}. **{label}** — {count} articles covering this trend')
lines.append('')

markdown_content = '\n'.join(lines)

with open(output_path, 'w') as f:
    f.write(markdown_content)

print(f'\n✅ Written to: {output_path}')
print(f'   Size: {len(markdown_content)} chars, {len(lines)} lines')
print(f'   Themes: {[t[1] for t in top_themes]}')
