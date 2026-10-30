'use strict';

const $ = id => document.getElementById(id);
let metadata = {}, entity = '', records = [], editing = null, busy = false;

function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
}

async function request(path, method = 'GET', payload) {
  const response = await fetch(path, {
    method,
    headers: payload === undefined ? {} : {'Content-Type': 'application/json'},
    body: payload === undefined ? undefined : JSON.stringify(payload)
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === 'string' ? error.detail : `요청 실패 (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll('button, #form input, #form select, #search').forEach(node => { node.disabled = value; });
}

function buildForm(record = null) {
  editing = record;
  $('form-title').textContent = record ? `수정 · #${record.id}` : '등록';
  $('delete').hidden = !record;
  $('fields').replaceChildren();
  for (const field of metadata[entity].fields) {
    const label = element('label', (field.label || field.name) + (field.required ? ' *' : ''));
    const input = element(field.type === 'bool' ? 'select' : 'input');
    input.id = `field-${field.name}`;
    input.name = field.name;
    input.required = Boolean(field.required);
    if (field.type === 'bool') {
      if (!field.required) input.append(new Option('미지정', ''));
      input.append(new Option('참', 'true'), new Option('거짓', 'false'));
    } else {
      input.type = ({int: 'number', float: 'number', date: 'date', datetime: 'datetime-local'})[field.type] || 'text';
      if (field.type === 'int') input.step = '1';
      if (field.type === 'float' || field.type === 'datetime') input.step = 'any';
    }
    const value = record ? record[field.name] : field.default;
    // 기존 datetime 문자열의 시간대와 정밀도는 편집하지 않으면 그대로 보존한다.
    input.value = value == null ? '' : String(value);
    input.dataset.initial = input.value;
    label.htmlFor = input.id;
    label.append(input);
    $('fields').append(label);
  }
  renderRows();
}

function renderRows() {
  const fields = metadata[entity].fields;
  const query = $('search').value.toLocaleLowerCase();
  const visible = records.filter(record => fields.some(field => field.type === 'str' && String(record[field.name] ?? '').toLocaleLowerCase().includes(query)) || !query);
  $('count').textContent = `${visible.length} / ${records.length}건`;
  $('rows').replaceChildren();
  for (const record of visible) {
    const row = element('tr');
    row.classList.toggle('selected', editing?.id === record.id);
    const cell = element('td');
    const edit = element('button', String(record.id));
    edit.type = 'button';
    edit.setAttribute('aria-label', `${record.id}번 수정`);
    edit.disabled = busy;
    cell.append(edit);
    row.append(cell);
    for (const field of fields) row.append(element('td', record[field.name] == null ? '—' : String(record[field.name])));
    row.addEventListener('click', () => { if (!busy) buildForm(record); });
    $('rows').append(row);
  }
  if (!visible.length) {
    const cell = element('td', '표시할 데이터가 없습니다.');
    cell.colSpan = fields.length + 1;
    const row = element('tr');
    row.append(cell);
    $('rows').append(row);
  }
}

async function selectEntity(name) {
  setBusy(true);
  $('message').textContent = '';
  try {
    const loaded = await request(`/api/${encodeURIComponent(name)}`);
    entity = name;
    records = loaded;
    $('title').textContent = metadata[name].label || name;
    $('search').value = '';
    for (const button of $('entities').children) button.setAttribute('aria-current', String(button.dataset.entity === name));
    const row = element('tr');
    for (const label of ['ID', ...metadata[name].fields.map(field => field.label || field.name)]) {
      const cell = element('th', label);
      cell.scope = 'col';
      row.append(cell);
    }
    $('head').replaceChildren(row);
    buildForm();
  } catch (error) { $('message').textContent = error.message; }
  finally { setBusy(false); }
}

async function mutate(method, payload) {
  setBusy(true);
  $('message').textContent = '';
  try {
    const saved = await request(`/api/${encodeURIComponent(entity)}${editing ? `/${editing.id}` : ''}`, method, payload);
    if (method === 'DELETE') records = records.filter(record => record.id !== editing.id);
    else if (editing) records = records.map(record => record.id === editing.id ? saved : record);
    else records.push(saved);
    buildForm();
    $('message').textContent = method === 'DELETE' ? '삭제했습니다.' : '저장했습니다.';
  } catch (error) { $('message').textContent = error.message; }
  finally { setBusy(false); }
}

$('form').addEventListener('submit', event => {
  event.preventDefault();
  if (busy || !entity) return;
  const payload = {};
  for (const field of metadata[entity].fields) {
    const input = $(`field-${field.name}`);
    if (editing && input.value === input.dataset.initial) continue;
    payload[field.name] = input.value === '' ? (field.type === 'str' ? '' : null)
      : field.type === 'bool' ? input.value === 'true'
      : ['int', 'float'].includes(field.type) ? Number(input.value) : input.value;
  }
  mutate(editing ? 'PUT' : 'POST', payload);
});
$('delete').addEventListener('click', () => {
  if (!busy && editing && window.confirm(`#${editing.id} 항목을 삭제하시겠습니까?`)) mutate('DELETE');
});
$('new').addEventListener('click', () => { if (entity && !busy) buildForm(); });
$('cancel').addEventListener('click', () => { if (entity && !busy) buildForm(); });
$('search').addEventListener('input', () => { if (entity) renderRows(); });

async function initialize() {
  setBusy(true);
  try {
    metadata = await request('/api/meta');
    for (const [name, config] of Object.entries(metadata)) {
      const button = element('button', config.label || name);
      button.type = 'button';
      button.dataset.entity = name;
      button.addEventListener('click', () => { if (!busy) selectEntity(name); });
      $('entities').append(button);
    }
    const first = Object.keys(metadata)[0];
    if (first) await selectEntity(first);
    else $('title').textContent = '엔티티가 없습니다.';
  } catch (error) { $('message').textContent = error.message; }
  finally { setBusy(false); }
}
initialize();
