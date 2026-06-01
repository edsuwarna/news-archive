# Kubernetes Security Briefing — June 1, 2026

---

## 🔴 Latest CVEs

### CVE-2026-4342 — ingress-nginx Comment-Based Nginx Configuration Injection
- **Date:** Mar 20, 2026
- **Severity:** 🟡 HIGH (CVSS 8.8)
- **Component:** ingress-nginx
- **Description:** Combination of Ingress annotations can be used to inject configuration into nginx, leading to arbitrary code execution in the ingress-nginx controller and disclosure of Secrets accessible cluster-wide.
- **Affected:** ingress-nginx < v1.13.9, < v1.14.5, < v1.15.1
- **Fixed in:** v1.13.9, v1.14.5, v1.15.1
- **Reported by:** wooseokdotkim
- **GitHub:** https://github.com/kubernetes/kubernetes/issues/137893

### CVE-2026-3288 — ingress-nginx Rewrite-Target Nginx Configuration Injection
- **Date:** Mar 10, 2026
- **Severity:** 🟡 HIGH (CVSS 8.8)
- **Component:** ingress-nginx
- **Description:** The `nginx.ingress.kubernetes.io/rewrite-target` annotation can be used to inject configuration into nginx, leading to arbitrary code execution and Secret disclosure.
- **Affected:** ingress-nginx < 1.13.8, < 1.14.4, < 1.15.0
- **Fixed in:** 1.13.8, 1.14.4, 1.15.0
- **Reported by:** Kai Aizen
- **GitHub:** https://github.com/kubernetes/kubernetes/issues/137560

### Multiple ingress-nginx CVEs (CVE-2026-1580, CVE-2026-24512, CVE-2026-24513, CVE-2026-24514)
- **Date:** Feb 2, 2026
- **Severity:** 🟡 HIGH (CVSS up to 8.8)
- **Component:** ingress-nginx
- **Description:** Multiple issues disclosed simultaneously in ingress-nginx. The most serious can result in arbitrary code execution in the ingress-nginx controller.
- **Affected:** ingress-nginx < v1.13.7, < v1.14.3
- **Fixed in:** v1.13.7, v1.14.3
- **GitHub:** Individual issues per CVE (see links in advisory)

### CVE-2026-3865 — CSI Driver for SMB Path Traversal via subDir
- **Date:** Apr 11, 2026
- **Severity:** 🟡 Medium (CVSS 6.5)
- **Component:** CSI Driver for SMB (`smb.csi.k8s.io`)
- **Description:** Insufficient validation of the subDir parameter allows path traversal. An attacker with PersistentVolume create privileges can craft a volumeHandle with `../` sequences to delete/modify directories outside the intended subdirectory on the SMB server.
- **Affected:** All versions prior to v1.20.1
- **Fixed in:** v1.20.1
- **Reported by:** @Shaul Ben Hai, SentinelOne
- **GitHub:** https://github.com/kubernetes/kubernetes/issues/138319

### CVE-2026-3864 — CSI Driver for NFS Path Traversal via subDir
- **Date:** Mar 17, 2026
- **Severity:** 🟡 Medium (CVSS 6.5)
- **Component:** CSI Driver for NFS (`nfs.csi.k8s.io`)
- **Description:** Identical vulnerability pattern to CVE-2026-3865 but affecting the NFS CSI driver. Path traversal via subDir parameter allows unintended directory deletion/modification on the NFS server.
- **Affected:** All versions prior to v4.13.1
- **Fixed in:** v4.13.1
- **Reported by:** @Shaul Ben Hai, SentinelOne
- **GitHub:** https://github.com/kubernetes/kubernetes/issues/137797

---

## 🔴 Security News

### GitHub Breached via Employee Device — 3,800+ Internal Repos Exfiltrated (May 20)
Threat actor TeamPCP listed GitHub's source code (≈4,000 internal repos) for sale at $50,000 on a cybercrime forum. The breach originated from an employee device compromise. GitHub stated no customer data was impacted but is monitoring for follow-on activity.

### PCPJack Credential Stealer Exploits 5 CVEs, Spreads Worm-Like Across Cloud (May 7)
SentinelOne disclosed PCPJack, a credential theft framework targeting exposed cloud infrastructure: Docker, Kubernetes, Redis, MongoDB, RayML, and web apps. It spreads worm-like, harvesting credentials from cloud, container, developer, and financial services, exfiltrating via attacker-controlled infrastructure.

