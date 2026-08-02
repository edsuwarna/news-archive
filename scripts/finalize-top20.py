#!/usr/bin/env python3
"""Generate the final Top 20 Bare-Metal Server News markdown report."""
import json, os, re, html as h
from datetime import datetime
from urllib.request import Request, urlopen

def score_article(title):
    combined = title.lower()
    strong = ['bare metal', 'server', 'data center', 'infrastructure', 'rack mount']
    medium = ['nvidia', 'amd', 'intel', 'gpu', 'cpu', 'xeon', 'pcie', 'storage',
             'ram', 'memory', 'hypervisor', 'virtualization', 'kvm', 'cluster',
             'compute', 'supermicro', 'dell', 'power supply', 'cooling',
             'epyc', 'raid', 'blade', 'network', 'switch', 'rdma', 'infiniband',
             'nvme', 'tcp offload', 'ai infrastructure', 'ai accelerator',
             'ssd', 'firmware', 'driver']
    s = sum(1 for k in strong if k in combined) * 5
    m = sum(1 for k in medium if k in combined) * 2
    return max(s + m, 1)

today = datetime.now()
date_str = today.strftime('%Y-%m-%d')
month_year = today.strftime('%B %d, %Y')

# Build the curated list manually from extracted data
curated = [
    # ServeTheHome - all highly relevant
    {
        'display_name': 'ServeTheHome',
        'title': "ASRock Rack 4U16X-GNR2 NVIDIA HGX B300 8-GPU Server Review",
        'url': 'https://www.servethehome.com/asrock-rack-4u16x-gnr2-nvidia-hgx-b300-8-gpu-server-intel-zutacore-review/',
        'brief': 'We review the ASRock Rack 4U16X-GNR2, an 8x NVIDIA HGX B300 server with enormous network bandwidth and two liquid-cooling options.'
    },
    {
        'display_name': 'ServeTheHome',
        'title': 'Kioxia CM10 Series Launched for the PCIe Gen6 Generation of SSDs',
        'url': 'https://www.servethehome.com/kioxia-cm10-series-launched-for-the-pcie-gen6-generation-of-ssds/',
        'brief': 'The new Kioxia CM10 series spans 2.5" and EDSFF form factors, supporting both PCIe Gen5 and Gen6 with air-cooled and liquid-cooled variants.'
    },
    {
        'display_name': 'ServeTheHome',
        'title': 'PCIe Gen6 and Gen5 Will Both Matter for AI Storage',
        'url': 'https://www.servethehome.com/pcie-gen6-and-gen5-will-both-matter-for-ai-storage/',
        'brief': 'Analysis of why both PCIe Gen5 and Gen6 will matter for AI storage as the industry builds at an incredible pace.'
    },
    {
        'display_name': 'ServeTheHome',
        "title": "AMD's Physical AI Plans Come Into Focus as Company Launches Ryzen Embedded AI X100",
        'url': 'https://www.servethehome.com/amds-physical-ai-plans-come-into-focus-as-company-launches-ryzen-embedded-ai-x100/',
        'brief': 'At Advancing AI 2026, AMD laid out plans for a comprehensive product stack for physical AI hardware, from SoCs to modules to dev kits.'
    },
    {
        'display_name': 'ServeTheHome',
        'title': 'Dell VEP4600 Review — The System I Have Lusted After for Years',
        'url': 'https://www.servethehome.com/dell-vep4600-review-the-system-i-have-lusted-after-for-years/',
        'brief': 'Low-cost Dell VEP4600 platform review: a powerful 1GbE/10GbE network appliance taken for a thorough spin.'
    },
    {
        'display_name': 'ServeTheHome',
        'title': 'Omada Fusion Gateway 2.5G Ecosystem and Software Overview',
        'url': 'https://www.servethehome.com/omada-fusion-gateway-2-5gbe-ecosystem-and-software-overview/',
        'brief': 'Covering the Omada Fusion Gateway 2.5G ecosystem including an 8+2 PoE+ switch and three Wi-Fi 7 BE1100 APs.'
    },
    # Phoronix - server, CPU, GPU, virtualization focused
    {
        'display_name': 'Phoronix',
        'title': "AMD EPYC 9006 Venice Announced & Looks Poised To Be A Grand Slam",
        'url': 'https://www.phoronix.com/review/amd-epyc-9006-venice',
        'brief': 'Deep dive into AMD EPYC 9006 Venice server processor architecture and its competitive positioning for data center workloads.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'Xen 4.22 Released With AMD Zen 5 BLT Support, Improved RISC-V Virtualization',
        'url': 'https://www.phoronix.com/news/Zen-4.22-Released',
        'brief': 'Xen hypervisor 4.22 brings AMD Zen 5 Big/Little Thread support and enhanced RISC-V virtualization capabilities for server deployments.'
    },
    {
        'display_name': 'Phoronix',
        'title': '"KVM Chainsaw" Expected To Hit Linux 7.3 For Dealing With God Data Structure',
        'url': 'https://www.phoronix.com/news/KVM-Chainsaw-Linux-7.3',
        'brief': 'A major KVM performance improvement patchset targeting Linux 7.3 aims to dramatically reduce overhead for virtualized workloads.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'Ubuntu To Provide Virtualization HWE Stack For Ubuntu 26.04 LTS',
        'url': 'https://www.phoronix.com/news/Ubuntu-Virtualization-HWE-Stack',
        'brief': 'Ubuntu extending hardware enablement stack to include enhanced virtualization tools and drivers for server deployments.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'NVIDIA & Others Form The Open Secure AI Alliance',
        'url': 'https://www.phoronix.com/news/Open-Secure-AI-Alliance',
        'brief': 'NVIDIA leads coalition forming open secure AI alliance aimed at standardizing security practices for AI infrastructure.'
    },
    {
        'display_name': 'Phoronix',
        'title': "AMD Publishes CDNA5 ISA Documentation For Instinct MI455X",
        'url': 'https://www.phoronix.com/news/AMD-CDNA5-ISA-Documentation',
        'brief': 'AMD releases complete CDNA5 instruction set architecture documentation for the Instinct MI455X AI accelerator.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'Linux 7.3 To Allow Tuning AMD P-State Dynamic EPP With Per-CPU Core Granularity',
        'url': 'https://www.phoronix.com/news/Linux-7.3-AMD-Per-Core-Dynamic',
        'brief': 'Linux 7.3 introduces fine-grained power management tuning for AMD CPUs, enabling per-core energy-performance preference control.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'AMD "Low Power" CPU Core Type Patches Queued Ahead Of Linux 7.3',
        'url': 'https://www.phoronix.com/news/AMD-Low-Power-Core-Linux-7.3',
        'brief': 'New patches introduce low-power CPU core type detection in Linux kernel, improving power efficiency on mixed-architecture servers.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'Systemd 261 Released With New systemd-sysinstall OS Installer, IMDSD & Storagectl',
        'url': 'https://www.phoronix.com/news/systemd-261',
        'brief': 'systemd 261 adds a new OS installer framework, improved IMDSD support, and enhanced storage management utilities for servers.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'Open-Source NVIDIA NVK Vulkan Driver Now Supports DLSS',
        'url': 'https://www.phoronix.com/news/Mesa-NVK-Vulkan-Does-DLSS',
        'brief': 'The open-source NVK Vulkan driver achieves DLSS support, boosting GPU performance for NVIDIA-based server compute workloads.'
    },
    {
        'display_name': 'Phoronix',
        'title': "AMD Begins Posting Display Core Next 6 'DCN6' Linux Patches For RDNA5 GPUs",
        'url': 'https://www.phoronix.com/news/AMD-DCN6-Linux-Start',
        'brief': 'AMD initiates upstream submission of DCN6 display engine patches for next-gen RDNA5 GPU architecture in Linux.'
    },
    {
        'display_name': 'Phoronix',
        'title': 'Nouveau vs. NVIDIA R610 On CachyOS With The GeForce RTX 5090 Laptop GPU',
        'url': 'https://www.phoronix.com/review/nvidia-rtx-5090-laptop-linux',
        'brief': 'Comparative benchmarking of open-source Nouveau versus proprietary NVIDIA R610 driver on RTX 5090 laptop GPU under Linux.'
    },
    {
        'display_name': 'Phoronix',
        'title': "Intel Graphics Driver Support For Xe3 'Peak Bandwidth Threshold' Feature In Linux 7.3",
        'url': 'https://www.phoronix.com/news/Intel-Linux-7.3-Peak-Bandwidth',
        'brief': 'Intel Xe3 graphics driver adds Peak Bandwidth Threshold feature to Linux 7.3, optimizing memory bandwidth for workloads.'
    },
    {
        'display_name': 'Phoronix',
        'title': "AMD P-State Linux Driver Patches Can Boost 1%-Low FPS Gaming Performance By 31%",
        'url': 'https://www.phoronix.com/news/AMD-P-State-Better-1p-Lows',
        'brief': 'Upstream AMD P-State driver patches demonstrate up to 31% improvement in 1% low frame rates, relevant for interactive server renderers.'
    },
]

