#!/usr/bin/env python3
"""Fetch Kubernetes security advisories from multiple sources and output as JSON."""
import json, re, html, urllib.request, urllib.error, ssl, time, sys
from datetime import datetime, timezone

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

all_advisories = []

def fetch(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=30)
            data = resp.read().decode('utf-8', errors='replace')
            return data
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2)
    return ""

def parse_hn_articles(html_text):
    """Parse The Hacker News for K8s-related articles."""
    items = []
    # Find article blocks
    articles = re.findall(r'<div class="story-body">(.*?)</div>', html_text, re.DOTALL)
    if not articles:
        articles = re.findall(r'<article[^>]*>(.*?)</article>', html_text, re.DOTALL)
    for art in articles[:20]:
        title_match = re.search(r'<h2[^>]*>.*?<a[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', art, re.DOTALL)
        if title_match:
            url = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
            if 'kubernetes' in title.lower() or 'k8s' in title.lower() or 'container' in title.lower() or 'docker' in title.lower() or 'cve' in title.lower() or 'kube' in title.lower():
                items.append({'title': title, 'url': url, 'source': 'The Hacker News'})
    # Fallback: search whole text
    if not items:
        links = re.findall(r'<a[^>]*href=["\'](https?://thehackernews\.com[^"\']+)["\'][^>]*>(.*?)</a>', html_text, re.DOTALL)
        for url, title_html in links:
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            if any(k in title.lower() for k in ['kubernetes', 'k8s', 'container', 'docker', 'cve', 'kube', 'rbac', 'admission', 'pod', 'cluster', 'secret', 'istio', 'cilium']):
                items.append({'title': title, 'url': url, 'source': 'The Hacker News'})
    return items[:8]

def parse_nvd_cves(html_text):
    """Parse NVD search results for K8s CVEs."""
    items = []
    cves = set()
    # Find CVE IDs
    for m in re.finditer(r'(CVE-\d{4}-\d{4,7})', html_text):
        cves.add(m.group(1))
    # Try to get details for each CVE
    for cve in list(cves)[:15]:
        cve_url = f"https://nvd.nist.gov/vuln/detail/{cve}"
        cve_html = fetch(cve_url)
        desc_match = re.search(r'<p[^>]*class="[^"]*detail-text[^"]*"[^>]*>(.*?)</p>', cve_html, re.DOTALL)
        desc = desc_match.group(1) if desc_match else "No description available"
        desc = re.sub(r'<[^>]+>', '', desc).strip()
        
        # CVSS 3.1 score
        cvss_match = re.search(r'<span[^>]*id="Cvss3NistScore"[^>]*>([\d.]+)</span>', cve_html)
        cvss = cvss_match.group(1) if cvss_match else "N/A"
        
        # Severity
        sev_match = re.search(r'<span[^>]*id="Cvss3NistSeverity"[^>]*>(\w+)</span>', cve_html)
        severity = sev_match.group(1) if sev_match else "N/A"
        
        if 'kubernetes' in desc.lower() or 'kube' in desc.lower():
            items.append({
                'title': cve,
                'url': cve_url,
                'description': desc[:300],
                'cvss': cvss,
                'severity': severity,
                'source': 'NVD'
            })
    return items

def parse_rss_feed(url, source_name):
    """Parse an RSS/Atom feed."""
    items = []
    data = fetch(url)
    entries = re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL)
    if not entries:
        entries = re.findall(r'<item>(.*?)</item>', data, re.DOTALL)
    for entry in entries[:15]:
        title_m = re.search(r'<title[^>]*>(.*?)</title>', entry, re.DOTALL)
        link_m = re.search(r'<link[^>]*href=["\']?(https?://[^"\'>\s]+)["\'>]', entry)
        if not link_m:
            link_m = re.search(r'<link>(https?://[^<]+)</link>', entry)
        title = title_m.group(1).strip() if title_m else ''
        link = link_m.group(1).strip() if link_m else ''
        if title:
            items.append({'title': title, 'url': link, 'source': source_name})
    return items

