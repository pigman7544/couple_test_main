(() => {
  const meanings = {
    일간: '태어난 날의 두 글자 중 앞 글자예요. 사주에서 나를 나타내요.',
    일주: '태어난 날에 해당하는 두 글자예요. 앞 글자는 일간이에요.',
    월주: '태어난 달을 절기 기준으로 나타낸 두 글자예요.',
    년주: '태어난 해에 해당하는 두 글자예요.',
    연주: '태어난 해에 해당하는 두 글자예요.',
    시주: '태어난 시간대에 해당하는 두 글자예요.',
    월지: '월주 두 글자 중 뒤 글자예요.',
    일지: '일주 두 글자 중 뒤 글자예요.',
    명식: '태어난 연·월·일·시를 사주의 글자로 정리한 표예요.',
    오행: '목·화·토·금·수 다섯 가지 성질이에요.',
    십성: '일간을 기준으로 다른 글자와의 관계를 열 가지로 나눈 이름이에요.',
    상생: '오행에서 한 성질이 다른 성질을 돕는 관계예요.',
    상극: '오행에서 한 성질이 다른 성질을 조절하는 관계예요.',
    육충: '서로 마주하는 지지 여섯 쌍을 말해요.',
    육합: '전통 사주에서 서로 짝이 되는 지지 여섯 쌍을 말해요.',
    천간합: '전통 사주에서 서로 짝이 되는 천간 다섯 쌍을 말해요.',
    천간: '연·월·일·시를 적는 두 글자 가운데 각각 앞에 오는 글자예요.',
    지지: '연·월·일·시를 적는 두 글자 가운데 각각 뒤에 오는 글자예요.',
  };
  const alternatives = Object.keys(meanings).map(term =>
    term === '일주' ? '일주(?!일)' : term === '시주' ? '시주(?!하)' : term
  ).join('|');
  const pattern = new RegExp('(?<![가-힣0-9])(?:' + alternatives + ')', 'g');
  let nextId = 0;
  window.annotateSaju = (sections, seen = new Set()) => {
    for (const section of sections) {
      const walker = document.createTreeWalker(section, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      for (const node of nodes) {
        const matches = [...node.data.matchAll(pattern)];
        if (!matches.length) continue;
        const fragment = document.createDocumentFragment();
        let end = 0;
        for (const {0: term, index} of matches) {
          fragment.append(node.data.slice(end, index));
          end = index + term.length;
          if (seen.has(term)) {
            const label = document.createElement('span');
            label.className = 'saju-term';
            label.textContent = term;
            fragment.append(label);
            continue;
          }
          seen.add(term);
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'saju-term';
          button.textContent = term;
          button.setAttribute('aria-expanded', 'false');
          const definition = document.createElement('span');
          definition.className = 'saju-definition';
          definition.id = 'saju-definition-' + ++nextId;
          definition.hidden = true;
          definition.textContent = meanings[term];
          button.setAttribute('aria-controls', definition.id);
          function toggle(open) {
            definition.hidden = !open;
            button.setAttribute('aria-expanded', String(open));
          }
          button.addEventListener('click', () => toggle(definition.hidden));
          button.addEventListener('keydown', event => {
            if (event.key === 'Escape' && !definition.hidden) {
              event.stopPropagation();
              toggle(false);
            }
          });
          fragment.append(button, definition);
        }
        fragment.append(node.data.slice(end));
        node.replaceWith(fragment);
      }
    }
  };
})();
