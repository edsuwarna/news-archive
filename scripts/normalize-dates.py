#!/usr/bin/env python3
"""Batch normalize article formatting across all categories."""

import os
import re

ROOT = '/home/ubuntu/projects-repo/news-archive'

MONTHS_ID_TO_EN = {
    'januari': 'January', 'februari': 'February', 'maret': 'March',
    'april': 'April', 'mei': 'May', 'juni': 'June', 'juli': 'July',
    'agustus': 'August', 'september': 'September', 'oktober': 'October',
    'nopember': 'November', 'november': 'November', 'desember': 'December',
}

CYRILIC_REPLACEMENTS = {
    'Проекты': 'Projects',
    'Релизы': 'Releases',
    'Тренды': 'Trends',
}

DAY_NAMES_EN = [
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
    'saturday', 'sunday'
]

DAY_NAMES_ID = [
    'senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu'
]


def normalize_month(month_raw):
    return MONTHS_ID_TO_EN.get(month_raw.lower(), month_raw.title())


def strip_day_names(text):
    result = text
    for day in DAY_NAMES_EN + DAY_NAMES_ID:
        result = re.sub(r'\b' + day + r'\b[,.\s\-]*', '', result, flags=re.IGNORECASE)
    result = re.sub(r',[,\-]', '', result)
    result = re.sub(r'[,\-]\s*', '', result)
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def normalize_date_in_text(text):
    # Pattern 1: ISO YYYY-MM-DD
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        year, month_num, day = m.group(1), int(m.group(2)), int(m.group(3))
        months = ['January','February','March','April','May','June',
                   'July','August','September','October','November','December']
        if 1 <= month_num <= 12:
            normalized = f"{day} {months[month_num-1]} {year}"
            return text[:m.start()] + normalized + text[m.end():], True

    # Pattern 2: "Month DD, YYYY" (swapping to DD Month YYYY)
    m = re.search(r'([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})', text)
    if m:
        month_en = normalize_month(m.group(1))
        normalized = f"{int(m.group(2))} {month_en} {m.group(3)}"
        return text[:m.start()] + normalized + text[m.end():], True

    # Pattern 3: "DD Month, YYYY" (normalize month name only)
    m = re.search(r'(\d{1,2})\s+([A-Za-z]+),?\s*(\d{4})', text)
    if m:
        month_en = normalize_month(m.group(2))
        normalized = f"{int(m.group(1))} {month_en} {m.group(3)}"
        return text[:m.start()] + normalized + text[m.end():], True

    return text, False


def strip_cyrillic(content):
    changed = False
    for cyr, eng in CYRILIC_REPLACEMENTS.items():
        if cyr in content:
            content = content.replace(cyr, eng)
            changed = True
    cleaned_chars = []
    for ch in content:
        cp = ord(ch)
        if 0x0400 <= cp <= 0x04FF:
            changed = True
            continue
        cleaned_chars.append(ch)
    if changed:
        return ''.join(cleaned_chars), True
    return content, False


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        original = f.read()

    lines = original.split('\n')
    changes = []

    h1_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^#\s+\S', line) and not line.startswith('##'):
            h1_idx = i
            break

    if h1_idx is None:
        return original, []

    h1 = lines[h1_idx]
    content_changed = original

    # Strip Cyrillic
    stripped_content, cyrillic_stripped = strip_cyrillic(content_changed)
    if cyrillic_stripped:
        content_changed = stripped_content
        lines = content_changed.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'^#\s+\S', line) and not line.startswith('##'):
                h1_idx = i
                break
        h1 = lines[h1_idx]
        changes.append("Stripped non-Latin characters")

    # Normalize date in H1 title
    parts = h1.rsplit(' — ', 1)
    new_h1 = h1
    if len(parts) >= 2:
        title_part = parts[0]
        date_part = ' — '.join(parts[1:])
        date_part = re.sub(r'\s*\([^)]*\)\s*$', '', date_part)
        date_part = strip_day_names(date_part)
        new_date, date_normed = normalize_date_in_text(date_part)
        if date_normed:
            new_h1 = title_part + ' — ' + new_date
            changes.append("Date normalized in title")

    if new_h1 != lines[h1_idx]:
        lines[h1_idx] = new_h1

    cat_name = os.path.basename(os.path.dirname(filepath))
    if cat_name == 'ekonomi':
        has_type_marker = any(re.match(r'#\s*Type:', l) for l in lines[:5])
        if not has_type_marker:
            has_tables = '|-' in content_changed
            model = 'C1' if has_tables else 'C2'
            lines.insert(1, f'# Type: {model}')
            changes.append(f"Added type marker ({model})")

    new_content = '\n'.join(lines)
    return new_content, changes


def main():
    total = 0
    fixed = 0
    skipped = 0
    summary = {}

    for cat in sorted(os.listdir(ROOT)):
        cat_dir = os.path.join(ROOT, cat)
        if not os.path.isdir(cat_dir):
            continue
        md_files = sorted(f for f in os.listdir(cat_dir) if f.endswith('.md'))
        cat_count = 0
        for filename in md_files:
            filepath = os.path.join(cat_dir, filename)
            total += 1
            try:
                new_content, changes = process_file(filepath)
            except Exception as e:
                print(f"ERROR {cat}/{filename}: {e}")
                continue
            if changes:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                rel = f"{cat}/{filename}"
                print(f"FIXED: {rel}")
                for c in changes:
                    print(f"      - {c}")
                fixed += 1
                cat_count += 1
            else:
                skipped += 1
        summary[cat] = cat_count

    print(f"\n{'='*60}")
    print(f"BATCH FIX COMPLETE")
    print(f"  Total files : {total}")
    print(f"  Fixed       : {fixed}")
    print(f"  Skipped OK  : {skipped}")
    print(f"{'='*60}")
    for cat, cnt in sorted(summary.items()):
        if cnt > 0:
            print(f"  [{cat}] {cnt} files fixed")
        else:
            print(f"  [{cat}] clean")


if __name__ == '__main__':
    main()
