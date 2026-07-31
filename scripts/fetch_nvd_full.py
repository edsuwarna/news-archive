#!/usr/bin/env python3
"""Comprehensive K8s NVDFetch with full CVSS + details."""
import urllib.request, ssl, json, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent': 'Mozilla/5.0'}

req = urllib.request.Request(
    'https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=kubernetes&pubStartDate=2026-01-01T00:00:00.000&pubEndDate=2026-07-31T23:59:59.000&resultsPerPage=30',
    headers=hdr
)
data = urllib.request.urlopen(req, context=ctx, timeout=30).read().decode()
results = json.loads(data)

output = []
for vuln in results.get('vulnerabilities', []):
    cve = vuln.get('cve', {})
    id_ = cve.get('id', '')
    desc = ''
    for d in cve.get('descriptions', []):
        if d.get('lang') == 'en':
            desc = d.get('value', '')[:500]
            break
    metrics = cve.get('metrics', {})
    cvss_score = 'N/A'
    cvss_sev = 'N/A'
    attack_vector = 'N/A'
    for k in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
        if k in metrics and metrics[k]:
            cd = metrics[k][0].get('cvssData', {})
            cvss_score = str(cd.get('baseScore', ''))
            cvss_sev = str(cd.get('baseSeverity', ''))
            attack_vector = str(cd.get('attackVector', 'N/A'))
            break
    pub_date = cve.get('published', '')[:10]
    
    # Get configurations (affected products)
    configs = cve.get('configurations', [])
    affected = ''
    for cfg in configs:
        for node in cfg.get('nodes', []):
            for match in node.get('cpeMatch', []):
                cpe = match.get('criteria', '')
                if 'kubernetes' in cpe.lower() or 'openshift' in cpe.lower():
                    affected = cpe
                    break
    
    output.append({
        'id': id_,
        'cvss': cvss_score,
        'severity': cvss_sev,
        'attackVector': attack_vector,
        'published': pub_date,
        'description': desc,
        'affected': affected
    })

print(json.dumps(output, indent=2))
