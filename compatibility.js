'use strict';

const byId = id => document.getElementById(id);
const form = byId('birth-form');
const fields = {};
let activePayload = null;

for (const [key, name] of [['a', '첫째'], ['b', '둘째']]) {
  const fieldset = byId('birth-template').content.firstElementChild.cloneNode(true);
  fieldset.querySelector('legend').textContent = name;
  const inputs = Object.fromEntries(
    [...fieldset.querySelectorAll('[name]')].map(input => [input.name, input]),
  );
  inputs.calendar.addEventListener('change', () => {
    inputs.leap.parentElement.hidden = inputs.calendar.value !== 'lunar';
    if (inputs.leap.parentElement.hidden) inputs.leap.checked = false;
  });
  fields[key] = inputs;
  byId('birth-fields').append(fieldset);
}

function birth(inputs) {
  return {
    date: inputs.date.value,
    time: inputs.time.value,
    calendar: inputs.calendar.value,
    leap: inputs.leap.checked,
  };
}

async function request(action, payload) {
  const response = await fetch('/api/compatibility/' + action, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error);
  return data;
}

function text(tag, value) {
  const element = document.createElement(tag);
  element.textContent = value;
  return element;
}

function focus(id) {
  byId(id).focus({preventScroll: true});
  byId(id).scrollIntoView({block: 'start'});
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const payload = {a: birth(fields.a), b: birth(fields.b)};
  byId('submit').disabled = true;
  byId('input-error').textContent = '';
  byId('input-status').textContent = '두 사람의 궁합을 살펴보고 있어요.';
  try {
    const preview = await request('preview', payload);
    activePayload = payload;
    byId('preview-title').textContent = preview.title;
    byId('preview-excerpt').textContent = preview.excerpt;
    byId('contents').replaceChildren(...preview.chapters.map(title => text('li', title)));
    byId('input-panel').hidden = true;
    byId('preview').hidden = false;
    focus('preview-label');
  } catch (error) {
    byId('input-error').textContent = error.message || '잠시 후 다시 시도해 주세요.';
  } finally {
    byId('submit').disabled = false;
    byId('input-status').textContent = '';
  }
});

byId('open-report').addEventListener('click', async () => {
  const payload = activePayload;
  if (!payload) return;
  byId('open-report').disabled = true;
  byId('report-error').textContent = '';
  byId('report-status').textContent = '전체 리포트를 준비하고 있어요.';
  try {
    const report = await request('report', payload);
    if (payload !== activePayload) return;
    byId('chapters').replaceChildren(...report.chapters.map((chapter, index) => {
      const article = document.createElement('article');
      const heading = text('h3', chapter.title);
      heading.prepend(text('span', (index + 1) + '장'));
      article.append(heading);
      for (const paragraph of chapter.paragraphs) {
        article.append(text('p', paragraph.text));
      }
      return article;
    }));
    byId('preview').hidden = true;
    byId('report').hidden = false;
    byId('samples').hidden = false;
    focus('report-title');
  } catch (error) {
    if (payload === activePayload) {
      byId('report-error').textContent = error.message || '잠시 후 다시 시도해 주세요.';
    }
  } finally {
    byId('open-report').disabled = false;
    byId('report-status').textContent = '';
  }
});

function editInputs() {
  activePayload = null;
  byId('preview').hidden = true;
  byId('report').hidden = true;
  byId('samples').hidden = true;
  byId('report-error').textContent = '';
  byId('input-panel').hidden = false;
  focus('input-title');
}

byId('edit').addEventListener('click', editInputs);
byId('again').addEventListener('click', editInputs);
