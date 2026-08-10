# Kubernetes & Cloud Security Digest — 10 Aug 2026

**1.** CVE-2025-55182 — React2Shell: Critical RCE in React Server Components Flight Protocol | CVSS:10.0 | Severity:Critical (<https://nvd.nist.gov/vuln/detail/CVE-2025-55182>)
**2.** CVE-2026-9198 — IBM Langflow OSS Unauthenticated RCE via auto_login/SUPERUSER token chain | CVSS:9.8 | Severity:Critical (<https://nvd.nist.gov/vuln/detail/CVE-2026-9198>)
**3.** CVE-2026-64564 — SCTPhantom: 18-Year-Old Linux Kernel SCTP ASCONF UAF Enables Root Privilege Escalation & Container Escape | CVSS:9.8 | Severity:Critical (<https://nvd.nist.gov/vuln/detail/CVE-2026-64564>)
**4.** CVE-2025-1974 — IngressNightmare: Kubernetes Ingress NGINX Unauthenticated Remote Code Execution | CVSS:9.8 | Severity:Critical (<https://nvd.nist.gov/vuln/detail/CVE-2025-1974>)
**5.** CVE-2025-65719 — Kubectl MCP Server: Critical RCE from Single Webpage Visit Enables Cluster Takeover | CVSS:9.5 | Severity:Critical (<https://nvd.nist.gov/vuln/detail/CVE-2025-65719>)
**6.** CVE-2026-53359 — Januscape: 16-Year-Old KVM/x86 Shadow Paging UAF Guest-to-Host VM Escape | CVSS:8.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-53359>)
**7.** CVE-2026-64561 — Zapscape: KVM/x86 MMU Flaw Allows Nested L1 Guest Host Escape to Root | CVSS:8.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-64561>)
**8.** CVE-2026-34040 — Docker/Moby Engine Authorization Plugin Bypass via Oversized Request Body (>1MB Silences AuthZ Checks) | CVSS:8.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-34040>)
**9.** CVE-2026-43503 — DirtyClone: Linux Kernel skbuff Cloned Network Packet Local Privilege Escalation to Root | CVSS:8.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-43503>)
**10.** CVE-2026-43500 — Dirty Frag: Linux Kernel Shared Page Fragment Flag Loss via UDP Splicing Causes LPE | CVSS:7.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-43500>)
**11.** CVE-2026-43284 — Dirty Frag (ESP Variant): Linux Kernel XFRM ESP In-Place Decrypt on Shared SKB Frags | CVSS:7.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-43284>)
**12.** CVE-2026-46300 — Fragnesia: Linux Kernel ESP-in-TCP Subsystem Container Breakout & LPE | CVSS:7.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-46300>)
**13.** CVE-2026-31431 — Copy Fail: Linux Kernel AF_ALG AEAD Page Cache Corruption Enables Stealthy Root Escalation & Container Escape | CVSS:7.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-31431>)
**14.** CVE-2025-21756 — Attack of the Vsock: Linux Kernel Virtual Socket Use-After-Free Enables Container Escape | CVSS:7.8 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2025-21756>)
**15.** CVE-2025-14847 — MongoBleed: Unauthenticated Memory Disclosure in MongoDB Zlib Compressed Protocol Headers | CVSS:7.5 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2025-14847>)
**16.** CVE-2026-34486 — Apache Tomcat EncryptInterceptor Bypass: Missing Encryption of Sensitive Data (CISA KEV) | CVSS:7.5 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2026-34486>)
**17.** CVE-2025-31133 — runC Masked Path Abusive Mount Race Condition Enables Container Escape | CVSS:7.3 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2025-31133>)
**18.** CVE-2025-52565 — runC /dev/console Mount Race Vulnerability Enables Container Escape | CVSS:7.3 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2025-52565>)
**19.** CVE-2025-52881 — runC Arbitrary Write Gadgets & procfs Write Redirects Enable Container Escape & LSM Label Bypass | CVSS:7.3 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2025-52881>)
**20.** CVE-2025-12972 — Fluent Bit Path Traversal & Authentication Bypass Expose Cloud Infrastructure to RCE | CVSS:7.5 | Severity:High (<https://nvd.nist.gov/vuln/detail/CVE-2025-12972>)

### Key Actions / Summary Themes
1. **Patch Kernel & Hypervisor Stack**: Multiple critical kernel LPE and VM escape vulnerabilities (Copy Fail, SCTPhantom, Januscape, Zapscape, Fragnesia, DirtyClone) affect all Linux hosts running containers or VMs. Prioritize applying upstream kernel patches immediately, especially for GKE/EKS/AKS managed node pools where vendor patches may be lagging.
2. **Upgrade Container Runtimes**: All three runc vulnerabilities (CVE-2025-31133, CVE-2025-52565, CVE-2025-52881) enable container escapes from Docker/Kubernetes workloads. Upgrade to patched runc versions and review OCP/seccomp profiles to mitigate impact while patches propagate.
3. **Address Actively Exploited Services**: CISA has added Langflow (CVE-2026-9198), Apache Tomcat (CVE-2026-34486), and N-able N-central to its KEV catalog. Immediately patch or network-isolate affected systems—Langflow requires upgrade to v1.10.1+, Tomcat to latest 9.0.x/10.1.x/11.0.x releases.
4. **Review Kubernetes Ingress Configurations**: CVE-2025-1974 (IngressNightmare) allows unauthenticated RCE on Ingress NGINX Controllers used by over 40% of cloud deployments. Verify your ingress-nginx controller version is patched and enforce admission webhook authentication.
5. **Harden AI/LLM Platform Exposures**: IBM Langflow and kubectl MCP server flaws demonstrate how AI agent tooling introduces new attack surfaces directly into cluster control planes. Disable unnecessary auto-login endpoints, restrict API exposure, and apply defense-in-depth zero-trust policies to AI infrastructure components.

---
_Git commit: `6b8297ac9ab8` pushed to main_
