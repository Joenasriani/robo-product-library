// --- Utilities ---
function getApiKey() { return document.getElementById('apiKey').value.trim(); }

function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  event.target.classList.add('active');
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
function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

async function apiFetch(url, options = {}) {
  const headers = options.headers || {};
  const key = getApiKey();
  if (key) headers['X-API-Key'] = key;
  options.headers = headers;
  try {
    const res = await fetch(url, options);
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { data = text; }
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

// --- Score rendering ---
function scoreColor(score) {
  if (score >= 70) return 'green';
  if (score >= 40) return 'yellow';
  return 'red';
}
function actionBadgeClass(action) {
  const normalized = String(action || '').toLowerCase();
  if (normalized === 'pursue') return 'badge-green';
  if (normalized === 'review') return 'badge-yellow';
  return 'badge-red';
}
function riskBadgeClass(risk) {
  const normalized = String(risk || '').toLowerCase();
  if (normalized === 'low') return 'badge-green';
  if (normalized === 'medium') return 'badge-yellow';
  return 'badge-red';
}

function renderResult(item) {
  const a = item.analysis || item;
  const scoreValue = Number.isFinite(Number(a.score)) ? Number(a.score) : 0;
  const sc = scoreColor(scoreValue);
  const reqs = (a.key_requirements || []).map(r => `<li>${escapeHtml(r)}</li>`).join('');
  const cr = item.credits_remaining != null ? item.credits_remaining : (a.credits_remaining != null ? a.credits_remaining : null);
  const action = String(a.recommended_action || '');
  const risk = String(a.risk_level || '');
  return `
  <div class="result-card">
    <div class="result-header">
      <div>
        <div class="result-title">${escapeHtml(item.id || 'Analysis Result')}</div>
        <div class="result-meta" style="margin-top:6px">
          <span class="badge ${actionBadgeClass(action)}">⚡ ${escapeHtml(action.toUpperCase())}</span>
          <span class="badge ${riskBadgeClass(risk)}">Risk: ${escapeHtml(risk.toLowerCase())}</span>
          <span class="badge badge-blue">Confidence: ${Math.round((a.confidence_score||0)*100)}%</span>
        </div>
      </div>
      <div class="score-section">
        <div>
          <div class="score-num" style="color:var(--${sc === 'green' ? 'success' : sc === 'yellow' ? 'warning' : 'danger'})">${scoreValue}</div>
          <div class="score-label">/ 100</div>
        </div>
      </div>
    </div>
    <div class="progress-wrap"><div class="progress-bar ${sc}" style="width:${scoreValue}%"></div></div>
    <div class="result-section">
      <div class="result-section-title">Summary</div>
      <div class="result-text">${escapeHtml(a.summary)}</div>
    </div>
    ${reqs ? `<div class="result-section"><div class="result-section-title">Key Requirements</div><ul class="req-list">${reqs}</ul></div>` : ''}
    <div class="result-section">
      <div class="result-section-title">Reasoning</div>
      <div class="result-text">${escapeHtml(a.reasoning)}</div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}

// --- Account ---
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

// --- Analyze text ---
document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const btn = document.getElementById('analyzeBtn');
  const alertEl = document.getElementById('analyzeAlert');
  hideAlert(alertEl);
  const payload = {
    id: `manual-${Date.now()}`,
    title: document.getElementById('title').value || 'Untitled Tender',
    issuer: document.getElementById('issuer').value || 'Unknown Issuer',
    country: document.getElementById('country').value || 'GCC',
    sector: document.getElementById('sector').value || '',
    description: document.getElementById('description').value || ''
  };
  if (!payload.description) { showAlert(alertEl, 'Please enter a tender description.'); return; }
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/tenders/analyze', {
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
  const items = Array.isArray(res.data) ? res.data : [res.data];
  const container = document.getElementById('resultContainer');
  container.style.display = 'block';
  container.innerHTML = '<h2 style="font-size:16px;font-weight:600;margin-bottom:4px">Analysis Results</h2>' + items.map(renderResult).join('');
  if (items[0]?.credits_remaining != null) updateCreditsDisplay(items[0].credits_remaining);
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// --- Upload PDF ---
document.getElementById('uploadBtn').addEventListener('click', async () => {
  const btn = document.getElementById('uploadBtn');
  const alertEl = document.getElementById('uploadAlert');
  hideAlert(alertEl);
  const files = Array.from(document.getElementById('pdfFile').files || []);
  if (!files.length) { showAlert(alertEl, 'Please select at least one file first.'); return; }
  setLoading(btn, true);
  const key = getApiKey();
  const titleOverride = document.getElementById('pdfTitle').value;
  const issuerOverride = document.getElementById('pdfIssuer').value;
  const country = document.getElementById('pdfCountry').value || 'GCC';
  const sector = document.getElementById('pdfSector').value;
  const requests = files.map(async file => {
    const form = new FormData();
    form.append('file', file);
    form.append('title', titleOverride);
    form.append('issuer', issuerOverride);
    form.append('country', country);
    form.append('sector', sector);
    const res = await fetch('/api/v1/tenders/analyze-file', {
      method: 'POST',
      headers: key ? { 'X-API-Key': key } : {},
      body: form
    }).then(async r => {
      const t = await r.text();
      let d; try { d = JSON.parse(t); } catch { d = t; }
      return { ok: r.ok, status: r.status, data: d };
    }).catch(e => ({ ok: false, status: 0, data: { detail: e.message } }));
    return { file, res };
  });
  const settled = await Promise.all(requests);
  const allItems = [];
  const failures = [];
  for (const { file, res } of settled) {
    if (!res.ok) {
      const msg = res.status === 402 ? 'Insufficient credits.' : (res.data?.detail || 'Upload failed.');
      failures.push(`${file.name.replace(/\s+/g, ' ').trim()}: ${msg}`);
      continue;
    }
    const items = Array.isArray(res.data) ? res.data : [res.data];
    allItems.push(...items);
  }
  setLoading(btn, false);
  if (!allItems.length) {
    const msg = failures[0] || 'Upload failed.';
    showAlert(alertEl, msg.includes('Insufficient credits') ? '⚡ Insufficient credits — please top up your account.' : msg, msg.includes('Insufficient credits') ? 'info' : 'error');
    return;
  }
  const container = document.getElementById('resultContainer');
  container.style.display = 'block';
  container.innerHTML = '<h2 style="font-size:16px;font-weight:600;margin-bottom:4px">Analysis Results</h2>' + allItems.map(renderResult).join('');
  if (allItems[allItems.length - 1]?.credits_remaining != null) updateCreditsDisplay(allItems[allItems.length - 1].credits_remaining);
  if (failures.length) {
    showAlert(alertEl, `Analyzed ${allItems.length} file(s). ${failures.length} failed: ${failures.join(' | ')}`, 'info');
  }
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// --- History ---
document.getElementById('loadHistoryBtn').addEventListener('click', loadHistory);
async function loadHistory() {
  const btn = document.getElementById('loadHistoryBtn');
  const alertEl = document.getElementById('historyAlert');
  const list = document.getElementById('historyList');
  hideAlert(alertEl);
  if (!getApiKey()) { showAlert(alertEl, 'Enter your API key first.'); return; }
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/tenders/history');
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed to load history'); return; }
  const items = res.data;
  if (!items.length) { list.innerHTML = '<div class="empty-state"><p>No analysis history yet. Run your first analysis!</p></div>'; return; }
  list.innerHTML = items.map(item => {
    const a = item.analysis?.analysis || item.analysis || {};
    const sc = scoreColor(a.score || 0);
    return `<div class="history-item" onclick="showHistoryDetail(${JSON.stringify(JSON.stringify(item))})">
      <div>
        <div class="history-title">${item.tender_title || item.tender_id}</div>
        <div class="history-meta">${item.created_at?.substring(0,10) || ''} · Score: ${a.score || '?'} · ${a.recommended_action || '?'}</div>
      </div>
      <div class="badge ${actionBadgeClass(a.recommended_action)}">${a.recommended_action?.toUpperCase() || '?'}</div>
    </div>`;
  }).join('');
}

function showHistoryDetail(jsonStr) {
  const item = JSON.parse(jsonStr);
  const analysis = item.analysis;
  // Normalize — history stores full TenderAnalysisResult
  const toRender = analysis?.analysis ? { id: item.tender_id, ...analysis } : { id: item.tender_id, analysis: analysis };
  const container = document.getElementById('resultContainer');
  container.style.display = 'block';
  container.innerHTML = '<h2 style="font-size:16px;font-weight:600;margin-bottom:4px">History Detail</h2>' + renderResult(toRender);
  document.getElementById('section-analyze').classList.add('active');
  document.getElementById('section-history').classList.remove('active');
  document.querySelectorAll('.nav-btn').forEach((b,i) => b.classList.toggle('active', i===0));
  container.scrollIntoView({ behavior: 'smooth' });
}

// --- Billing / Upgrade ---
async function startCheckout(plan) {
  const alertEl = document.getElementById('upgradeAlert');
  hideAlert(alertEl);
  if (!getApiKey()) { showAlert(alertEl, 'Enter your API key (in the Analyze tab) before upgrading.'); return; }
  // Load account to get client_id
  const accRes = await apiFetch('/api/v1/account/me');
  if (!accRes.ok) { showAlert(alertEl, accRes.data?.detail || 'Could not load account. Check your API key.'); return; }
  const clientId = accRes.data.client.id;
  const successUrl = window.location.origin + '/?upgraded=1';
  const cancelUrl = window.location.href;
  const res = await apiFetch('/api/v1/billing/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId, plan, success_url: successUrl, cancel_url: cancelUrl })
  });
  if (!res.ok) {
    const detail = res.data?.detail || 'Checkout failed.';
    if (res.status === 503) {
      showAlert(alertEl, '⚠️ Stripe billing is not configured for this deployment. Contact the administrator to top up credits.', 'info');
    } else {
      showAlert(alertEl, detail);
    }
    return;
  }
  window.location.href = res.data.checkout_url;
}
