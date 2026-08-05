#!/usr/bin/env python3
"""Apply all UI/UX improvements to index.html in one shot."""

FILE = '/home/ubuntu/projects-repo/news-archive/index.html'

with open(FILE, 'r') as f:
    content = f.read()

# 1. ADD THEME PERSISTENCE BEFORE init()
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
content = content.replace(
    "        async function init() {",
    theme_js + "\n        async function init() {\n            loadTheme();"
)

# 2. FIX THEME TOGGLE TO SAVE
old_tt = """                    case 'dark':
                        document.documentElement.setAttribute('data-theme', '');
                        break;
                    case 'light':
                        document.documentElement.setAttribute('data-theme', 'light');
                        break;
                }
            };
        })();"""
new_tt = """                    case 'dark':
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
content = content.replace(old_tt, new_tt)

# 3. SIDEBAR TITLE TRIMMING
old_st = """                    // Format date: remove .md extension and show nicely
                    const display = item.title || file.replace('.md', '').replace(/-/g, '/');
                    const cleanTitle = stripEmoji(display);"""
new_st = """                    // Format date: remove .md extension and show nicely
                    const display = item.title || file.replace('.md', '').replace(/-/g, '/');
                    let cleanTitle = stripEmoji(display);
                    // Trim long titles for sidebar readability
                    if (cleanTitle.length > 80) {
                        cleanTitle = cleanTitle.substring(0, 77) + '\\u{2026}';
                    }"""
content = content.replace(old_st, new_st)

# 4. ADD GLOBAL HELPER FOR SHOW MORE WITH ANIMATION
helper = r'''
        // Show all hidden articles with smooth animation
        function showAllArticles(btn, total) {
            const container = btn.closest('.article-list').querySelector('#articleItems');
            const hidden = container.querySelectorAll('.hidden-item');
            hidden.forEach((item, i) => {
                setTimeout(() => {
                    item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
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
content = content.replace(
    '    </script>\n    <div class="lightbox"',
    helper + '    </script>\n    <div class="lightbox"'
)

# 5. CSS: HIDDEN ITEMS TRANSITION
css_hide = '''        .hidden-item {
            opacity: 0;
            transform: translateY(8px);
            transition: opacity 0.3s ease, transform 0.3s ease, border-color 0.15s, background 0.15s;
        }
        /* Article item card */
'''
content = content.replace(
    '        /* Article item card */',
    css_hide
)

# 6. LOAD-MORE BUTTON HOVER EFFECT
old_lmb = ".load-more-btn:hover {\n    border-color: var(--accent);\n    color: var(--accent);\n    background: var(--bg3);\n}"
new_lmb = """.load-more-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--bg3);
    transform: translateY(-1px);
}
.load-more-btn:active {
    transform: translateY(0);
}"""
content = content.replace(old_lmb, new_lmb)

# 7. BACK-TO-TOP SMOOTHER
old_btt = """            transition: all 0.2s;"""
new_btt = """            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);"""
content = content.replace(old_btt, new_btt)

old_btt2 = """            transform: translateY(-2px);"""
new_btt2 = """            transform: translateY(-3px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        }
        .back-to-top:active {
            transform: translateY(0);"""
content = content.replace(old_btt2, new_btt2)

# 8. CATEGORY CARD META WITH LAYOUT FLEX
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
content = content.replace(old_meta, new_meta)

with open(FILE, 'w') as f:
    f.write(content)

print("All UI/UX improvements applied!")
print(f"File size: {len(content)} bytes")
