#!/usr/bin/env python3
"""Final cleanup: fix ALL remaining date inconsistencies in article titles."""
import os, re

ROOT = '/home/ubuntu/projects-repo/news-archive'

MONTHS_ID = {
    'mei': 'May', 'juni': 'June', 'juli': 'July', 'agustus': 'August',
    'maret': 'March', 'januari': 'January', 'februari': 'February',
    'april': 'April', 'september': 'September', 'oktober': 'October',
    'nopember': 'November', 'november': 'November', 'desember': 'December',
}

DAY_NAMES = ['senin','selasa','rabu','kamis','jumat','sabtu','minggu']


def clean_title(line):
    if not line.startswith('# '):
        return None
    title_prefix = '# '
    body = line[2:]
    parts = body.rsplit(' — ', 1)
    if len(parts) < 2:
        new_body = process_plain_date(body)
        if new_body and new_body != body:
            return title_prefix + new_body
        return None
    prefix_part = parts[0]
    date_part = ' — '.join(parts[1:])
    date_part = re.sub(r'\s*\([^)]*\)\s*$', '', date_part)
    for day in DAY_NAMES:
        date_part = re.sub(r'\b' + day + r'\b\s*', '', date_part, flags=re.IGNORECASE)
    date_part = re.sub(r'\s*,\s*', ' ', date_part)
    date_part = re.sub(r'\s+', ' ', date_part).strip()
    for id_m, en_m in MONTHS_ID.items():
        date_part = re.sub(r'\b' + id_m + r'\b', en_m, date_part, flags=re.IGNORECASE)
    m = re.match(r'^(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})$', date_part)
    changed = False
    if m:
        date_part = f"{m.group(2)} {int(m.group(1))}, {m.group(3)}"
        changed = True
    else:
        m_iso = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date_part)
        if m_iso:
            year, mon, day = m_iso.group(1), int(m_iso.group(2)), int(m_iso.group(3))
            months = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December']
            if 1 <= mon <= 12:
                date_part = f"{months[mon-1]} {day}, {year}"
                changed = True
    result = f"{prefix_part} — {date_part}"
    if result != line:
        return result
    return None


def process_plain_date(text):
    def swap(m):
        day, mon, year = m.group(1), m.group(2), m.group(3)
        return f"{mon} {int(day)}, {year}"
    def swap_iso(m):
        y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
        months = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December']
        if 1 <= mo <= 12:
            return f"{months[mo-1]} {d}, {y}"
        return m.group(0)
    new_text = re.sub(r'^.*?(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4}).*$', swap, text)
    if new_text == text:
        new_text = re.sub(r'(\d{4})-(\d{2})-(\d{2})', swap_iso, text)
    if new_text != text:
        return new_text
    return None


def main():
    fixed = 0
    total = 0
    for cat in sorted(os.listdir(ROOT)):
        cat_dir = os.path.join(ROOT, cat)
        if not os.path.isdir(cat_dir) or cat == 'scripts':
            continue
        for f in sorted(os.listdir(cat_dir)):
            if not f.endswith('.md'):
                continue
            total += 1
            fp = os.path.join(cat_dir, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                lines = fh.readlines()
            old_first = lines[0]
            new_first = clean_title(old_first)
            if new_first:
                lines[0] = new_first
                with open(fp, 'w', encoding='utf-8') as fh:
                    fh.writelines(lines)
                fixed += 1
                print(f"  [{cat}/{f}]")
                print(f"    OLD: {old_first.rstrip()}")
                print(f"    NEW: {lines[0].rstrip()}")
    
    print(f"\nTotal: {total}, Fixed: {fixed}")


if __name__ == '__main__':
    main()
