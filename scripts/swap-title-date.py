#!/usr/bin/env python3
"""Swap dates in article titles from 'DD Month YYYY' to 'Month DD, YYYY'.
Only processes H1 lines (article titles). Body content untouched."""
import os, re, glob

ROOT = '/home/ubuntu/projects-repo/news-archive'

def swap(m):
    day, month, year = m.group(1), m.group(2), m.group(3)
    return f"{month} {day}, {year}"

total = 0
fixed = 0

for mdfile in sorted(glob.glob(os.path.join(ROOT, '*', '*.md'))):
    cat = os.path.basename(os.path.dirname(mdfile))
    
    # Skip non-article files (scripts, ARTICLE-TEMPLATES, etc.)
    if cat == 'scripts':
        continue
        
    with open(mdfile, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        continue
    
    # Only process the very first line (H1 title)
    h1 = lines[0]
    new_h1 = re.sub(r'\b(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})\b', swap, h1)
    
    if new_h1 != h1:
        lines[0] = new_h1
        with open(mdfile, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        fixed += 1
        print(f"  {cat}/{os.path.basename(mdfile)}")
        print(f"    OLD: {h1.rstrip()}")
        print(f"    NEW: {new_h1.rstrip()}")
    
    total += 1

print(f"\nTotal: {total}, Fixed: {fixed}")
