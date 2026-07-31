#!/usr/bin/env python3
"""Dump all NVD results sorted."""
import urllib.request, ssl, json, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0'}

req = urllib.request.Request(
    'https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=kubernetes&pubStartDate=2026-06-01T00:00:00.000&pubEndDate=2026-07-31T23:59:59.000&resultsPerPage=30',
    headers=hdr
)
data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
results = json.loads(data)

for vuln in results.get('vulnerabilities', []):
    cve = vuln.get('cve', {})
    id_ = cve.get('id', '')
    desc = ''
    for d in cve.get('descriptions', []):
        if d.get('lang') == 'en':
            desc = d.get('value', '')[:400]
            break
    metrics = cve.get('metrics', {})
    cvss_score = '?'
    cvss_sev = '?'
    for k in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
        if k in metrics and metrics[k]:
            cd = metrics[k][0].get('cvssData', {})
            cvss_score = str(cd.get('baseScore', '?'))
            cvss_sev = str(cd.get('baseSeverity', '?'))
            break
    pub_date = cve.get('published', '')[:10]
    print(f"ID: {id_}")
    print(f"CVSS: {cvss_score} | Severity: {cvss_sev} | Published: {pub_date}")
    print(f"Description: {desc}")
    print()
