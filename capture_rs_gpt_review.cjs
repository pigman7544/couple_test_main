const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const {randomBytes} = require('node:crypto');
const {mkdir, readFile} = require('node:fs/promises');
const {resolve} = require('node:path');
const {createInterface} = require('node:readline');
const {chromium} = require('playwright');

const output = resolve(process.argv[2] || 'rs-gpt-review-artifacts');
const token = randomBytes(32).toString('hex');
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) =>
  /^(PATH|PATHEXT|SYSTEMROOT|WINDIR|TEMP|TMP|TMPDIR|PYTHONPATH)$/i.test(key)));
Object.assign(env, {RS_GPT_ADMIN_TOKEN: token, RS_GPT_LIVE: '0'});

async function capture() {
  await mkdir(output, {recursive: true});
  const server = spawn(process.env.PYTHON || 'python', ['-u', '-c', [
    'from rs_gpt_server import Handler, ThreadingHTTPServer',
    'with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:',
    '    print(server.server_port, flush=True)',
    '    server.serve_forever()',
  ].join('\n')], {cwd: __dirname, env, stdio: ['ignore', 'pipe', 'inherit']});
  let browser;
  try {
    const lines = createInterface({input: server.stdout});
    const port = await new Promise((resolvePort, reject) => {
      const timeout = setTimeout(() => reject(new Error('Local server startup timed out')), 15000);
      const fail = error => { clearTimeout(timeout); reject(error); };
      server.once('error', fail);
      server.once('exit', code => fail(new Error('Local server exited: ' + code)));
      lines.once('line', line => { clearTimeout(timeout); resolvePort(Number(line)); });
    });
    assert.ok(Number.isInteger(port) && port > 0);
    const origin = 'http://127.0.0.1:' + port;
    const samplePath = '/api/rs-gpt/admin/editorial-sample';
    for (const headers of [{}, {Authorization: 'Bearer ' + 'x'.repeat(64)}]) {
      const response = await fetch(origin + samplePath, {headers});
      assert.equal(response.status, 403);
    }
    browser = await chromium.launch();
    for (const [width, height] of [[1440, 1000], [390, 844]]) {
      const page = await browser.newPage({
        viewport: {width, height}, deviceScaleFactor: 1, locale: 'ko-KR',
        isMobile: width === 390, hasTouch: width === 390,
      });
      await page.route('**/*', route => {
        const request = route.request();
        return request.method() === 'GET' && new URL(request.url()).origin === origin
          ? route.continue() : route.abort();
      });
      await page.goto(origin + '/rs-gpt/admin');
      assert.equal(await page.locator('#review-export').isVisible(), false);
      await page.locator('#token').fill(token);
      await page.locator('#login button').click();
      await page.locator('#editorial-sample').click();
      await page.locator('#review-export').waitFor();
      assert.equal(await page.locator('#generate').isEnabled(), false);
      assert.equal(await page.locator('#token').inputValue(), '');
      assert.equal(await page.locator('.manuscript').count(), 3);
      assert.equal(await page.locator('.card-grid img').count(), 2);
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.images].map(image => image.decode()));
        window.scrollTo(0, 0);
      });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.screenshot({path: resolve(output, 'rs-gpt-admin-' + width + '.png'), fullPage: true});
      if (width === 1440) {
        for (const format of ['html', 'json']) {
          const [download] = await Promise.all([
            page.waitForEvent('download'), page.locator(`[data-format="${format}"]`).click(),
          ]);
          await download.saveAs(resolve(output, download.suggestedFilename()));
        }
        const json = JSON.parse(await readFile(resolve(output, 'rs-gpt-review.json'), 'utf8'));
        const html = await readFile(resolve(output, 'rs-gpt-review.html'), 'utf8');
        assert.equal(json.metadata.source, 'editorial_sample');
        assert.equal(json.metadata.export_version, 1);
        assert.equal(json.chapters.length, 3);
        assert.deepEqual(Object.keys(json.charts).sort(), ['a', 'b']);
        assert.deepEqual(Object.keys(json.art).sort(), ['plain', 'title']);
        assert.equal((html.match(/src="data:image\/png;base64,/g) || []).length, 2);
        assert.ok(!html.includes('<script') && !html.includes(token));
      }
      await page.close();
    }
    console.log(output);
  } finally {
    server.kill();
    await browser?.close();
  }
}

capture().catch(error => { console.error(error); process.exitCode = 1; });