### Docker CVE-2026-34040 — AuthZ Bypass (CVSS 8.8) (Apr 7)
A high-severity bypass of Docker authorization plugins stemming from an incomplete fix for CVE-2024-41110. Attackers can craft API requests that bypass AuthZ plugins by omitting the request body. Impacts anyone relying on body-introspecting authorization plugins.

### TeamPCP Backdoors LiteLLM via Trivy CI/CD Compromise (Mar 24)
Malicious LiteLLM versions 1.82.7–1.82.8 pushed to PyPI containing a 3-stage payload: credential harvester (SSH keys, cloud creds, K8s secrets, crypto wallets), K8s lateral movement toolkit (deploys privileged pods to every node), and a persistent systemd backdoor.

### TeamPCP Hacks Checkmarx GitHub Actions Using Stolen CI Credentials (Mar 24)
Two Checkmarx GitHub Actions (`ast-github-action`, `kics-github-action`) compromised using credentials stolen from the Trivy breach. Tracked as CVE-2026-33634 (CVSS 9.4).

### Trivy Supply Chain Attack — Worm and K8s Wiper (Mar 23)
Malicious Trivy Docker Hub images (v0.69.4–0.69.6) distributed containing TeamPCP infostealer. The attack used stolen CI credentials and spread via Docker Hub with worm-like behavior targeting K8s environments.

### UNC4899 (North Korea) Breaches Crypto Firm via AirDropped Trojan (Mar 9)
State-sponsored actor compromised a crypto firm by exploiting developer's personal-to-corporate device file transfer (AirDrop). Pivoted to cloud environments using LOTC techniques, abused DevOps workflows to harvest credentials, break out of containers, and tamper with Cloud SQL databases.

### TeamPCP Worm Exploits Cloud Infrastructure (Feb 9)
Massive worm-driven campaign targeting exposed Docker APIs, K8s clusters, Ray dashboards, and Redis servers. Leveraged React2Shell (CVE-2025-55182, CVSS 10.0). Active since at least Nov 2025, with 700+ Telegram members publishing stolen data.

### Fluent Bit Flaws — RCE and Cloud Infrastructure Takeover (Nov 2025)
Five vulnerabilities disclosed in Fluent Bit (telemetry agent) allowing authentication bypass, path traversal, RCE, DoS, and tag manipulation. Could be chained to compromise cloud/K8s infrastructure.

### LinkPro Linux Rootkit Uses eBPF, Deployed via K8s Clusters (Oct 2025)
New rootkit discovered by Synacktiv using eBPF modules for concealment and magic-packet activation. Deployed via malicious Docker Hub image on exposed Jenkins servers (CVE-2024-23897), then onto K8s clusters.

### Chaos Mesh Critical GraphQL Flaws — Full K8s Cluster Takeover (Sep 2025)
"Chaotic Deputy" vulnerabilities (CVE-2025-59358, CVSS 7.5) in Chaos Mesh allow attackers with minimal in-cluster network access to execute fault injections, steal service account tokens, and take over K8s clusters.

---

## 🔴 Trends & Analysis

1. **TeamPCP Dominance:** The threat actor TeamPCP (DeadCatx3/PCPcat) has been the most active K8s/cloud threat group in 2026, executing supply chain attacks (Trivy, LiteLLM, Checkmarx) and worm-like proliferation across exposed cloud services.

2. **Supply Chain CI/CD Pipeline Attacks:** The dominant attack vector in 2026 is compromising CI/CD credentials to push malicious artifacts to registries (Docker Hub, PyPI) and GitHub Actions. The Trivy compromise cascaded through multiple downstream projects.

3. **ingress-nginx as Repeat Target:** Since Feb 2026, 7+ CVEs have been disclosed in ingress-nginx, all HIGH severity (CVSS 8.8), all involving annotation-based nginx configuration injection leading to RCE and cluster-wide Secret disclosure.

4. **CSI Driver Supply Chain:** Two path traversal CVEs (CVE-2026-3865 for SMB, CVE-2026-3864 for NFS) reported by SentinelOne highlight the attack surface in storage drivers. Both allow directory deletion/modification on storage servers.

5. **State-Sponsored Cloud Compromises:** UNC4899 (North Korea) continues to target crypto firms through social engineering + cloud pivot, using DevOps workflows for credential harvesting and container breakout.

6. **Runtime Security & eBPF Threats:** The LinkPro rootkit demonstrates advanced evasion via eBPF, deployed through container escape vectors into K8s clusters.

---

*Generated by Hermes Agent K8s Security News Cron — Sources: K8s Security Announcements, The Hacker News, Aqua Security Blog*
