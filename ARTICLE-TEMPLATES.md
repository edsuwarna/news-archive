# Article Templates — News Archive

Standar format untuk semua artikel. Setiap kategori wajib mengikuti salah satu dari 5 tipe layout ini agar renderer `index.html` menampilkan konten dengan benar dan konsisten.

---

## Global Rules

- **Format tanggal baku:** `DD Month YYYY` — contoh: `05 August 2026`. Jangan pakai nama hari (Senin/Selasa), jangan pakai angka nol di depan kalau tidak perlu (pake `5 August`, bukan `05 August`). Format ini yang paling rapi di sidebar dan kartu homepage.
- **Bahasa:** Satu artikel = satu bahasa penuh. English untuk DevOps/AI/K8s/Tech Foundations. Indonesian untuk Self-Hosted/Ekonomi. JANGAN campur dalam satu paragraf/artikel. JANGAN nyelip karakter non-Latin (Cyrillic, CJK, dll).
- **Judul maksimal 65 karakter.** Jika lebih panjang, tulis ringkasan judul di H2, detail lengkapnya di paragraf pertama. Sidebar akan memotong judul jika melebihi batas.

---

## Tipe A: News Roundup (DevOps, AI, Bare Metal)
*Gunakan untuk: daftar berita harian/mingguan.*

```markdown
# Top [Category] News — [Month DD], YYYY

## 1. 🚀 Emoji Title [Link](url)
Paragraf deskripsi singkat berisi inti berita. Tambahkan detail teknis atau angka penting jika relevan. Gunakan bullet points untuk poin-poin spesifik.

**Source:** [Headline](url)

## 2. 🔒 Emoji Title [Link](url)
Deskripsi artikel kedua...

**Source:** [Headline](url)
```

**Rules:**
- Heading `## N.` dimulai dari 1, berturutan sampai ~20.
- Setiap item harus punya link di judul DAN source link terpisah di bawah.
- Pakai bahasa Inggris penuh.
- Batas maksimal 21 item per artikel (sudah default scraper).
- Emojis hanya sebagai prefix visual, bukan pengganti heading.

---

## Tipe B: Tool Report (Self-Hosted)
*Gunakan untuk: roundup tools/aplikasi self-hosted.*

```markdown
# Self-Hosted Tools Report — [Month DD], YYYY

## 1. Tool Name — Short Tagline (one-liner)
Deskripsi dalam Bahasa Indonesia. Jelaskan apa tool ini, use-case utama, teknologi yang dipakai, dan siapa target audienya. Gunakan bullet points untuk fitur-fitur kunci.

**Source:** [Link](url)

## 2. Another Tool — Brief Description
Detail lebih lanjut...

**Source:** [Link](url)
```

**Rules:**
- Nama tool ditulis **bold**: `**Tool Name**`.
- Deskripsi menggunakan Bahasa Indonesia.
- Format tagline setelah nama tool: pisahkan dengan em-dash (—), maksimal 8 kata.
- Tetap pakai numbering `## N.`.

---

## Tipe C: Economics Report (Ekonomi)
*HANYA SATU DARI DUA MODEL INI — jangan dicampur.*

### Model C1: Market Snapshot (recommended untuk hari kerja)
```markdown
# UPDATE EKONOMI INDONESIA & GLOBAL — [Month DD], YYYY

### Ringkasan Pasar
Paragraf ringkasan menyeluruh ekonomi hari ini. Key macro indicators, sentiment pasar.

| Indikator | Nilai | Perubahan |
|-----------|-------|-----------|
| IHSG | ... | ... |
| USD/IDR | ... | ... |

### Ekonomia Indonesia
Sub-kategori ekonomi domestik, analisis kebijakan BI, inflasi, dll.

| Tabel Data | ... | ... |
|------------|-----|-----|

### Ekonomi Global
Berita ekonomi internasional yang berdampak pada Indonesia.
```

**Rules:**
- Gunakan tabel untuk data numerik (kurs, saham, GDP, dll).
- Bahasa Indonesia penuh.
- Header section tanpa numbering.

### Model C2: News List (recommended untuk weekend/special report)
```markdown
# Laporan Ekonomi — [Month DD], YYYY

## 1. 📉 Headline Berita Utama
Deskripsi lengkap berita ekonomi pertama.

## 2. 🏦 Headline Berita Kedua
Deskripsi berita kedua.
```