def search_github_advisories():
    """Search GitHub Advisory Database for K8s advisories."""
    items = []
    query = "kubernetes+type:reviewed+ecosystem:go"
    url = f"https://api.github.com/advisories?query={query}&per_page=15"
    try:
        req = urllib.request.Request(url, headers={**headers, 'Accept': 'application/vnd.github+json'})
        resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=30)
        data = json.loads(resp.read().decode())
        for adv in data[:15]:
            items.append({
                'title': adv.get('summary', adv.get('ghsa_id', 'Unknown')),
                'url': adv.get('html_url', adv.get('permalink', '')),
                'description': adv.get('description', '')[:300],
                'cvss': str(adv.get('severity', {}).get('score', 'N/A')),
                'severity': adv.get('severity', {}).get('severity', 'N/A'),
                'source': 'GitHub Advisory'
            })
    except Exception as e:
        print(f"  GitHub API error: {e}", file=sys.stderr)
    return items

def search_aqua_security():
    """Search Aqua Security blog for K8s security."""
    items = []
    url = "https://www.aquasec.com/blog/"
    data = fetch(url)
    articles = re.findall(r'<article[^>]*>(.*?)</article>', data, re.DOTALL)
    if not articles:
        articles = re.findall(r'<div[^>]*class="[^"]*blog-post[^"]*"[^>]*>(.*?)</div>', data, re.DOTALL)
    for art in articles[:15]:
        title_m = re.search(r'<h[2-4][^>]*>.*?<a[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', art, re.DOTALL)
        if title_m:
            url = title_m.group(1)
            title = re.sub(r'<[^>]+>', '', title_m.group(2)).strip()
            if any(k in (title + art).lower() for k in ['kubernetes', 'k8s', 'container security', 'cloud native', 'cve', 'kube', 'admission', 'rbac', 'supply chain']):
                items.append({'title': title, 'url': url, 'source': 'Aqua Security'})
    if not items:
        # Try search
        search_url = "https://www.aquasec.com/?s=kubernetes+security"
        data = fetch(search_url)
        links = re.findall(r'<a[^>]*href=["\'](https?://www\.aquasec\.com/[^"\']+?)["\'][^>]*>(.*?)</a>', data, re.DOTALL)
        for url, t in links[:10]:
            title = re.sub(r'<[^>]+>', '', t).strip()
            if any(k in title.lower() for k in ['kubernetes', 'k8s', 'cve', 'container']):
                items.append({'title': title, 'url': url, 'source': 'Aqua Security'})
    return items[:5]

def search_gitguardian():
    """Search GitGuardian for K8s secret泄漏."""
    items = []
    # Search their blog
    data = fetch("https://blog.gitguardian.com/search/?q=kubernetes+secret")
    articles = re.findall(r'<article[^>]*>(.*?)</article>', data, re.DOTALL)
    for art in articles[:10]:
        title_m = re.search(r'<h[2-4][^>]*>.*?<a[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', art, re.DOTALL)
        if title_m:
            url = title_m.group(1)
            title = re.sub(r'<[^>]+>', '', title_m.group(2)).strip()
            items.append({'title': title, 'url': url, 'source': 'GitGuardian'})
    return items[:3]

def search_cloudseclist():
    """Search CloudSecList archives."""
    data = fetch("https://cloudseclist.com/")
    items = []
    links = re.findall(r'<a[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', data, re.DOTALL)
    for url, t in links[:15]:
        title = re.sub(r'<[^>]+>', '', t).strip()
        if any(k in (title + url).lower() for k in ['kubernetes', 'k8s', 'cve', 'container', 'kube', 'cluster', 'pod', 'rbac']):
            items.append({'title': title, 'url': url, 'source': 'CloudSecList'})
    return items[:5]

