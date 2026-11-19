const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require(process.env.YEONYEON_PLAYWRIGHT || 'playwright');
const baseline = JSON.parse(fs.readFileSync('tests/fixtures/latest_matching.json'));
const db = JSON.parse(fs.readFileSync('couples.json'));
const origin = process.env.YEONYEON_REVIEW_URL || 'http://127.0.0.1:8932';
const controlledOrigin = process.env.YEONYEON_CONTROLLED_URL || 'http://127.0.0.1:8933';
const cases = new Map(baseline.cases.map(row => [row.couple, row.payload]));
cases.set('c06', {a:{date:'1992-03-18',time:'16:00'},b:{date:'1992-04-30',time:'01:00'}});
cases.set('c03', {a:{date:'1992-01-04'},b:{date:'1992-02-23'}});
const main = async () => {
  const browser = await chromium.launch({executablePath: process.env.YEONYEON_BROWSER});
  const outcome = {};
  try {
    const page = await browser.newPage({viewport:{width:390,height:844},isMobile:true,acceptDownloads:true});
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    for (const couple of db) {
      const payload = cases.get(couple.id) || cases.get('c06');
      const controlled = !cases.has(couple.id);
      const endpoint = controlled ? controlledOrigin : origin;
      await page.goto(endpoint);
      if (controlled) await page.evaluate(id => fetch('/__test/' + id), couple.id);
      for (const person of ['a', 'b']) {
        await page.locator('[name=' + person + '_date]').fill(payload[person].date);
        await page.locator('[name=' + person + '_time]').fill(payload[person].time || '');
        await page.locator('[name=' + person + '_calendar]').selectOption(payload[person].calendar || 'solar');
      }
      await page.locator('#submit').click();
      await page.locator('#heroArt').waitFor({state:'visible'});
      assert.equal(await page.locator('#pairName').innerText(), couple.name);
      const art = couple.id === 'c06' ? 'baek_heo' : couple.id;
      assert.equal(await page.locator('#heroArt').getAttribute('src'), '/assets/' + art + '_title.png');
      assert.ok(await page.locator('#heroArt').evaluate(img => img.decode().then(() => img.naturalWidth > 0)));
      assert.equal(await page.locator('#premiumReport').isVisible(), false);
      await page.locator('#payButton').click();
      await page.locator('#premiumReport').waitFor({state:'visible'});
      const term = page.locator('#roles button.saju-term').filter({hasText:/^일간$/}).first();
      await term.click();
      const definition = page.locator('#' + await term.getAttribute('aria-controls'));
      assert.match(await definition.innerText(), /태어난 날/);
      await term.press('Escape');
      assert.equal(await definition.isVisible(), false);
      const count = await page.locator('[data-report-chapter]').count();
      assert.equal(count, couple.id === 'c11' ? 3 : 5);
      if (couple.id === 'c11') {
        await page.locator('#plotOpen').click();
        assert.ok((await page.locator('#plotBody').innerText()).length > 300);
        await page.keyboard.press('Escape');
        assert.equal(await page.locator('#plotDialog').isVisible(), false);
      }
      const chapters = [];
      for (let i = 0; i < count; i++) {
        const active = page.locator('[data-report-chapter].chapter-visible');
        const title = await active.locator(':scope > h2').innerText();
        const body = await active.locator(':scope > .prose').innerText();
        assert.ok(body.trim().length > 80, title);
        assert.doesNotMatch(body, /편집상 비교|동점이면 입력 순서|성별이나 누가 더 사랑|세심한 품격/);
        if (i === 2 || await active.locator('#sajuA').count()) assert.equal(await active.locator('.subhead').count(), 0, title);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
        if (couple.id === 'c01' && i === 2) await page.screenshot({path:'../editorial-audit/chunhyang-chapter3.png',fullPage:true});
        chapters.push(title);
        if (i + 1 < count) await page.locator('#chapterReaderBottom .reader-next').click();
      }
      const cards = page.locator('#artSection figure');
      assert.equal(await cards.count(), 2);
      for (const [i, suffix] of ['title', 'plain'].entries()) {
        const card = cards.nth(i);
        const path = '/assets/' + art + '_' + suffix + '.png';
        assert.equal(await card.locator('img').getAttribute('src'), path);
        assert.ok(await card.locator('img').evaluate(img => img.decode().then(() => img.naturalWidth > 0)));
        const [download] = await Promise.all([page.waitForEvent('download'), card.locator('a[download]').click()]);
        assert.equal(await download.failure(), null);
        assert.deepEqual(fs.readFileSync(await download.path()), fs.readFileSync('.' + path));
      }
      outcome[couple.id] = {controlled, chapters, downloads:2};
      if (couple.id === 'c06') await page.screenshot({path:'../editorial-audit/baek-heo-cards.png',fullPage:true});
      console.log(couple.id, controlled ? 'controlled' : 'natural', chapters.length);
    }
    await page.goto(origin + '/manuscripts');
    const titles = await page.locator('.entry[data-action^="book-"]').evaluateAll(links => links.map(link => link.dataset.action));
    assert.equal(titles.length, 37);
    let shelfChapters = 0;
    for (const action of titles) {
      await page.locator('[data-action="' + action + '"]').click();
      await page.locator('[data-action="checkout"]').click();
      await page.locator('[data-action="unlock"]').click();
      for (let i = 0; i < 3; i++) {
        if (i) await page.locator('.reader-nav [data-action="chapter-' + i + '"]').click();
        const chapter = page.locator('article.article');
        assert.ok((await chapter.innerText()).length > 200, action);
        if (i === 2) assert.equal(await chapter.locator('h3').count(), 0);
        shelfChapters++;
      }
      await page.locator('.spread [data-action="library"]').click();
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync('../editorial-audit/browser.json', JSON.stringify({outcome,shelfChapters,errors}, null, 2));
  } finally { await browser.close(); }
};
main().catch(error => { console.error(error); process.exitCode = 1; });
