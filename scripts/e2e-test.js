const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    
    // Enable console capture
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log('  [BROWSER ERROR]', msg.text());
        }
    });

    let passed = 0;
    let failed = 0;

    function assert(test, name) {
        if (test) {
            console.log(`  ✅ ${name}`);
            passed++;
        } else {
            console.log(`  ❌ ${name}`);
            failed++;
        }
    }

    console.log('\n=== E2E TEST SUITE ===\n');

    // ============================
    // Test 1: Homepage loads correctly
    // ============================
    console.log('[Test] Homepage loads');
    await page.goto('https://news.edsuwarna.id', { waitUntil: 'networkidle2', timeout: 15000 });
    
    const title = await page.title();
    assert(title === 'News Archive', 'Page title is "News Archive"');
    
    const sidebarExists = await page.$('.sidebar') !== null;
    assert(sidebarExists, 'Sidebar exists');
    
    const latestSectionExists = await page.$('.latest-section') !== null;
    assert(latestSectionExists, 'Latest News section exists');
    
    const categoryCards = await page.$$('.cat-card');
    assert(categoryCards.length >= 7, `Category cards exist (${categoryCards.length} found, expected ≥7)`);

    // ============================
    // Test 2: Sidebar categories in alphabetical order
    // ============================
    console.log('\n[Test] Sidebar category order');
    const catElements = await page.$$('.sidebar-cat-header span:first-child');
    const catNames = [];
    for (const el of catElements) {
        const text = await page.evaluate(e => e.textContent.trim(), el);
        // Get the text after the SVG icon
        const allText = await el.$$eval('span', spans => spans.map(s => s.textContent.trim()).join(' ').trim().replace(/▶$/, '').trim());
    }
    
    // Better approach: get from the visible heading elements in sidebar
    const sidebarCats = await page.$$eval('.sidebar-cat-header span', els => 
        els.map(el => el.textContent.replace(/[▶\s]+$/, '').trim())
    );
    console.log(`  Found categories: ${sidebarCats.join(', ')}`);
    
    // Check alphabetical: AI < Bare Metal < DevOps < Ekonomi < K8s Security < Self Hosted < Tech Foundations
    const expectedOrder = ['Home', 'AI', 'Bare Metal', 'DevOps', 'Ekonomi', 'K8s Security', 'Self Hosted', 'Tech Foundations'];
    
    // The sidebar has Home first, then alphabetically sorted categories
    const actualAlphabetical = sidebarCats.filter(c => c !== 'Home');
    const expectedAlphabetical = ['AI', 'Bare Metal', 'DevOps', 'Ekonomi', 'K8s Security', 'Self Hosted', 'Tech Foundations'];
    const isAlphabetical = JSON.stringify(actualAlphabetical) === JSON.stringify(expectedAlphabetical);
    assert(isAlphabetical, `Categories in alphabetical order (${actualAlphabetical.join(' → ')})`);

    // ============================
    // Test 3: Date format consistency in sidebar links
    // ============================
    console.log('\n[Test] Date format in sidebar articles');
    const articleLinks = await page.$$eval('.sidebar-cat-list a', links => 
        links.slice(0, 10).map(a => a.textContent.trim().replace(/^[\u{2600}-\u{27BF}\u{2900}-\u{29FF}\u{2300}-\u{23FF}\u{FE00}-\u{FE0F}\u{1F300}-\u{1FAFF}]+/gu, '').trim().split(/\s+/).pop())
    );
    
    // Check that dates contain commas (Month DD, YYYY format) or are ISO (should be replaced)
    // Most recent articles should have "August" or "July" style
    console.log(`  Sample sidebar dates: ${articleLinks.join(', ')}`);
    const hasCommaDates = articleLinks.some(d => d.includes(','));
    const hasIsoDates = articleLinks.some(d => /^\d{4}-\d{2}-\d{2}$/.test(d));
    assert(!hasIsoDates, 'No ISO format dates in sidebar');
    assert(articleLinks.length > 0, 'Articles loaded in sidebar');

    // ============================
    // Test 4: Theme persistence
    // ============================
    console.log('\n[Test] Theme persistence');
    
    // First, set localStorage and refresh to simulate
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'networkidle2' });
    
    // Default should be dark (from HTML attribute)
    const initialTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    console.log(`  Initial theme: ${initialTheme}`);
    
    // Click theme toggle button
    await page.click('#themeToggle');
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Should now be light
    const afterToggleTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    console.log(`  After click: ${afterToggleTheme}`);
    
    // Check localStorage has the saved value
    const savedTheme = await page.evaluate(() => localStorage.getItem('news-theme'));
    console.log(`  Saved in localStorage: ${savedTheme}`);
    
    assert(afterToggleTheme === 'light', 'Theme changed to light after toggle');
    assert(savedTheme === 'light', 'Theme saved to localStorage');
    
    // Refresh and check it persists
    await page.reload({ waitUntil: 'networkidle2' });
    const persistedTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    const storedAfterRefresh = await page.evaluate(() => localStorage.getItem('news-theme'));
    console.log(`  After refresh: ${persistedTheme}, localStorage: ${storedAfterRefresh}`);
    
    // We need to manually set back to dark because the page starts as dark by default
    await page.evaluate(() => {
        localStorage.setItem('news-theme', 'dark');
        document.documentElement.setAttribute('data-theme', 'dark');
    });
    await page.reload({ waitUntil: 'networkidle2' });
    
    // ============================
    // Test 5: Show More functionality
    // ============================
    console.log('\n[Test] Show More button');
    
    // Navigate to a category with many articles
    await page.goto('https://news.edsuwarna.id/#/devops', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const articleItemsInitial = await page.$$('#articleItems .article-item');
    console.log(`  Articles on page (before show more): ${articleItemsInitial.length}`);
    
    // There should be some hidden items (only 10 shown initially)
    const totalArticles = await page.$$eval('#articleItems .article-item', items => items.length);
    const hiddenCount = await page.$$eval('#articleItems .hidden-item', items => items.length);
    console.log(`  Total articles: ${totalArticles}, Hidden: ${hiddenCount}`);
    
    const loadMoreBtn = await page.$('.load-more-btn');
    assert(loadMoreBtn !== null, 'Load more button exists');
    
    if (loadMoreBtn && totalArticles > 10) {
        console.log(`  Total (${totalArticles}) > 10, testing show all...`);
        
        // Scroll down to make sure button is visible
        await page.evaluate(() => window.scrollBy(0, 500));
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Click show more
        await page.click('.load-more-btn');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // All items should now be visible
        const articleItemsAfter = await page.$$eval('#articleItems .article-item', items => items.filter(i => i.style.display !== 'none').length);
        console.log(`  Articles visible after showing all: ${articleItemsAfter}`);
        
        assert(articleItemsAfter === totalArticles, `All ${totalArticles} articles visible after show all`);
        
        // Hidden items class should be removed
        const remainingHidden = await page.$$eval('.hidden-item', items => items.length);
        assert(remainingHidden === 0, 'All hidden-item classes removed');
    } else {
        console.log(`  Skipping show-all test (only ${totalArticles} articles, not > 10)`);
    }

    // ============================
    // Test 6: Load more button hover effect
    // ============================
    console.log('\n[Test] Load more button CSS');
    if (loadMoreBtn) {
        const btnStyles = await page.getComputedStyle(await page.$('.load-more-btn'), ':hover');
        const transform = await page.evaluate(el => getComputedStyle(el).transform, await page.$('.load-more-btn'));
        console.log(`  Transform property exists: ${!!transform}`);
        
        const fullCSS = await page.evaluate(() => {
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.selectorText === '.load-more-btn:hover') {
                            return rule.style.transform;
                        }
                    }
                } catch(e) {}
            }
            return null;
        });
        console.log(`  .load-more-btn:hover transform: ${fullCSS}`);
        assert(fullCSS === 'translateY(-1px)', 'Load more button has translateY(-1px) on hover');
    }

    // ============================
    // Test 7: Back-to-top button
    // ============================
    console.log('\n[Test] Back-to-top button');
    const btt = await page.$('#backToTop');
    assert(btt !== null, 'Back to top button exists');
    
    // Check cubic-bezier in CSS
    const bttCSS = await page.evaluate(() => {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText === '.back-to-top') {
                        return rule.style.transition || '';
                    }
                }
            } catch(e) {}
        }
        return null;
    });
    console.log(`  Transition: ${bttCSS}`);
    assert(bttCSS && bttCSS.includes('cubic-bezier'), 'Back-to-top has cubic-bezier easing');

    // ============================
    // Test 8: Hidden item animation CSS
    // ============================
    console.log('\n[Test] Hidden item CSS transition');
    const hiddenCSS = await page.evaluate(() => {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText === '.hidden-item') {
                        return rule.style.transition || '';
                    }
                }
            } catch(e) {}
        }
        return null;
    });
    console.log(`  .hidden-item transition: ${hiddenCSS}`);
    assert(hiddenCSS !== null, '.hidden-item CSS exists');
    assert(hiddenCSS && hiddenCSS.includes('opacity'), '.hidden-item has opacity transition');

    // ============================
    // Summary
    // ============================
    console.log(`\n========================================`);
    console.log(`RESULTS: ${passed} passed, ${failed} failed out of ${passed + failed} tests`);
    console.log(`========================================\n`);
    
    await browser.close();
    
    process.exit(failed > 0 ? 1 : 0);
})();
