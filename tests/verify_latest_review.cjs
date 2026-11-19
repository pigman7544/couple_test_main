const assert = require('node:assert/strict');
const { chromium } = require(process.env.YEONYEON_PLAYWRIGHT || 'playwright');
const origin = process.env.YEONYEON_REVIEW_URL || 'http://127.0.0.1:8797';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.YEONYEON_BROWSER });
  try {
    for (const width of [360, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 844 }, isMobile: true });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const visible = sel => page.locator(sel).waitFor({ state: 'visible' });
      const noOverflow = async () => assert.equal(await page.evaluate(() =>
        document.documentElement.scrollWidth > innerWidth), false);
      await page.goto(origin);
      await page.locator('[name=b_date]').fill('1992-04-30');
      await page.locator('#submit').click();
      await visible('#result');
      assert.match(await page.locator('#pairName').innerText(), /백소정.*허선/);
      await visible('#heroArt');
      assert.ok(await page.locator('#heroArt').evaluate(img => img.decode().then(() => img.naturalWidth)));
      assert.match(await page.locator('#blurTeaser').evaluate(el => getComputedStyle(el).filter), /blur/);
      assert.ok((await page.locator('#previewStory').innerText()).trim());
      assert.equal(await page.locator('#premiumReport').isVisible(), false);
      await noOverflow();
      await page.locator('#payButton').click();
      await visible('#premiumReport');
      const term = page.locator('#roles button.saju-term').filter({ hasText: /^일간$/ });
      await term.click();
      const definition = page.locator('#' + await term.getAttribute('aria-controls'));
      await definition.waitFor({ state: 'visible' });
      assert.match(await definition.innerText(), /태어난 날/);
      await page.keyboard.press('Escape');
      assert.equal(await definition.isVisible(), false);
      assert.equal(await page.locator('[data-report-chapter]').count(), 5);
      for (let i = 0; i < 4; i++) await page.locator('#chapterReaderBottom .reader-next').click();
      await visible('#artSection .art-grid');
      const cards = page.locator('#artSection .art-grid figure');
      assert.equal(await cards.count(), 2);
      const files = [];
      for (const card of await cards.all()) {
        assert.ok(await card.locator('img').evaluate(img => img.decode().then(() => img.naturalWidth)));
        const [download] = await Promise.all([
          page.waitForEvent('download'), card.locator('a[download]').click()
        ]);
        assert.equal(await download.failure(), null);
        assert.match(download.suggestedFilename(), /\.png$/);
        files.push(require('node:fs').readFileSync(await download.path()));
      }
      assert.ok(files.every(file => file.subarray(0, 8).equals(Buffer.from('89504e470d0a1a0a', 'hex'))));
      assert.notDeepEqual(files[0], files[1]);
      await noOverflow();

      await page.goto(origin);
      for (const [name, value] of Object.entries({
        a_date: '1999-01-22', a_time: '01:00',
        b_date: '1998-11-09', b_time: '21:00'
      })) {
        await page.locator('[name=' + name + ']').fill(value);
      }
      await page.locator('#submit').click();
      await visible('#result');
      assert.match(await page.locator('#pairName').innerText(), /엘리자베스.*다아시/);
      assert.match(await page.locator('#tagline').innerText(), /숱한 오해를 넘어 새로운 사랑으로/);
      await page.locator('#payButton').click();
      await visible('#premiumReport');
      assert.equal(await page.locator('[data-report-chapter]').count(), 3);
      await page.locator('#plotOpen').click();
      await visible('#plotDialog');
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('#plotDialog').isVisible(), false);
      assert.ok(await page.locator('#heroArt').evaluate(img => img.decode().then(() => img.naturalWidth)));
      await noOverflow();

      await page.goto(origin);
      for (const [name, value] of Object.entries({
        a_date: '1992-01-04', a_time: '',
        b_date: '1992-02-23', b_time: ''
      })) await page.locator('[name=' + name + ']').fill(value);
      await page.locator('#submit').click();
      await visible('#result');
      assert.match(await page.locator('#pairName').innerText(), /온달.*평강/);
      assert.ok(await page.locator('#heroArt').evaluate(img => img.decode().then(() => img.naturalWidth)));
      await page.locator('#payButton').click();
      await visible('#roles');
      assert.match(await page.locator('#roles').innerText(), /말을 구해 돌봐요/);
      for (let i = 0; i < 2; i++) await page.locator('#chapterReaderBottom .reader-next').click();
      await visible('#sajuA');
      assert.match(await page.locator('#sajuA').innerText(), /어떤 약속이 마음을 놓이게 할까요/);
      assert.match(await page.locator('#sajuA').innerText(), /두 사람의 일간은 모두 기토예요/);
      await noOverflow();

      await page.goto(origin + '/manuscripts');
      assert.equal(await page.locator('.entry').count(), 37);
      await page.locator('#search').fill('로미오와 줄리엣');
      assert.equal(await page.locator('.entry').count(), 2);
      await page.locator('.entry').filter({hasText: '병계'}).click();
      await page.locator('[data-action=checkout]').click();
      await page.locator('[data-action=unlock]').click();
      assert.match(await page.locator('body').innerText(), /달을 증인 삼아/);
      await noOverflow();
      assert.deepEqual(errors, []);
      await page.close();
      console.log(width + 'px: matching, illustration, blur, unlock, reference report, and manuscript shelf passed');
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