**Rules:**
- Sama kayak Tipe A tapi Bahasa Indonesia.
- Tanpa tabel. Cocok untuk laporan non-data-driven.

---

## Tipe D: Security Briefing (K8s Security)
*Gunakan untuk: CVE, advisories, vulnerability reports.*

```markdown
# Kubernetes Security Briefing — [Month DD], YYYY

## 🔴 Critical

### 1. Tool/System Name — Vulnerability Type (CVE-XXXX-XXXXXXX)
Detailed description of the vulnerability, affected versions, attack vector, and impact on Kubernetes environments. Include any available patches or mitigations.

### 2. Another CVE — Description (CVE-XXXX-XXXXXXX)
More details...

## 🟡 High

### 1. Medium Severity Vuln — Description (CVE-XXXX-XXXXXXX)
...

## 🟢 Medium

### 1. Low Impact Issue — Description
...
```

**Rules:**
- Severity levels WAJIB ada: `🔴 Critical`, `🟡 High`, `🟢 Medium`.
- Setiap CVE minimal punya: affected component, CVE ID, and short impact summary.
- Bahasa Inggris penuh.
- Tidak perlu nomor urut lintas severity (1,2,3 hanya dalam satu level).

---

## Tipe E: Foundation Updates (Tech Foundations)
*Gunakan untuk: CNCF, Apache, Linux Foundation, OpenInfra updates.*

### Model E1: Grouped by Foundation (recommended)
```markdown
# Tech Foundations Weekly — [Month DD], YYYY

## 🌐 CNCF (Cloud Native Computing Foundation)

### 1. Project/Release Title
Description of the announcement, release highlights, and relevance to cloud-native ecosystem.

### 2. Second Announcement
...

## 🪶 Apache Software Foundation

### 1. Apache Project Update
Details about Apache project news, releases, or governance changes.

## 🐧 Linux Foundation

### 1. LF Announces New Initiative
Information about Linux Foundation initiatives, collaborations, or funding.
```

### Model E2: Flat Numbered (alternative)
```markdown
# Tech Foundations Update — [Month DD], YYYY

## 1. 🌐 CNCF: Project Release Title
Description...

## 2. 🪶 Apache: Project Update
Description...

## 3. 🐧 Linux: Foundation News
Description...
```

**Rules:**
- Pilih satu model saja per artikel. Jangan mix Model E1 dan E2 dalam satu file.
- Foundation emoji opsional tapi disarankan untuk quick scanning.
- Bahasa Inggris penuh untuk technical announcements.
- JANGAN nyelipkan karakter non-Latin (contoh: Cyrillic `Проекты` harus diganti jadi `Projects`).

---

## Quick Decision Matrix

| Kategori | Tipe | Model |
|----------|------|-------|
| DevOps | A | Standard |
| AI | A | Standard |
| Bare Metal | A | Standard (pakai English) |
| Self-Hosted | B | Standard |
| Ekonomi (weekday) | C1 | Market Snapshot |
| Ekonomi (weekend) | C2 | News List |
| K8s Security | D | Standard |
| Tech Foundations | E1 | Grouped by Foundation |

---

## Checklist Before Publishing

1. ✅ Format heading sesuai tipe (bukan manual override)
2. ✅ Tanggal pakai format `DD Month YYYY` (contoh: `5 August 2026`)
3. ✅ Bahasa konsisten — satu bahasa penuh per artikel (EN untuk DevOps/AI/K8s/Tech Foundations; ID untuk Self-Hosted/Ekonomi)
4. ✅ Judul maksimal 65 karakter (jika lebih panjang, ringkas di heading, detail di body)
5. ✅ No Cyrillic, CJK, atau karakter non-Latin dalam artikel
6. ✅ Minimal 1 sumber/link per artikel
7. ✅ No mixed formatting (e.g., don't use tables AND numbered list in same Ekonomi article)
8. ✅ Max 21 items per article (default scraper cap)
9. ✅ Validasi otomatis di script generator (`finalize-top20.py`): pastikan script menerapkan template dan reject output yang melanggar rules global
