const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const base=process.env.QA_BASE || 'http://127.0.0.1:8923';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH});
 const cases=JSON.parse(fs.readFileSync('tests/c11-browser-responses.json','utf8'));
 const checks=[];
 for(const width of [360,390,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const c of cases){
   const res=await page.request.post(base+'/api/test-unlock',{data:c.payload});
   assert.equal(res.status(),200);assert.deepEqual(await res.json(),c.response);
   await page.goto(base+'/?sample=c11-'+c.id);
   await page.locator('#premiumReport').waitFor({state:'visible'});
   await page.evaluate(()=>document.fonts.ready);
   const r=c.response.full_report;
   for(let i=0;i<5;i++){
    const key=r.sections[i],id=key==='saju_a'?'sajuA':key,el=page.locator('#'+id);
    assert.equal(await page.locator('#premiumReport').getAttribute('data-active-chapter'),String(i+1));
    assert.ok(await el.isVisible());
    const text=(await el.innerText()).replace(/\s+/g,'');
    assert.equal(text,r[key].replaceAll('**','').replaceAll('◆','').replace(/\s+/g,''));
    assert.doesNotMatch(text,/\d+(?:\.\d+)?\/(?:10|100)(?!\d)|\d+점|궁합(?:점수|등급)/);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    const density=await el.evaluate(e=>[...e.querySelectorAll('p')].map(p=>{const b=p.cloneNode(true);b.querySelectorAll('.subhead').forEach(h=>h.remove());return b.querySelectorAll('strong').length;}));
    assert.ok(density.every(n=>n<=2));
    if(i===0){
     assert.equal(await el.locator('.subhead').count(),2);
     assert.ok((await el.locator('.subhead').allTextContents()).every(h=>/를 닮은 (당신|상대방)/.test(h)));
     for(const strong of await el.locator('strong').all())assert.ok(Number(await strong.evaluate(e=>getComputedStyle(e).fontWeight))>=600);
    }
    await el.screenshot({path:`tests/qa-c11-${c.id}-${width}-ch${i+1}.png`});
    checks.push({sample:c.id,width,chapter:i+1,domEqualsApi:true,overflow:false,maxBodyBold:Math.max(...density)});
    if(i<4)await page.locator('#chapterReaderBottom .reader-next').click();
   }
   await page.locator('#back').click();await page.locator('#formSection').waitFor({state:'visible'});
   // Actual input -> free preview -> test unlock, without forced matcher responses.
   await page.goto(base);
   for(const who of ['a','b']){
    await page.locator(`[name="${who}_date"]`).fill(c.payload[who].date);
    await page.locator(`[name="${who}_time"]`).fill(c.payload[who].time);
   }
   await page.locator('#submit').click();await page.locator('#result').waitFor({state:'visible'});
   assert.equal(await page.locator('#pairName').innerText(),'엘리자베스·다아시');
   assert.equal(await page.locator('#premiumReport').isVisible(),false);
   await page.locator('#payButton').click();await page.locator('#premiumReport').waitFor({state:'visible'});
   assert.equal((await page.locator('#roles').innerText()).replace(/\s+/g,''),r.roles.replaceAll('**','').replaceAll('◆','').replace(/\s+/g,''));
   assert.deepEqual(errors,[]);
  }
  await page.close();
 }
 const health=await browser.newPage();assert.equal((await health.request.get(base+'/health')).status(),200);
 await browser.close();
 fs.writeFileSync(process.env.QA_OUTPUT||'docs/qa-c11-local.json',JSON.stringify({base,checks,actualInputPreviewUnlock:6,pageErrors:[],health:200},null,2));
 console.log('PASS: c11 actual A/B x 360/390/1440 x 5 chapters; API/DOM equality; input/preview/unlock; no scores/overflow/page errors');
})().catch(e=>{console.error(e);process.exit(1)});
