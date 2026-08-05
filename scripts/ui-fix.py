#!/usr/bin/env python3
"""Apply 7 UI/UX improvements to index.html safely."""

FILE = '/home/ubuntu/projects-repo/news-archive/index.html'

with open(FILE, 'r') as f:
    content = f.read()

changes = []

# === 1. THEME PERSISTENCE (JS) ===
if 'loadTheme()' not in content:
    before_init = "        async function init() {"
    theme_js = '''        // ── Theme Persistence ──
        function loadTheme() {
            const saved = localStorage.getItem('news-theme');
            if (saved) {
                document.documentElement.setAttribute('data-theme', saved);
                updateThemeIcon(saved);
            }
        }
        function saveTheme(theme) {
            localStorage.setItem('news-theme', theme);
        }
        function updateThemeIcon(theme) {
            const btn = document.getElementById('themeToggle');
            if (btn) btn.textContent = theme === 'light' ? '\\u{1F319}' : '\\u2600\\ufe0f';
        }

'''
    content = content.replace(before_init, theme_js + "\n        async function init() {\n            loadTheme();", 1)
    changes.append("Theme persistence functions added")

# === 2. SAVE THEME ON TOGGLE ===
old_toggle = """                    case 'dark':
                        document.documentElement.setAttribute('data-theme', '');
                        break;
                    case 'light':
                        document.documentElement.setAttribute('data-theme', 'light');
                        break;
                }
            };
        })();"""
new_toggle = """                    case 'dark':
                        document.documentElement.setAttribute('data-theme', '');
                        saveTheme('dark');
                        updateThemeIcon('dark');
                        break;
                    case 'light':
                        document.documentElement.setAttribute('data-theme', 'light');
                        saveTheme('light');
                        updateThemeIcon('light');
                        break;
                }
            };
        })();"""
if old_toggle in content and new_toggle not in content:
    content = content.replace(old_toggle, new_toggle, 1)
    changes.append("Theme toggle now saves preference")

# === 3. SIDEBAR TITLE TRIMMING ===
old_trim = "                    const cleanTitle = stripEmoji(display);"
new_trim = """                    let cleanTitle = stripEmoji(display);
                    // Trim long titles for sidebar readability
                    if (cleanTitle.length > 80) {
                        cleanTitle = cleanTitle.substring(0, 77) + '\\u{2026}';
                    }"""
if old_trim in content:
    content = content.replace(old_trim, new_trim, 1)
    changes.append("Sidebar title trimming (>80 chars)")

# === 4. SHOW ALL HELPER FUNCTION ===
if 'showAllArticles' not in content:
    helper = '''
        // Show all hidden articles with smooth animation
        function showAllArticles(btn, total) {
            const container = btn.closest('.article-list').querySelector('#articleItems');
            const hidden = container.querySelectorAll('.hidden-item');
            hidden.forEach((item, i) => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                    item.style.display = '';
                    item.classList.remove('hidden-item');
                }, i * 50);
            });
            setTimeout(() => {
                btn.parentElement.innerHTML = '<span style="color:var(--text3);font-size:13px">Showing all ' + total + ' articles</span>';
            }, hidden.length * 50 + 300);
        }
'''
    # Insert before "Init" comment near end of script
    content = content.replace(
        "        // Init\n        marked.setOptions({ breaks: true, gfm: true });\n        init();\n    </script>",
        helper + "        // Init\n        marked.setOptions({ breaks: true, gfm: true });\n        init();\n    </script>"
    )
    changes.append("showAllArticles helper function added")

# === 5. CSS: HIDDEN ITEMS TRANSITION ===
old_css_hide = "        /* Article item card */"
new_css_hide = """        .hidden-item {
            opacity: 0;
            transform: translateY(8px);
            transition: opacity 0.3s ease, transform 0.3s ease, border-color 0.15s, background 0.15s;
        }

        /* Article item card */"""
if ".hidden-item" not in content:
    content = content.replace(old_css_hide, new_css_hide, 1)
    changes.append("Hidden items CSS transition added")

# === 6. LOAD-MORE BUTTON HOVER EFFECT ===
old_lmb_hover = """        .load-more-btn:hover {
            border-color: var(--accent);
            color: var(--accent);
            background: var(--bg3);
        }"""
new_lmb_hover = """        .load-more-btn:hover {
            border-color: var(--accent);
            color: var(--accent);
            background: var(--bg3);
            transform: translateY(-1px);
        }
        .load-more-btn:active {
            transform: translateY(0);
        }"""
if "translateY(-1px)" not in content:
    content = content.replace(old_lmb_hover, new_lmb_hover, 1)
    changes.append("Load-more button hover effect added")

# === 7. BACK-TO-TOP SMOOTHER ===
old_btt = """        .back-to-top { position: fixed; bottom: 24px; right: 24px; z-index: 300; width: 40px; height: 40px; border-radius: 50%; background: var(--bg2); border: 1px solid var(--border); color: var(--text2); font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: all 0.2s; box-shadow: 0 2px 12px rgba(0,0,0,0.3); }
        .back-to-top.visible { opacity: 1; pointer-events: auto; }
        .back-to-top:hover { background: var(--bg3); color: var(--accent); border-color: var(--accent); transform: translateY(-2px); }"""
new_btt = """        .back-to-top { position: fixed; bottom: 24px; right: 24px; z-index: 300; width: 40px; height: 40px; border-radius: 50%; background: var(--bg2); border: 1px solid var(--border); color: var(--text2); font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 2px 12px rgba(0,0,0,0.3); }
        .back-to-top.visible { opacity: 1; pointer-events: auto; }
        .back-to-top:hover { background: var(--bg3); color: var(--accent); border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 4px 16px rgba(0,0,0,0.4); }
        .back-to-top:active { transform: translateY(0); }"""
if "cubic-bezier" not in content:
    content = content.replace(old_btt, new_btt, 1)
    changes.append("Back-to-top smoother animation added")

# === 8. CATEGORY CARD META FLEX + RECENT TAG ===
old_meta = """        .cat-card .meta {
            font-size: 11px;
            color: var(--text3);
            margin-top: 8px;
        }"""
new_meta = """        .cat-card .meta {
            font-size: 11px;
            color: var(--text3);
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .cat-card .meta .recent-tag {
            font-size: 10px;
            background: var(--green);
            color: #fff;
            padding: 1px 6px;
            border-radius: 10px;
            font-weight: 600;
            margin-left: 2px;
        }"""
if "recent-tag" not in content:
    content = content.replace(old_meta, new_meta, 1)
    changes.append("Category card flex layout + recent tag style added")

# Write back
with open(FILE, 'w') as f:
    f.write(content)

print(f"File size after: {len(content)} bytes ({len(content) - 83069:+d})\n")
for c in changes:
    print(f"✅ {c}")
print(f"\nTotal: {len(changes)}/8 improvements applied")
