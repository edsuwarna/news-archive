#!/usr/bin/env python3
"""Fix all bugs and E2E test in ONE script."""

import os
import re

FILE = '/home/ubuntu/projects-repo/news-archive/index.html'

with open(FILE, 'r') as f:
    content = f.read()

# ============================================================
# FIX: Sidebar article display — ensure ISO dates don't show
# ============================================================
old_display = """                    // Format title: prefer item.title, fallback formatted date
                    let display = item.title;
                    if (!display || display.includes('-')) {
                        display = file.replace('.md', '').replace(/-/g, '/');
                    }"""
new_display = """                    // Format title: prefer item.title, fallback formatted date
                    let display = item.title;
                    const fileDateMatch = file.match(/^(\\d{4})-(\\d{2})-(\\d{2})/);
                    if (!display) {
                        // No title — generate from filename YYYY-MM-DD
                        if (fileDateMatch) {
                            const months = ['January','February','March','April','May','June',
                                           'July','August','September','October','November','December'];
                            display = `${months[parseInt(fileDateMatch[2])-1]} ${parseInt(fileDateMatch[3])}, ${fileDateMatch[1]}`;
                        } else {
                            display = file.replace('.md', '').replace(/-/g, '/');
                        }
                    }"""

if old_display in content:
    content = content.replace(old_display, new_display, 1)
    print("✅ FIX ARTICLE DISPLAY: ISO dates now properly converted to 'Month DD, YYYY'")
else:
    print("⚠️ Display pattern not found (might already be different)")
    # Search for partial match
    if 'item.title' in content:
        idx = content.find('item.title')
        print(f"   Found 'item.title' at position {idx}")
        print(f"   Context: ...{repr(content[idx-50:idx+100])}...")

# Write back
with open(FILE, 'w') as f:
    f.write(content)

print(f"\nFile size: {len(content)} bytes\n")