def search_k8s_blog():
    """Search Kubernetes blog for security articles."""
    items = []
    data = fetch("https://kubernetes.io/blog/")
    articles = re.findall(r'<article[^>]*>(.*?)</article>', data, re.DOTALL)
    if not articles:
        articles = [data]
    for art in articles[:20]:
        links = re.findall(r'<a[^>]*href=["\'](https?://kubernetes\.io/blog/\d{4}/\d{2}/[^"\']+)["\'][^>]*>(.*?)</a>', art, re.DOTALL)
        for url, t in links:
            title = re.sub(r'<[^>]+>', '', t).strip()
            if any(k in (title + art).lower() for k in ['security', 'cve', 'vulnerability', 'advisory', 'fix', 'patch', 'rbac', 'secret', 'supply chain', 'sig']):
                items.append({'title': title, 'url': url, 'source': 'Kubernetes Blog'})
    return items[:5]

def search_cncf():
    """Search CNCF for security-related articles."""
    items = []
    data = fetch("https://www.cncf.io/blog/")
    articles = re.findall(r'<article[^>]*>(.*?)</article>', data, re.DOTALL)
    for art in articles[:15]:
        title_m = re.search(r'<h[2-4][^>]*>.*?<a[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', art, re.DOTALL)
        if title_m:
            url = title_m.group(1)
            title = re.sub(r'<[^>]+>', '', title_m.group(2)).strip()
            if any(k in (title + art).lower() for k in ['security', 'kubernetes', 'k8s', 'cve', 'supply chain', 'sbom', 'cluster']):
                items.append({'title': title, 'url': url, 'source': 'CNCF'})
    return items[:5]

# ========= MAIN =========
print("Fetching advisories...", file=sys.stderr)

# Source 1: Kubernetes Security Announce (Google Groups RSS)
print("  [1/6] Kubernetes Security Announce...", file=sys.stderr)
all_advisories.extend(parse_rss_feed(
    "https://groups.google.com/forum/feed/kubernetes-security-announce/msgs/rss.xml?num=15",
    "K8s Security Announce"
))

# Source 2: The Hacker News
print("  [2/6] The Hacker News...", file=sys.stderr)
hn_html = fetch("https://thehackernews.com/")
all_advisories.extend(parse_hn_articles(hn_html))

# Source 3: NVD
print("  [3/6] NVD CVE search...", file=sys.stderr)
nvd_html = fetch("https://nvd.nist.gov/vuln/search/results?query=kubernetes&results_type=overview&search_type=all&pub_start_date=2026-01-01&pub_end_date=2026-07-31")
try:
    all_advisories.extend(parse_nvd_cves(nvd_html))
except Exception as e:
    print(f"  NVD parse error: {e}", file=sys.stderr)

# Source 4: GitHub Advisory DB
print("  [4/6] GitHub Advisories...", file=sys.stderr)
try:
    all_advisories.extend(search_github_advisories())
except Exception as e:
    print(f"  GitHub error: {e}", file=sys.stderr)

# Source 5: Kubernetes Blog
print("  [5/6] Kubernetes Blog...", file=sys.stderr)
try:
    all_advisories.extend(search_k8s_blog())
except Exception as e:
    print(f"  K8s Blog error: {e}", file=sys.stderr)

# Source 6: Aqua Security + CNCF
print("  [6/6] Aqua Security & CNCF...", file=sys.stderr)
try:
    all_advisories.extend(search_aqua_security())
except Exception as e:
    print(f"  Aqua error: {e}", file=sys.stderr)
try:
    all_advisories.extend(search_cncf())
except Exception as e:
    print(f"  CNCF error: {e}", file=sys.stderr)

# Deduplicate by title
seen = set()
deduped = []
for adv in all_advisories:
    key = adv.get('title', '').lower().strip()[:80]
    if key and key not in seen:
        seen.add(key)
        deduped.append(adv)

print(json.dumps(deduped, indent=2))
