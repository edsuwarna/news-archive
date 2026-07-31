#!/usr/bin/env python3
"""Fetch Kubernetes security advisories - v2 with better source coverage."""
import urllib.request, ssl, json, re, sys, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

def fetch(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=hdr)
            resp = urllib.request.urlopen(req, context=ctx, timeout=30)
            return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            print(f"  [attempt {attempt+1}] {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2)
    return ""

results = []
seen = set()

# === 1. NVD API for Kubernetes CVEs 2026 ===
print("=== NVD API ===", file=sys.stderr)
data = fetch("https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=kubernetes&pubStartDate=2026-01-01T00:00:00.000&pubEndDate=2026-07-31T23:59:59.000&resultsPerPage=30")
if data:
    try:
        j = json.loads(data)
        for vuln in j.get('vulnerabilities', []):
            cve = vuln.get('cve', {})
            id_ = cve.get('id', '')
            desc = ''
            for d in cve.get('descriptions', []):
                if d.get('lang') == 'en':
                    desc = d.get('value', '')[:300]
                    break
            metrics = cve.get('metrics', {})
            cvss_score = ''
            cvss_sev = ''
            for k in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                if k in metrics and metrics[k]:
                    cvss_score = str(metrics[k][0].get('cvssData', {}).get('baseScore', ''))
                    cvss_sev = str(metrics[k][0].get('cvssData', {}).get('baseSeverity', ''))
                    break
            key = id_.lower()
            if key and key not in seen:
                seen.add(key)
                results.append({
                    'title': id_,
                    'url': f"https://nvd.nist.gov/vuln/detail/{id_}",
                    'description': desc,
                    'cvss': cvss_score,
                    'severity': cvss_sev,
                    'source': 'NVD'
                })
    except Exception as e:
        print(f"  NVD parse error: {e}", file=sys.stderr)
else:
    print("  NVD API returned nothing", file=sys.stderr)

# === 2. Kubernetes Security Announce (via groups.google.com) ===
print("=== K8s Security Announce ===", file=sys.stderr)
data = fetch("https://groups.google.com/g/kubernetes-security-announce")
if data:
    # Look for thread titles and links
    threads = re.findall(r'<a[^>]*href="([^"]*thread/[^"]*)"[^>]*>(.*?)</a>', data, re.DOTALL)
    for link, title_html in threads[:15]:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        full_url = link if link.startswith('http') else f'https://groups.google.com{link}'
        key = title.lower()[:60]
        if key and key not in seen:
            seen.add(key)
            results.append({'title': title, 'url': full_url, 'description': '', 'cvss': '', 'severity': '', 'source': 'K8s Security Announce'})

# === 3. Kubernetes Blog security articles ===
print("=== K8s Blog ===", file=sys.stderr)
data = fetch("https://kubernetes.io/blog/")
if data:
    links = re.findall(r'<a[^>]*href="(https?://kubernetes\.io/blog/\d{4}/\d{2}/[^"]+)"[^>]*>(.*?)</a>', data, re.DOTALL)
    for url, title_html in links:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        if any(k in (title + url).lower() for k in ['security', 'cve', 'vulnerability', 'advisory', 'patch', 'fix', 'rbac', 'secret', 'supply chain']):
            key = title.lower()[:60]
            if key and key not in seen:
                seen.add(key)
                results.append({'title': title, 'url': url, 'description': '', 'cvss': '', 'severity': '', 'source': 'Kubernetes Blog'})

# === 4. The Hacker News - search for K8s articles ===
print("=== The Hacker News ===", file=sys.stderr)
data = fetch("https://thehackernews.com/search/label/Kubernetes")
if not data or 'Kubernetes' not in data:
    data = fetch("https://thehackernews.com/")
if data:
    links = re.findall(r'<a[^>]*href="(https?://thehackernews\.com[^"]+)"[^>]*>(.*?)</a>', data, re.DOTALL)
    for url, title_html in links:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        if any(k in title.lower() for k in ['kubernetes', 'k8s', 'kube', 'container', 'docker', 'runc', 'containerd', 'cri-o', 'pod', 'cluster']):
            key = title.lower()[:60]
            if key and key not in seen:
                seen.add(key)
                results.append({'title': title, 'url': url, 'description': '', 'cvss': '', 'severity': '', 'source': 'The Hacker News'})

# === 5. Aqua Security Blog ===
print("=== Aqua Security ===", file=sys.stderr)
data = fetch("https://www.aquasec.com/blog/")
if data:
    links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', data, re.DOTALL)
    for url, title_html in links:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        if 'aquasec.com' in url and any(k in title.lower() for k in ['kubernetes', 'k8s', 'container', 'cve', 'cloud native', 'supply chain', 'admission', 'kube']):
            key = title.lower()[:60]
            if key and key not in seen:
                seen.add(key)
                results.append({'title': title, 'url': url, 'description': '', 'cvss': '', 'severity': '', 'source': 'Aqua Security'})

# === 6. CNCF Blog ===
print("=== CNCF ===", file=sys.stderr)
data = fetch("https://www.cncf.io/blog/")
if data:
    links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', data, re.DOTALL)
    for url, title_html in links:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        if 'cncf.io' in url and any(k in (title + url).lower() for k in ['security', 'kubernetes', 'k8s', 'cve', 'sbom', 'supply chain', 'cluster']):
            key = title.lower()[:60]
            if key and key not in seen:
                seen.add(key)
                results.append({'title': title, 'url': url, 'description': '', 'cvss': '', 'severity': '', 'source': 'CNCF'})

# === 7. GitHub Advisory DB for K8s ecosystem ===
print("=== GitHub Advisories ===", file=sys.stderr)
try:
    req = urllib.request.Request('https://api.github.com/advisories?ecosystem=go&keywords=kubernetes&per_page=20', headers={**hdr, 'Accept': 'application/vnd.github+json'})
    data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
    advisories = json.loads(data)
    if isinstance(advisories, list):
        for adv in advisories[:20]:
            title = adv.get('summary', adv.get('ghsa_id', ''))
            url = adv.get('html_url', adv.get('permalink', ''))
            desc = adv.get('description', '')[:300]
            severity_data = adv.get('severity', {})
            if isinstance(severity_data, dict):
                cvss = str(severity_data.get('score', ''))
                sev = str(severity_data.get('severity', ''))
            else:
                cvss = str(adv.get('cvss_score', ''))
                sev = str(severity_data)
            key = title.lower()[:60]
            if key and key not in seen:
                seen.add(key)
                results.append({'title': title, 'url': url, 'description': desc, 'cvss': cvss, 'severity': sev, 'source': 'GitHub Advisory'})
except Exception as e:
    print(f"  GitHub API error: {e}", file=sys.stderr)

# === Deduplicate by URL also ===
seen_urls = set()
final = []
for r in results:
    u = r.get('url', '').lower().strip()
    if u and u not in seen_urls:
        seen_urls.add(u)
        final.append(r)

print(json.dumps(final, indent=2))
