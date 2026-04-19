
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
    const id = document.getElementById('rfpId').value.trim();
    const co = document.getElementById('companyName').value.trim();
    const cap = document.getElementById('capabilities').value.trim();
    const txt = document.getElementById('rfpText').value.trim();
    if (!id || !co || !cap || !txt) { showAlert(alertEl, 'Please fill in all required fields.'); return null; }
    return { id, company_name: co, company_capabilities: cap, rfp_text: txt,
             submission_deadline: document.getElementById('deadline').value || null };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/rfp/analyze', {
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
  container.innerHTML = renderRFP(res.data);
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
  const res = await apiFetch('/api/v1/rfp/history');
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
document.getElementById('apiDocs').innerHTML = `
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">POST /api/v1/rfp/analyze — Analyze RFP text and generate response plan</div>
  <div class="code-block">curl -X POST http://localhost:8003/api/v1/rfp/analyze \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
  "id": "rfp-2024-001",
  "rfp_text": "We require a robotics integration partner for our warehouse...",
  "company_name": "Acme Robotics LLC",
  "company_capabilities": "10 years robotics integration, ROS2, AGV deployment",
  "submission_deadline": "2024-12-31"
}'</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">POST /api/v1/rfp/analyze-file — Upload PDF/TXT and analyze</div>
  <div class="code-block">curl -X POST http://localhost:8003/api/v1/rfp/analyze-file \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@rfp_document.pdf" \\
  -F "company_name=Acme Robotics LLC" \\
  -F "company_capabilities=10 years robotics integration, ROS2" \\
  -F "submission_deadline=2024-12-31"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /api/v1/rfp/history — List analysis history</div>
  <div class="code-block">curl http://localhost:8003/api/v1/rfp/history \\
  -H "X-API-Key: YOUR_API_KEY"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /api/v1/account/me — Get account &amp; credit balance</div>
  <div class="code-block">curl http://localhost:8003/api/v1/account/me \\
  -H "X-API-Key: YOUR_API_KEY"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /health — Health check (no auth)</div>
  <div class="code-block">curl http://localhost:8003/health</div>
</div>
`;

function renderRFP(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  const pct = r.win_probability || 0;
  const sc = pct >= 60 ? 'green' : pct >= 40 ? 'yellow' : 'red';
  const reqs = (r.requirement_matrix || []).map(req =>
    `<tr><td style="padding:8px;font-size:13px">${req.requirement}</td>
     <td style="padding:8px;text-align:center"><span class="badge ${req.can_meet?'badge-green':'badge-red'}">${req.can_meet?'✓ Yes':'✗ No'}</span></td>
     <td style="padding:8px;font-size:13px;color:var(--muted)">${req.notes}</td></tr>`).join('');
  const outline = (r.response_outline||[]).map((s,i)=>`<li style="padding:4px 0;font-size:14px">${i+1}. ${s}</li>`).join('');
  const risks = (r.risk_flags||[]).map(f=>`<li style="color:var(--danger);font-size:13px">${f}</li>`).join('');
  return `<div class="result-card">
    <div class="result-header">
      <div>
        <div class="result-title">RFP Analysis: ${data.id || ''}</div>
        <div style="margin-top:6px"><span class="badge badge-blue">Win Probability: ${pct}%</span></div>
      </div>
      <div class="score-section">
        <div class="score-num" style="color:var(--${sc==='green'?'success':sc==='yellow'?'warning':'danger'})">${pct}%</div>
        <div class="score-label">Win Prob</div>
      </div>
    </div>
    <div class="progress-wrap"><div class="progress-bar ${sc}" style="width:${pct}%"></div></div>
    <div class="result-section">
      <div class="result-section-title">Requirement Matrix</div>
      <table style="width:100%;border-collapse:collapse">
        <thead><tr>
          <th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">Requirement</th>
          <th style="padding:8px;font-size:12px;color:var(--muted)">Can Meet</th>
          <th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">Notes</th>
        </tr></thead>
        <tbody>${reqs}</tbody>
      </table>
    </div>
    ${risks ? `<div class="result-section"><div class="result-section-title">Risk Flags</div><ul class="req-list">${risks}</ul></div>` : ''}
    <div class="result-section">
      <div class="result-section-title">Response Outline</div>
      <ul style="list-style:none;padding:0">${outline}</ul>
    </div>
    <div class="result-section">
      <div class="result-section-title">Executive Summary Draft</div>
      <div class="result-text" style="background:#f8faff;padding:12px;border-radius:8px;border:1px solid #dbeafe">${r.executive_summary_draft}</div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}

document.getElementById('uploadBtn').addEventListener('click', async () => {
  const btn = document.getElementById('uploadBtn');
  const alertEl = document.getElementById('uploadAlert');
  hideAlert(alertEl);
  const file = document.getElementById('rfpFile').files[0];
  if (!file) { showAlert(alertEl, 'Please select a file first.'); return; }
  const co = document.getElementById('fileCompanyName').value.trim();
  const cap = document.getElementById('fileCapabilities').value.trim();
  if (!co || !cap) { showAlert(alertEl, 'Company name and capabilities are required.'); return; }
  setLoading(btn, true);
  const form = new FormData();
  form.append('file', file);
  form.append('company_name', co);
  form.append('company_capabilities', cap);
  form.append('submission_deadline', document.getElementById('fileDeadline').value || '');
  const key = getApiKey();
  const res = await fetch('/api/v1/rfp/analyze-file', {
    method: 'POST', headers: key ? { 'X-API-Key': key } : {}, body: form
  }).then(async r => { const t = await r.text(); let d; try { d = JSON.parse(t); } catch { d = t; } return { ok: r.ok, status: r.status, data: d }; })
    .catch(e => ({ ok: false, status: 0, data: { detail: e.message } }));
  setLoading(btn, false);
  if (!res.ok) {
    const msg = res.status === 402 ? '⚡ Insufficient credits.' : (res.data?.detail || 'Upload failed.');
    showAlert(alertEl, msg, res.status === 402 ? 'info' : 'error'); return;
  }
  const container = document.getElementById('resultContainer');
  container.style.display = 'block';
  container.innerHTML = renderRFP(res.data);
  if (res.data?.credits_remaining != null) updateCreditsDisplay(res.data.credits_remaining);
  container.scrollIntoView({ behavior: 'smooth' });
});
