# 📰 News Archive

Automated news aggregation repository powered by **Hermes Agent** cron jobs. This repository stores categorized news summaries that are automatically collected, compiled, and pushed on a scheduled basis.

## 📂 Directory Structure

```
devops/             → DevOps, SRE & Cloud Engineering news
baremetal/          → Bare-metal Server & Hardware news
selfhosted/         → Self-hosted tools & applications
ekonomi/            → Indonesian & Global Economy updates
k8s-security/       → Kubernetes Security briefings
tech-foundations/   → CNCF, Apache, Linux & OpenInfra Foundation updates
f1/                 → Formula 1 race schedule & post-session analysis
motogp/              → MotoGP race schedule & post-session analysis
```

### 🌐 Web Viewer

Access the news archive online: **[https://news.edsuwarna.id](https://news.edsuwarna.id)**

A client-side SPA (`index.html`) automatically lists all articles by category. No build step needed — just open the page.

### 📋 Updating Article Index

After cron jobs push new articles, regenerate the index:

```bash
python3 scripts/generate-articles-json.py
git add articles.json
git commit -m "Update article index"
git push
```

The SPA will reflect new articles immediately after deploy.

## 🤖 How It Works

This repository is automatically updated by **Hermes Agent** — an AI-powered automation system running on a VPS. Each cron job performs the following steps:

1. **Collect** — Gathers latest news from multiple sources using web research
2. **Summarize** — Compiles a concise briefing in markdown format
3. **Save** — Writes the markdown file to the appropriate directory
4. **Push** — Automatically commits and pushes to this repository

### Schedule

| Directory | Frequency |
|---|---|
| `devops/` | Every 2 days at 07:00 WIB |
| `baremetal/` | Every 2 days at 07:00 WIB (alternating with devops) |
| `selfhosted/` | Every Friday at 21:00 WIB |
| `ekonomi/` | Every 3 days at 20:00 WIB |
| `k8s-security/` | Every 3 days at 08:00 WIB |
| `tech-foundations/` | Every Saturday at 08:00 WIB |
| `f1/` | Race weekend schedule |
| `motogp/` | Race weekend schedule |

## 🚀 Setting Up Your Own Instance

To run this yourself, you'll need **Hermes Agent** installed on a server with cron capabilities.

### Prerequisites

- A Linux server (VPS or bare-metal)
- [Hermes Agent](https://hermes-agent.nousresearch.com) installed
- Git configured with SSH access to your fork

### Configuration

1. Fork this repository and clone it to your server:
   ```bash
   git clone git@github.com:yourusername/news-archive.git
   ```

2. Configure Hermes Agent cron jobs with the following pattern:
   ```bash
   hermes cron create \
     --name "devops-news" \
     --schedule "0 7 */2 * *" \
     --prompt "Research and compile latest DevOps/SRE/Cloud news..." \
     --deliver "local"
   ```

3. Each cron job should save markdown files to the news-archive directory and auto-push:
   ```bash
   cd /path/to/news-archive && \
   git add -A && \
   git commit -m "Update: $(date +%Y-%m-%d) news" && \
   git push origin main
   ```

### Manual Run

To trigger an immediate update:
```bash
hermes cron run <job-id>
```

## 📄 License

This repository contains automatically collected news summaries. Content belongs to their respective original sources.

---

> Auto-updated by Hermes Agent 🤖
