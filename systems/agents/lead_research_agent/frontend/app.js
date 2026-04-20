
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
    const ind = document.getElementById('industry').value.trim();
    if (!c || !ind) { showAlert(alertEl, 'Company name and industry are required.'); return null; }
    return { company_name: c, industry: ind, region: document.getElementById('region').value || 'GCC',
             company_size: document.getElementById('companySize').value || null,
             additional_context: document.getElementById('context').value || null };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/leads/analyze', {
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
  container.innerHTML = renderLead(res.data);
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
  const res = await apiFetch('/api/v1/leads/history');
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
document.getElementById('apiDocs').innerHTML = `<div class="code-block">curl -X POST http://localhost:8002/api/v1/leads/analyze \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"company_name": "Emaar", "industry": "Real Estate", "region": "UAE"}'</div>`;

function scoreColor(s) { return s >= 70 ? 'green' : s >= 40 ? 'yellow' : 'red'; }
function statusBadge(s) { return s === 'hot' ? 'badge-red' : s === 'warm' ? 'badge-yellow' : 'badge-blue'; }

function renderLead(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  const sc = scoreColor(r.lead_score);
  const signals = (r.opportunity_signals || []).map(s =>
    `<li><span class="badge ${s.strength==='high'?'badge-red':s.strength==='medium'?'badge-yellow':'badge-green'}" style="margin-right:6px">${s.strength}</span>${s.signal}</li>`
  ).join('');
  return `<div class="result-card">
    <div class="result-header">
      <div>
        <div class="result-title">Lead Intelligence Report</div>
        <div class="result-meta" style="margin-top:6px">
          <span class="badge ${statusBadge(r.lead_status)}">${r.lead_status?.toUpperCase()}</span>
          <span class="badge badge-blue">Confidence: ${Math.round((r.confidence_score||0)*100)}%</span>
        </div>
      </div>
      <div class="score-section">
        <div class="score-num" style="color:var(--${sc==='green'?'success':sc==='yellow'?'warning':'danger'})">${r.lead_score}</div>
        <div class="score-label">/ 100</div>
      </div>
    </div>
    <div class="progress-wrap"><div class="progress-bar ${sc}" style="width:${r.lead_score}%"></div></div>
    <div class="result-section">
      <div class="result-section-title">Company Summary</div>
      <div class="result-text">${r.company_summary}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Opportunity Signals</div>
      <ul class="req-list">${signals}</ul>
    </div>
    <div class="result-section">
      <div class="result-section-title">Qualification Notes</div>
      <div class="result-text">${r.qualification_notes}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Recommended Approach</div>
      <div class="result-text"><strong>${r.recommended_approach}</strong></div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}
