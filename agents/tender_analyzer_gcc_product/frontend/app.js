const apiKeyInput = document.getElementById('apiKey');
const accountOutput = document.getElementById('accountOutput');
const resultOutput = document.getElementById('resultOutput');

async function apiFetch(url, options = {}) {
  const headers = options.headers || {};
  const key = apiKeyInput.value.trim();
  if (key) headers['X-API-Key'] = key;
  options.headers = headers;
  const response = await fetch(url, options);
  const text = await response.text();
  try { return { ok: response.ok, data: JSON.parse(text) }; }
  catch { return { ok: response.ok, data: text }; }
}

document.getElementById('loadAccount').addEventListener('click', async () => {
  const res = await apiFetch('/api/v1/account/me');
  accountOutput.textContent = JSON.stringify(res.data, null, 2);
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const payload = {
    id: `manual-${Date.now()}`,
    title: document.getElementById('title').value || 'Untitled tender',
    issuer: document.getElementById('issuer').value || 'Unknown issuer',
    country: document.getElementById('country').value || 'GCC',
    sector: document.getElementById('sector').value || '',
    description: document.getElementById('description').value || ''
  };
  const res = await apiFetch('/api/v1/tenders/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  resultOutput.textContent = JSON.stringify(res.data, null, 2);
});

document.getElementById('uploadBtn').addEventListener('click', async () => {
  const file = document.getElementById('pdfFile').files[0];
  if (!file) { resultOutput.textContent = 'Choose a file first.'; return; }
  const form = new FormData();
  form.append('file', file);
  form.append('title', document.getElementById('pdfTitle').value);
  form.append('issuer', document.getElementById('pdfIssuer').value);
  form.append('country', document.getElementById('pdfCountry').value || 'GCC');
  form.append('sector', document.getElementById('pdfSector').value);
  const key = apiKeyInput.value.trim();
  const res = await fetch('/api/v1/tenders/analyze-file', {
    method: 'POST',
    headers: key ? { 'X-API-Key': key } : {},
    body: form
  });
  const text = await res.text();
  try { resultOutput.textContent = JSON.stringify(JSON.parse(text), null, 2); }
  catch { resultOutput.textContent = text; }
});