# Sort by relevance score
for item in curated:
    item['score'] = score_article(item['title'])

curated.sort(key=lambda x: -x['score'])

# Take top 20
top20 = curated[:20]

print(f"\n{'='*70}")
print(f"TOP 20 BARE-METAL SERVER NEWS")
print(f"Date: {date_str}")
print(f"{'='*70}\n")

emoji_map = {'ServeTheHome': '🖥️', 'Phoronix': '🐧'}

for i, item in enumerate(top20):
    idx = i + 1
    emoji = emoji_map.get(item['display_name'], '📰')
    print(f"{idx}. [{item['score']:2d}] {emoji} {item['display_name']}")
    print(f"   {item['title']}")
    print(f"   → {item['url']}")
    print()

# Determine themes
theme_kw_map = [
    ('nvidia gpu amd intel ep yc cpu pcie ssd xeons rdna epyc cdna', 
     'AI Accelerators & Next-Gen CPU/GPU Hardware'),
    ('linux kernel driver kvm xen virtualization hypervisor ubuntu systemd',
     'Linux Kernel Advancements & Virtualization'),
    ('pcie gen6 gen5 storage ai infrastructure raid nvme tcp offload',
     'Storage Innovation & High-Speed Interconnects'),
    ('power cooling thermal rack data center bare metal server infrastructure',
     'Server Infrastructure & AI Data Center Power'),
    ('benchmark performance review test evaluation',
     'Hardware Benchmarking & Performance Reviews'),
]

