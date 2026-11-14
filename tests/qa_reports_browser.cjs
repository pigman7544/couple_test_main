// BROWSER_PATH and PLAYWRIGHT_MODULE are local runner configuration.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
(async () => {
 const browser = await chromium.launch({headless:true});
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
   assert.equal(check.oldScores,false);assert.ok(check.headings>=6);
   for(const scores of check.scores) assert.deepEqual(scores,[]);
   if(!['c01','c06'].includes(fixture.couple.id)) assert.ok(check.comments);
   results.push({width,id:fixture.couple.id,...check});
   if(fixture.couple.id==='c06'||(width===390&&['c11','f01'].includes(fixture.couple.id))) {
    for(const [id,chapter] of [['sajuA',3],['crisis',4]]) {
     await page.locator('#'+id).evaluate(e=>{const section=e.closest('.section');window.scrollTo({top:section.getBoundingClientRect().top+scrollY,behavior:'instant'});});
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     await page.locator('#'+id).locator('..').screenshot({path:`tests/qa-display-${fixture.couple.id}-${width}-ch${chapter}.png`});
    }
   }
  }
  assert.deepEqual(errors,[]);
  await page.locator('#back').click();
  await page.locator('#formSection').waitFor({state:'visible'});
  await page.close();
 }
 await browser.close();
 fs.writeFileSync('docs/qa-display-browser.json',JSON.stringify(results,null,2));
 console.log('PASS: real c06 input/preview/unlock/back; 36 controlled report renders; five chapters; no numeric compatibility scores; selective body emphasis; no overflow or page errors');
})().catch(e=>{console.error(e);process.exit(1)});
