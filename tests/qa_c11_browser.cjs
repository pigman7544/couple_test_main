const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const base=process.env.QA_BASE || 'http://127.0.0.1:8931';
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
   assert.equal(await page.locator('#story').isVisible(),false);
   const opener=page.locator('#plotOpen'),dialog=page.locator('#plotDialog');
   await opener.focus();await page.keyboard.press('Enter');
   assert.equal(await dialog.evaluate(e=>e.open),true);
   assert.equal(await page.locator('#plotClose').evaluate(e=>e===document.activeElement),true);
   assert.equal((await page.locator('#plotBody').innerText()).replace(/\s+/g,''),r.plot.body.replaceAll('**','').replaceAll('◆','').replace(/\s+/g,''));
   for(let k=0;k<5;k++){await page.keyboard.press('Tab');assert.ok(await dialog.evaluate(e=>e.contains(document.activeElement)));}
   await page.keyboard.press('Shift+Tab');assert.ok(await dialog.evaluate(e=>e.contains(document.activeElement)));
   const box=await dialog.boundingBox();assert.ok(box.width<=width-20);assert.ok(box.height<=900*.81);
   await page.locator('#plotBody').evaluate(e=>e.scrollTop=e.scrollHeight);
   assert.ok(await page.locator('#plotBody').evaluate(e=>e.scrollTop>0));
   await dialog.screenshot({path:`tests/qa-structure-modal-${c.id}-${width}.png`});
   await page.keyboard.press('Escape');assert.equal(await dialog.evaluate(e=>e.open),false);
   assert.equal(await opener.evaluate(e=>e===document.activeElement),true);
   await opener.click();await page.locator('#plotClose').click();assert.equal(await dialog.evaluate(e=>e.open),false);
   await opener.click();await page.mouse.click(2,2);assert.equal(await dialog.evaluate(e=>e.open),false);
   assert.equal(await page.evaluate(()=>document.body.style.overflow),'');

   for(let i=0;i<3;i++){
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
    await el.screenshot({path:`tests/qa-structure-c11-${c.id}-${width}-ch${i+1}.png`});
    checks.push({sample:c.id,width,chapter:i+1,domEqualsApi:true,overflow:false,maxBodyBold:Math.max(...density)});
    if(i<2)await page.locator('#chapterReaderBottom .reader-next').click();
   }
   assert.ok(await page.locator('.generated-card img').isVisible());
   assert.ok((await page.locator('.generated-card a').getAttribute('href')).startsWith('data:image/svg+xml'));
   const downloaded=page.waitForEvent('download');await page.locator('.generated-card a').click();assert.equal((await downloaded).suggestedFilename(),'연연_c11_이야기카드.svg');
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
   // Reuse the same renderer for another type, then return to c11.
   const c06=await (await page.request.get(base+'/api/c06-sample/A')).json();
   await page.evaluate(x=>{fillPairName(x.couple.name);fill(x.full_report);setupCoupleCard(x.couple,x.full_report);arrangeFinalChapter();yeonyeonInitReader(x.couple);},c06);
   assert.equal(await page.locator('#plotOpen').isVisible(),false);
   assert.equal(await page.locator('[data-report-chapter="true"]').count(),5);
   await page.evaluate(x=>{fillPairName(x.couple.name);fill(x.full_report);setupCoupleCard(x.couple,x.full_report);arrangeFinalChapter();yeonyeonInitReader(x.couple);},c.response);
   assert.equal(await page.locator('[data-report-chapter="true"]').count(),3);
   assert.equal(await page.locator('#plotOpen').isVisible(),true);
   assert.deepEqual(errors,[]);
  }
  await page.close();
 }
 // Every unchanged type still renders with five chapters after c11 in the same document.
 const compatibility=await browser.newPage();await compatibility.goto(base+'/?sample=c11-A');await compatibility.locator('#premiumReport').waitFor({state:'visible'});
 for(const f of JSON.parse(fs.readFileSync('tests/browser-reports.json','utf8')).filter(f=>f.couple.id!=='c11')){
  await compatibility.evaluate(x=>{fillPairName(x.couple.name);fill(x.full_report);setupCoupleCard(x.couple,x.full_report);arrangeFinalChapter();yeonyeonInitReader(x.couple);},f);
  assert.equal(await compatibility.locator('[data-report-chapter="true"]').count(),5);
  assert.equal(await compatibility.locator('#plotOpen').isVisible(),false);
 }
 await compatibility.close();
 const health=await browser.newPage();assert.equal((await health.request.get(base+'/health')).status(),200);
 await browser.close();
 fs.writeFileSync(process.env.QA_OUTPUT||'docs/qa-c11-structure-local.json',JSON.stringify({base,checks,actualInputPreviewUnlock:6,pageErrors:[],health:200,modalKeyboardCloseFocusReturn:6,cardDownloads:6,otherTypeCompatibility:11},null,2));
 console.log('PASS: c11 actual A/B x 360/390/1440 x 3 chapters; API/DOM equality; input/preview/unlock; no scores/overflow/page errors');
})().catch(e=>{console.error(e);process.exit(1)});
