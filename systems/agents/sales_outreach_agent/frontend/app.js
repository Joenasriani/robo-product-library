
function getApiKey() { return document.getElementById('apiKey').value.trim(); }

function showSection(name, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  if (btn) btn.classList.add('active');
}

function setLoading(btn, loading) {
  btn.disabled = loading;
  btn.classList.toggle('loading', loading);
}

function showAlert(el, msg, type='error') {
  el.className = 'alert show alert-' + type;
  el.textContent = msg;
}
function hideAlert(el) { el.className = 'alert'; el.textContent = ''; }

async function apiFetch(url, options = {}) {
  const headers = options.headers || {};
  const key = getApiKey();
  if (key) headers['X-API-Key'] = key;
  options.headers = headers;
  try {
    const res = await fetch(url, options);
    const text = await res.text();
    let data; try { data = JSON.parse(text); } catch { data = text; }
    return { ok: res.ok, status: res.status, data };
  } catch(e) {
    return { ok: false, status: 0, data: { detail: 'Network error: ' + e.message } };
  }
}

function updateCreditsDisplay(remaining) {
  const badge = document.getElementById('creditsBadge');
  const count = document.getElementById('creditsCount');
  badge.style.display = 'inline-flex';
  count.textContent = remaining;
  badge.className = 'credit-badge' + (remaining < 5 ? ' low' : '');
}

document.getElementById('loadAccount').addEventListener('click', async () => {
  const btn = document.getElementById('loadAccount');
  const alertEl = document.getElementById('accountAlert');
  setLoading(btn, true);
  hideAlert(alertEl);
  const res = await apiFetch('/api/v1/account/me');
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed to load account'); return; }
  const c = res.data.client;
  document.getElementById('accCredits').textContent = c.credits_remaining;
  document.getElementById('accPlan').textContent = c.plan;
  document.getElementById('accTotal').textContent = c.credits_total;
  document.getElementById('accUsed').textContent = c.credits_used;
  document.getElementById('accName').textContent = c.name;
  document.getElementById('accountInfo').style.display = 'block';
  updateCreditsDisplay(c.credits_remaining);
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const btn = document.getElementById('analyzeBtn');
  const alertEl = document.getElementById('analyzeAlert');
  hideAlert(alertEl);
  const payload = (() => {
    const c = document.getElementById('companyName').value.trim();
    const r = document.getElementById('targetRole').value.trim();
    const p = document.getElementById('problemStatement').value.trim();
    const s = document.getElementById('serviceOffer').value.trim();
    if (!c || !r || !p || !s) { showAlert(alertEl, 'Please fill in all required fields.'); return null; }
    return { company_name: c, target_role: r, problem_statement: p, service_offer: s,
             region: document.getElementById('region').value || 'GCC',
             tone: document.getElementById('tone').value };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/outreach/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  setLoading(btn, false);
  if (!res.ok) {
    const msg = res.status === 402 ? '⚡ Insufficient credits — please top up your account.' : (res.data?.detail || 'Analysis failed.');
    showAlert(alertEl, msg, res.status === 402 ? 'info' : 'error');
    return;
  }
  const container = document.getElementById('resultContainer');
  container.style.display = 'block';
  container.innerHTML = renderOutreach(res.data);
  if (res.data?.credits_remaining != null) updateCreditsDisplay(res.data.credits_remaining);
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

document.getElementById('loadHistoryBtn').addEventListener('click', loadHistory);
async function loadHistory() {
  const btn = document.getElementById('loadHistoryBtn');
  const alertEl = document.getElementById('historyAlert');
  const list = document.getElementById('historyList');
  hideAlert(alertEl);
  if (!getApiKey()) { showAlert(alertEl, 'Enter your API key first.'); return; }
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/outreach/history');
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed to load history'); return; }
  const items = res.data;
  if (!items || !items.length) { list.innerHTML = '<div class="empty-state"><p>No history yet. Run your first analysis!</p></div>'; return; }
  list.innerHTML = items.map(item => `
    <div class="history-item">
      <div>
        <div class="history-title">${item.request_title || item.request_id}</div>
        <div class="history-meta">${item.created_at?.substring(0,10) || ''}</div>
      </div>
    </div>`).join('');
}

// API docs
document.getElementById('apiDocs').innerHTML = `<div class="code-block">curl -X POST http://localhost:8001/api/v1/outreach/analyze \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"company_name": "Al Futtaim", "target_role": "VP Operations", "problem_statement": "...", "service_offer": "..."}'</div>`;

// PDF upload handler
document.getElementById('uploadBtn').addEventListener('click', async () => {
  const btn = document.getElementById('uploadBtn');
  const alertEl = document.getElementById('uploadAlert');
  hideAlert(alertEl);
  const file = document.getElementById('uploadFile').files[0];
  if (!file) { showAlert(alertEl, 'Please select a file first.'); return; }
  const company = document.getElementById('uploadCompany').value.trim();
  const role = document.getElementById('uploadRole').value.trim();
  if (!company || !role) { showAlert(alertEl, 'Company name and target role are required.'); return; }
  if (!getApiKey()) { showAlert(alertEl, 'Enter your API key first.'); return; }
  setLoading(btn, true);
  const form = new FormData();
  form.append('file', file);
  form.append('company_name', company);
  form.append('target_role', role);
  form.append('service_offer', document.getElementById('uploadService').value || 'Robotics and AI solutions');
  form.append('region', document.getElementById('uploadRegion').value || 'GCC');
  form.append('tone', 'formal');
  const key = getApiKey();
  const res = await fetch('/api/v1/outreach/analyze-file', {
    method: 'POST',
    headers: key ? { 'X-API-Key': key } : {},
    body: form
  }).then(async r => {
    const t = await r.text();
    let d; try { d = JSON.parse(t); } catch { d = t; }
    return { ok: r.ok, status: r.status, data: d };
  }).catch(e => ({ ok: false, status: 0, data: { detail: e.message } }));
  setLoading(btn, false);
  if (!res.ok) {
    const msg = res.status === 402 ? '⚡ Insufficient credits — please top up your account.' : (res.data?.detail || 'Upload failed.');
    showAlert(alertEl, msg, res.status === 402 ? 'info' : 'error');
    return;
  }
  const container = document.getElementById('resultContainer');
  container.style.display = 'block';
  container.innerHTML = '<h2 style="font-size:16px;font-weight:600;margin-bottom:4px">Outreach Results</h2>' + renderOutreach(res.data);
  if (res.data?.credits_remaining != null) updateCreditsDisplay(res.data.credits_remaining);
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

function renderOutreach(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  return `<div class="result-card">
    <div class="result-header">
      <div class="result-title">Outreach Sequence</div>
      <span class="badge badge-blue">Confidence: ${Math.round((r.confidence_score||0)*100)}%</span>
    </div>
    <div class="result-section">
      <div class="result-section-title">Subject Line</div>
      <div style="font-size:15px;font-weight:600;color:var(--primary)">${r.subject_line}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Value Proposition</div>
      <div class="result-text">${r.value_proposition}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Initial Message</div>
      <div class="result-text" style="background:#f8faff;border:1px solid #dbeafe;padding:12px;border-radius:8px">${r.short_message}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Follow-Up Message</div>
      <div class="result-text" style="background:#f8faff;border:1px solid #dbeafe;padding:12px;border-radius:8px">${r.followup_message}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Call to Action</div>
      <div class="result-text"><strong>${r.call_to_action}</strong></div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}
