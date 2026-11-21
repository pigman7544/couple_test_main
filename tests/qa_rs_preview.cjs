const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const url = process.argv[2] || 'http://127.0.0.1:8897';
const samples = {
  '01': ['비워 둔 시간이 약속이 되는 순간', 'pair.육충.a.day.b.hour'],
  '02': ['한 번 손을 보탠 뒤에 생기는 일', 'pair.상형.a.day.b.day'],
  '04': ['같은 곳에 가기로 하고 다른 주말을 그릴 때', 'pair.육해.a.day.b.day'],
  '03': ['한 번 바뀐 저녁을 다음 주에도 바꿀 수 있을까', 'pair.육충.a.day.b.month'],
  art: [null, null],
};

async function run() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const width of [360, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, isMobile: width < 500 });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const fit = async () => assert(await page.evaluate(() =>
        document.documentElement.scrollWidth <= innerWidth));
      for (const [sample, [title, id]] of Object.entries(samples)) {
        await page.goto(url);
        await fit();
        await page.selectOption('#demo', sample);
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
        if (title) assert.equal(await page.locator('#tagline').textContent(), title);
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
        assert.match(await page.locator('.natal-chart caption').first().textContent(), /봄님/);
        if (sample === '01') {
          assert.match(await page.locator('#coverage').textContent(), /월주.*보류/);
          assert.match(await page.locator('.natal-chart').first().textContent(), /己酉.*庚戌/);
        }
        await fit();
        await page.locator('#chapterReaderNav .reader-next').click();
        if (title) {
          assert.equal(await page.locator('.chapter-visible h2').textContent(), title);
          await page.locator('.chapter-visible details summary').first().click();
          assert(await page.locator('.chapter-visible [data-evidence-id="' + id + '"]:visible').count());
        }
        await fit();
        await page.locator('#chapterReaderNav .reader-next').click();
        await page.locator('.chapter-visible').getByRole('heading', { level: 2 }).waitFor();
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