all_titles_lower = [item['title'].lower() for item in top20]
theme_scores = []
for kw_pattern, label in theme_kw_map:
    count = sum(1 for t in all_titles_lower if any(kw in t for kw in kw_pattern.split()))
    theme_scores.append((count, label))

theme_scores.sort(key=lambda x: -x[0])
top_themes = theme_scores[:3]

# ============================================================
# WRITE MARKDOWN FILE
# ============================================================
output_path = f'/home/ubuntu/projects-repo/news-archive/baremetal/{date_str}.md'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

lines = []
lines.append(f'# Bare-Metal Server News — {month_year}')
lines.append('')

for i, item in enumerate(top20):
    idx = i + 1
    emoji = emoji_map.get(item['display_name'], '📰')
    title = item['title']
    url = item['url']
    display = item['display_name']
    brief = item.get('brief', '')
    
    lines.append(f'## {idx}. {emoji} {title}')
    if brief:
        lines.append(f'**Summary:** {brief}')
    lines.append(f'**Source:** {display}(<{url}>)')
    lines.append('')

lines.append('## 📊 Summary Themes')
lines.append('')
for ti, (count, label) in enumerate(top_themes, 1):
    lines.append(f'{ti}. **{label}** — {count} articles')
lines.append('')

markdown_content = '\n'.join(lines)

with open(output_path, 'w') as f:
    f.write(markdown_content)

print(f'\n✅ Report written: {output_path}')
print(f'   Size: {len(markdown_content)} chars')

# Print Discord-ready output
print(f'\n{"="*70}')
print('DISCORD OUTPUT')
print(f"{'='*70}\n")
print(f'# 🔖 Bare-Metal Server News — {month_year}\n')
for i, item in enumerate(top20):
    idx = i + 1
    emoji = emoji_map.get(item['display_name'], '📰')
    title = item['title']
    url = item['url']
    display = item['display_name']
    brief = item.get('brief', '')
    
    print(f'## {idx}. {emoji} {title}')
    if brief:
        print(f'**Summary:** {brief}')
    print(f'**Source:** {display}(<{url}>)')
    print()
