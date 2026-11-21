const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const url = process.argv[2] || 'http://127.0.0.1:8897';
const samples = ['01', '02', '04', '03', 'art', 'review'];

async function run() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const width of [360, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, isMobile: width < 500 });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const fit = async () => assert(await page.evaluate(() =>
        document.documentElement.scrollWidth <= innerWidth));
      for (const sample of samples) {
        await page.goto(url);
        await fit();
        await page.selectOption('#demo', sample);
        if (sample === 'review') {
          for (const [field, value] of Object.entries({
            a_date: '1992-03-18', b_date: '1992-04-30', a_time: '', b_time: '',
            a_gender: 'male', b_gender: 'female', a_calendar: 'solar', b_calendar: 'solar',
          })) assert.equal(await page.locator('#' + field).inputValue(), value);
        }
        await page.fill('#a_name', '봄');
        await page.fill('#b_name', '여름');
        if (sample === '02') {
          await page.route('**/api/match', async route => {
            const request = route.request().postDataJSON();
            request.a.date = '2024-02-30';
            await route.continue({ postData: JSON.stringify(request) });
          }, { times: 1 });
          const invalid = page.waitForResponse(r => r.url().endsWith('/api/match'));
          await page.click('#submit');
          assert.equal((await invalid).status(), 400);
          await page.locator('#error').filter({ hasText: '입력 정보를 확인해 주세요.' }).waitFor();
        }
        const free = page.waitForResponse(r => r.url().endsWith('/api/match'));
        await page.click('#submit');
        const preview = await (await free).json();
        assert(!preview.full_report);
        await page.locator('#result').waitFor({ state: 'visible' });
        assert.equal(await page.locator('#tagline').textContent(), '두 명식이 만나는 자리');
        await fit();
        if (preview.art) {
          await page.waitForFunction(() => document.querySelector('#heroArt').naturalWidth > 0);
        }
        const unlocked = page.waitForResponse(r => r.url().endsWith('/api/test-unlock'));
        await page.click('#payButton');
        const full = await (await unlocked).json();
        assert.equal(full.test_mode, true);
        await page.locator('#premiumReport').waitFor({ state: 'visible' });
        assert.equal(await page.locator('.natal-chart:visible').count(), 2);
        assert.match(await page.locator('.natal-chart caption').first().textContent(), /봄/);
        if (sample === '01') {
          assert.match(await page.locator('#coverage').textContent(), /월주.*보류/);
          assert.match(await page.locator('.natal-chart').first().textContent(), /己酉.*庚戌/);
        }
        await fit();
        await page.locator('#chapterReaderNav .reader-next').click();
        assert.equal(await page.locator('.chapter-visible h2').textContent(), '두 명식이 만나는 자리');
        assert.equal(await page.locator('.paragraph-evidence, [data-evidence-id], .literature-corner').count(), 0);
        if (sample === 'review') {
          assert.deepEqual(full.full_report.compatibility.coverage, { a: ['hour'], b: ['hour'] });
          assert.match(await page.locator('.chapter-visible').textContent(), /정재.*편관|정재.*정관/);
        }
        await fit();
        await page.locator('#chapterReaderNav .reader-next').click();
        await page.locator('.chapter-visible').getByRole('heading', { name: '두 사람의 관계를 이어 가는 법' }).waitFor();
        await fit();
        if (preview.art) {
          await page.locator('#artSection').scrollIntoViewIfNeeded();
          await page.waitForFunction(() =>
            [...document.querySelectorAll('#artSection img')].every(image => image.naturalWidth > 0));
          const saved = page.waitForEvent('download');
          await page.locator('#artSection a').first().click();
          assert.match((await saved).suggestedFilename(), /\.png$/);
        }
        await page.click('#back');
        await page.locator('#matchForm').waitFor({ state: 'visible' });
        assert.deepEqual(errors, []);
        console.log(JSON.stringify({ width, sample, title: preview.preview.title, art: !!preview.art }));
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
