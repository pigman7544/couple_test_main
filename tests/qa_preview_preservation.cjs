const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {execFileSync}=require('node:child_process');
const fs=require('node:fs'),assert=require('node:assert/strict');
const base=process.env.QA_BASE||'http://127.0.0.1:8931';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH});
 const original=execFileSync('git',['show','9a6b2b0:index.html'],{encoding:'utf8'});
 const checks=[];
 for(const width of [360,1440])for(const c of JSON.parse(fs.readFileSync('tests/fixtures/c11_comparison.json','utf8'))){
  const states=[];
  for(const baseline of [true,false]){
   const page=await browser.newPage({viewport:{width,height:900}});
   if(baseline)await page.route(base+'/',route=>route.fulfill({contentType:'text/html',body:original}));
   await page.goto(base+'/');
   for(const who of ['a','b']){await page.locator(`[name="${who}_date"]`).fill(c.payload[who].date);await page.locator(`[name="${who}_time"]`).fill(c.payload[who].time);}
   await page.locator('#submit').click();await page.locator('#result').waitFor({state:'visible'});
   states.push(await page.evaluate(()=>['pairName','heroWrap','tagline','previewStory','blurTeaser','paywall'].map(id=>{const e=document.getElementById(id);return {id,html:e.innerHTML,visible:!!e.getClientRects().length};})));
   assert.equal(await page.locator('#premiumReport').isVisible(),false);
   await page.close();
  }
  assert.deepEqual(states[0],states[1]);checks.push({sample:c.id,width,unchanged:true});
 }
 await browser.close();fs.writeFileSync(process.env.QA_OUTPUT||'docs/qa-c11-preview-preserved.json',JSON.stringify({base,checks},null,2));console.log('PASS: original/current free preview DOM and image visibility unchanged for A/B at 360/1440');
})().catch(e=>{console.error(e);process.exit(1)});
