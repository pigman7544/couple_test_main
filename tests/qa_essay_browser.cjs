// BROWSER_PATH and PLAYWRIGHT_MODULE are local runner configuration.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
(async () => {
 const browser = await chromium.launch({headless:true, executablePath:process.env.BROWSER_PATH});
 const results=[];
 for(const width of [360,390,1440]) {
  const page=await browser.newPage({viewport:{width,height:844}});
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8765');
  await page.locator('#submit').click();
  await page.locator('#result').waitFor({state:'visible'});
  await page.locator('#payButton').click();
  await page.locator('#premiumReport').waitFor({state:'visible'});
  assert.ok((await page.locator('#story').innerText()).includes('서호'));
  // Real c06 API flow first; all twelve controlled renderer fixtures follow.
  for(const fixture of JSON.parse(fs.readFileSync('tests/browser-reports.json','utf8'))) {
   await page.evaluate(x=>{fillPairName(x.couple.name);fill(x.full_report)},fixture);
   await page.evaluate(()=>document.fonts.ready);
   const check=await page.evaluate(()=>({
    overflow:document.documentElement.scrollWidth>innerWidth,
    chapters:['roles','story','sajuA','crisis','scene','tip'].map(id=>document.getElementById(id).closest('.section')).filter(e=>!e.classList.contains('hide')).length,
    modern:document.querySelector('#crisis').textContent.includes('가상 장면'),
    comments:document.querySelector('#story').textContent.includes('문학적 해설'),
    scores:['sajuA','crisis'].map(id=>[...document.getElementById(id).textContent.matchAll(/(?<!\d)(\d+)\/10(?!\d)/g)].map(x=>Number(x[1]))),
    oldScores:/\d+(?:\.\d+)?\/100/.test(document.querySelector('#premiumReport').textContent),
    bodyBold:[...document.querySelectorAll('#premiumReport .prose p strong')].filter(e=>!e.closest('.subhead')).length,
    headings:document.querySelectorAll('#sajuA strong, #crisis strong').length,
    headingText:[...document.querySelectorAll('#premiumReport .subhead')].map(e=>e.textContent)
   }));
   assert.equal(check.overflow,false); assert.equal(check.chapters,5); assert.ok(check.modern);
   const expectedHeadings=['roles','story','saju_a','crisis','scene','tip','ending'].flatMap(key=>fixture.full_report[key].split('\n').filter(line=>line.startsWith('◆ ')).map(line=>line.slice(2).replaceAll('**','')));
   assert.deepEqual(check.headingText,expectedHeadings);
   assert.equal(check.oldScores,false);assert.equal(check.bodyBold,0);assert.ok(check.headings>=6);
   for(const scores of check.scores) {assert.equal(scores.length,3);assert.ok(scores.every(n=>Number.isInteger(n)&&n>=1&&n<=10));}
   for(const [id,key] of [['sajuA','saju_a'],['crisis','crisis']]) {
    const expected=[...fixture.full_report[key].matchAll(/(?<!\d)(\d+)\/10(?!\d)/g)].map(x=>Number(x[1]));
    assert.deepEqual(check.scores[id==='sajuA'?0:1],expected);
   }
   if(!['c01','c06'].includes(fixture.couple.id)) assert.ok(check.comments);
   results.push({width,id:fixture.couple.id,...check});
   if(width===390) {
    for(const [id,chapter] of [['roles',1],['story',2],['sajuA',3],['crisis',4]]) {
     await page.locator('#'+id).evaluate(e=>{const section=e.closest('.section');window.scrollTo({top:section.getBoundingClientRect().top+scrollY,behavior:'instant'});});
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     await page.locator('#'+id).locator('..').screenshot({path:`tests/qa-essay-${fixture.couple.id}-${width}-ch${chapter}.png`});
    }
   }
  }
  assert.deepEqual(errors,[]);
  await page.locator('#back').click();
  await page.locator('#formSection').waitFor({state:'visible'});
  await page.close();
 }
 await browser.close();
 fs.writeFileSync('docs/qa-essay-browser.json',JSON.stringify(results,null,2));
 console.log('PASS: real c06 input/preview/unlock/back; 36 controlled report renders; five chapters; six integer scores; body bold removed; no overflow or page errors');
})().catch(e=>{console.error(e);process.exit(1)});
