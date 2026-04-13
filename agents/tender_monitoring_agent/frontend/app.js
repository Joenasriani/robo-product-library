
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
    const sectors = document.getElementById('sectors').value.split('\n').map(s=>s.trim()).filter(Boolean);
    const keywords = document.getElementById('keywords').value.split('\n').map(s=>s.trim()).filter(Boolean);
    const profile = document.getElementById('companyProfile').value.trim();
    if (!sectors.length || !keywords.length || !profile) { showAlert(alertEl, 'Sectors, keywords, and company profile are required.'); return null; }
    const countries = document.getElementById('countries').value.split(',').map(s=>s.trim()).filter(Boolean);
    const excl = document.getElementById('exclusions').value.split(',').map(s=>s.trim()).filter(Boolean);
    return { target_sectors: sectors, keywords, company_profile: profile,
             countries: countries.length ? countries : ['UAE', 'Saudi Arabia'],
             budget_range: document.getElementById('budgetRange').value || null,
             exclusion_keywords: excl.length ? excl : null };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/monitoring/analyze', {
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
  container.innerHTML = renderMonitoring(res.data);
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
  const res = await apiFetch('/api/v1/monitoring/history');
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
document.getElementById('apiDocs').innerHTML = ``;

function actionColor(a) { return a==='pursue'?'badge-green':a==='monitor'?'badge-yellow':'badge-red'; }
function scoreColor(s) { return s >= 70 ? 'green' : s >= 40 ? 'yellow' : 'red'; }

function renderMonitoring(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  const disclaimer = r.disclaimer || 'Results are AI-generated research leads. Verify on official procurement portals before acting.';
  const opps = (r.matched_opportunities||[]).map(o => {
    const sc = scoreColor(o.match_score);
    return `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap">
        <div>
          <div style="font-weight:600;font-size:14px">${o.title}</div>
          <div style="font-size:12px;color:var(--muted);margin-top:4px">${o.country} · ${o.sector} · ${o.source_type} ${o.estimated_value ? '· ' + o.estimated_value : ''}</div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <span class="badge ${actionColor(o.recommended_action)}">${o.recommended_action?.toUpperCase()}</span>
          <div style="text-align:center"><div style="font-size:20px;font-weight:700;color:var(--${sc==='green'?'success':sc==='yellow'?'warning':'danger'})">${o.match_score}</div><div style="font-size:10px;color:var(--muted)">match</div></div>
        </div>
      </div>
      <div style="margin-top:8px;font-size:13px;color:var(--muted)">${o.match_rationale}</div>
    </div>`;
  }).join('');
  return `<div class="result-card">
    <div class="result-header">
      <div class="result-title">Monitoring Report</div>
      <div class="result-meta">
        <span class="badge badge-blue">${r.shortlist_count} shortlisted</span>
        <span class="badge badge-green">Confidence: ${Math.round((r.confidence_score||0)*100)}%</span>
        <span class="badge badge-yellow">🤖 AI Research</span>
      </div>
    </div>
    <div style="background:var(--surface);border:1px solid var(--warning,#f59e0b);border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:12px;color:var(--muted)">
      ⚠️ <strong>Disclaimer:</strong> ${disclaimer}
    </div>
    <div class="result-section">
      <div class="result-section-title">Summary</div>
      <div class="result-text">${r.monitoring_summary}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Matched Opportunities</div>
      ${opps}
    </div>
    <div class="result-section">
      <div class="result-section-title">Top Opportunity Rationale</div>
      <div class="result-text">${r.top_opportunity_rationale}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Next Recommended Action</div>
      <div class="result-text"><strong>${r.next_recommended_action}</strong></div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}
