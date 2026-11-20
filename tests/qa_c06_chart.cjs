const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const base = process.env.QA_BASE || 'http://127.0.0.1:8771';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH});
 const cases=JSON.parse(fs.readFileSync('tests/fixtures/c06_comparison.json','utf8'));
 const checks=[];
 for(const width of [390,1440]){
  const page=await browser.newPage({viewport:{width,height:844}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const c of cases){
   const response=await page.request.post(base+'/api/match',{data:c.payload});
   assert.equal(response.status(),200);assert.equal((await response.json()).couple.id,'c06');
   const unlocked=await page.request.post(base+'/api/test-unlock',{data:c.payload});
   assert.equal(unlocked.status(),200);
   const actual=await unlocked.json();assert.deepEqual(actual,c.response);
   await page.goto(base+'/?sample=c06-'+c.id);
   await page.locator('#premiumReport').waitFor({state:'visible'});
   const report=actual.full_report;
   for(let i=0;i<5;i++){
    const key=report.sections[i];const id=key==='saju_a'?'sajuA':key;
    assert.equal(await page.locator('#premiumReport').getAttribute('data-active-chapter'),String(i+1));
    assert.ok(await page.locator('#'+id).isVisible());
    const txt=(await page.locator('#'+id).innerText()).replace(/\s+/g,'');
    assert.doesNotMatch(txt,/\d+(?:\.\d+)?\/(?:10|100)(?!\d)|\d+점|궁합(?:점수|등급)/);
    assert.equal(txt,report[key].replaceAll('**','').replaceAll('◆','').replace(/\s+/g,''));
    const rendered=await page.locator('#'+id).evaluate(el=>[...el.querySelectorAll('p')].map(p=>{
     const body=p.cloneNode(true);body.querySelectorAll('.subhead').forEach(h=>h.remove());
     return [...body.querySelectorAll('strong')].map(s=>s.textContent);
    }));
    const expected=report[key].split(/\n\n+/).map(block=>{
     const lines=block.split('\n');if(lines[0].startsWith('◆ '))lines.shift();
     return [...lines.join('\n').matchAll(/\*\*(.+?)\*\*/g)].map(m=>m[1]);
    });
    assert.deepEqual(rendered,expected);assert.ok(rendered.every(spans=>spans.length<=2));
    if(i===0){
     assert.deepEqual(await page.locator('#roles .subhead').allTextContents(),['허선을 닮은 당신','백소정을 닮은 상대방']);
     for(const word of ['일관성',c.id==='A'?'마음을 여는 속도':'돌봄의 방식']) assert.equal(await page.locator('#roles strong').filter({hasText:word}).count(),1);
    }
    if(i===0)for(const word of ['경금','단단한 쇠','병화','태양']){
     const strong=page.locator('#roles strong').filter({hasText:word});
     assert.equal(await strong.count(),1);
     assert.ok(Number(await strong.evaluate(el=>getComputedStyle(el).fontWeight))>=600);
    }
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    if(process.env.QA_SHOTS)await page.locator('#'+id).screenshot({path:`tests/qa-role-${c.id}-${width}-ch${i+1}.png`});
    else if(width===390)await page.locator('#'+id).screenshot({path:`tests/qa-c06-chart-${c.id}-ch${i+1}.png`});
    if(i<4)await page.locator('#chapterReaderBottom .reader-next').click();
   }
   assert.ok(await page.locator('#artSection').isVisible());
   assert.equal(await page.locator('#artSection a[download]').count(),2);
   checks.push({case:c.id,width,chapters:5,liveApiEqualsLocal:true,url:base+'/?sample=c06-'+c.id});
   await page.locator('#back').click();await page.locator('#formSection').waitFor({state:'visible'});
  }
  // Exercise the normal UI path too, with no sample query or forced type.
  await page.goto(base);
  const p=cases[0].payload;
  for(const who of ['a','b']){
   await page.locator(`[name="${who}_date"]`).fill(p[who].date);
   await page.locator(`[name="${who}_time"]`).fill(p[who].time);
  }
  await page.locator('#submit').click();await page.locator('#result').waitFor({state:'visible'});
  assert.equal(await page.locator('#premiumReport').isVisible(),false);
  await page.locator('#payButton').click();await page.locator('#premiumReport').waitFor({state:'visible'});
  assert.ok((await page.locator('#roles').innerText()).includes('당신의 일간은'));
  assert.deepEqual(errors,[]);await page.close();
 }
 const api=await request.newContext();
 for(const asset of ['baek_heo_title.png','baek_heo_plain.png']){
  const res=await api.get(base+'/assets/'+asset);
  assert.equal(res.status(),200);assert.ok((await res.body()).length>1000);
 }
 await api.dispose();await browser.close();
 fs.writeFileSync(process.env.QA_OUTPUT||'docs/qa-c06-chart-browser.json',JSON.stringify({base,checks,normalInputPreviewUnlock:true,cardAssets:true,pageErrors:[]},null,2));
 console.log('PASS: 2 cases x 2 widths x 5 chapters; real match/unlock equal fixtures; normal UI; cards; no overflow or page errors');
})().catch(e=>{console.error(e);process.exit(1)});
