#!/usr/bin/env python3
"""Fetch NVD CVEs for Kubernetes and output structured data."""
import urllib.request, ssl, json, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

req = urllib.request.Request('https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=kubernetes&pubStartDate=2026-01-01T00:00:00.000&pubEndDate=2026-07-31T23:59:59.000&resultsPerPage=25', headers=hdr)
data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
results = json.loads(data)

print(f"TotalResults: {results.get('totalResults', 0)}")
for vuln in results.get('vulnerabilities', []):
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
    pub_date = cve.get('published', '')[:10]
    print(f"{id_} | CVSS:{cvss_score} ({cvss_sev}) | Published:{pub_date}")
    print(f"  DESC: {desc}")
    print()
