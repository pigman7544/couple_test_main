// Exercise the real layout switch, including c06 -> another type -> c06.
const {readFileSync}=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=readFileSync('index.html','utf8');
const sections={};
const nodes={};
for(const id of ['roles','story','sajuA','crisis','scene','tip']){
 const classes=new Set();
 const chapter={textContent:'original '+id};
 const title={textContent:'title '+id};
 sections[id]={classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x)},querySelector:s=>s==='.chapter'?chapter:title};
 nodes[id]={closest:()=>sections[id]};
}
const script=html.split('<script>')[1].split('</script>')[0];
const code=script.slice(script.indexOf('function koreanParticle'),script.indexOf('function fill(x)'));
nodes.pairName={textContent:'백소정·허선',nextSibling:{textContent:'을 닮았어.'}};
const context=vm.createContext({$:id=>nodes[id]});
vm.runInContext(code,context);
const chapters=['roles','story','saju_a','crisis','tip'].map((key,i)=>({key,title:'c06 '+i}));
for(let pass=0;pass<2;pass++){
 context.setReportChapters(chapters);
 assert.equal(Object.values(sections).filter(s=>!s.classList.contains('hide')).length,5);
 assert.equal(sections.scene.classList.contains('hide'),true);
 assert.equal(sections.tip.querySelector('.chapter').textContent,'CHAPTER 05');
 assert.equal(sections.sajuA.querySelector('h2').textContent,'c06 2');
 context.setReportChapters(undefined);
 for(const [id,s] of Object.entries(sections)){
  assert.equal(s.classList.contains('hide'),false);
  assert.equal(s.querySelector('.chapter').textContent,'original '+id);
  assert.equal(s.querySelector('h2').textContent,id==='story'?'백소정·허선은 어떤 이야기를 남겼을까?':'title '+id);
 }
}
// Parse the complete inline script as well, catching syntax errors outside the switch.
new vm.Script(script);
console.log('PASS: c06 five chapters, other-type restoration, repeat navigation, script syntax');

// Every registered name: check preview particles and c06 -> other -> c06 restoration.
const couples=JSON.parse(readFileSync('couples.json','utf8'));
const expectedParticles={c01:'을',c02:'를',c03:'를',c06:'을',c10:'을',c11:'를',c13:'를',c18:'를',f01:'을',f02:'를',f03:'를',f04:'를'};
assert.equal(couples.length,12);
for(const couple of couples){
 context.fillPairName(couple.name);
 assert.equal(nodes.pairName.textContent,couple.name);
 assert.equal(nodes.pairName.nextSibling.textContent,expectedParticles[couple.id]+' 닮았어.',couple.id);
 context.setReportChapters(chapters);
 context.setReportChapters(couple.id==='c06'?chapters:undefined);
 assert.equal(Object.values(sections).filter(s=>!s.classList.contains('hide')).length,couple.id==='c06'?5:6);
 assert.equal(sections.story.querySelector('h2').textContent,couple.id==='c06'?'c06 1':couple.name+(expectedParticles[couple.id]==='을'?'은':'는')+' 어떤 이야기를 남겼을까?');
 context.setReportChapters(chapters);
 assert.equal(sections.story.querySelector('h2').textContent,'c06 1');
}
for(const [name,expected] of [['가','를'],['각','을'],['갈','을'],['힣','을'],['각','을'],['이름  ','을'],['','를'],[null,'를'],['Alice','를'],['123','를']]){
 assert.equal(context.koreanParticle(name,'을','를'),expected,String(name));
}
assert.ok(script.includes('fillPairName(d.couple.name);'));
assert.ok(!script.includes("$('pairName').textContent=d.couple.name;"));
console.log('PASS: all 12 couple names, preview particles, dynamic chapter titles, repeated type switches, Hangul boundaries and non-Hangul fallback');
