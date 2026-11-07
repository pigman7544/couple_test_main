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
const code=script.slice(script.indexOf('const reportLayoutIds'),script.indexOf('function fill(x)'));
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
  assert.equal(s.querySelector('h2').textContent,'title '+id);
 }
}
// Parse the complete inline script as well, catching syntax errors outside the switch.
new vm.Script(script);
console.log('PASS: c06 five chapters, other-type restoration, repeat navigation, script syntax');
