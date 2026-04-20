
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
    const b = document.getElementById('brandName').value.trim();
    const ctx = document.getElementById('brandContext').value.trim();
    const t = document.getElementById('campaignTopic').value.trim();
    if (!b || !ctx || !t) { showAlert(alertEl, 'Brand name, context, and campaign topic are required.'); return null; }
    const platforms = document.getElementById('platforms').value.split(',').map(s=>s.trim()).filter(Boolean);
    return { brand_name: b, brand_context: ctx, campaign_topic: t, platforms,
             posting_frequency: document.getElementById('frequency').value || '3x per week',
             region: document.getElementById('region').value || 'UAE',
             language: document.getElementById('language').value || 'English' };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/content/analyze', {
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
  container.innerHTML = renderContent(res.data);
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
  const res = await apiFetch('/api/v1/content/history');
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
document.getElementById('apiDocs').innerHTML = `<div class="code-block">curl -X POST http://localhost:8004/api/v1/content/analyze \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"brand_name": "Emirates Future", "brand_context": "...", "campaign_topic": "Ramadan 2024"}'</div>`;

function renderContent(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  const calRows = (r.content_calendar||[]).map(e =>
    `<tr><td style="padding:8px;font-size:13px;font-weight:500">${e.day}</td>
     <td style="padding:8px"><span class="badge badge-blue">${e.platform}</span></td>
     <td style="padding:8px;font-size:13px">${e.topic}</td>
     <td style="padding:8px"><span class="badge badge-green">${e.format}</span></td></tr>`).join('');
  const posts = (r.post_concepts||[]).map(p =>
    `<div class="result-card" style="margin-bottom:12px">
      <div class="result-meta" style="margin-bottom:8px">
        <span class="badge badge-blue">${p.platform}</span>
        <span class="badge badge-green">${p.post_type}</span>
        <span style="font-size:12px;color:var(--muted)">${p.best_time}</span>
      </div>
      <div class="result-text">${p.caption}</div>
      <div style="margin-top:8px;font-size:12px;color:var(--primary)">${(p.hashtags||[]).map(h=>'#'+h.replace('#','')).join(' ')}</div>
    </div>`).join('');
  const themes = (r.content_themes||[]).map(t=>`<span class="badge badge-blue" style="margin:2px">${t}</span>`).join('');
  return `<div class="result-card">
    <div class="result-title" style="margin-bottom:16px">Content Plan <span class="badge badge-blue" style="margin-left:8px">Confidence: ${Math.round((r.confidence_score||0)*100)}%</span></div>
    <div class="result-section-title">Content Themes</div>
    <div style="margin-bottom:16px">${themes}</div>
    <div class="result-section-title">Content Calendar</div>
    <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
      <thead><tr><th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">Day</th><th style="padding:8px;font-size:12px;color:var(--muted)">Platform</th><th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">Topic</th><th style="padding:8px;font-size:12px;color:var(--muted)">Format</th></tr></thead>
      <tbody>${calRows}</tbody>
    </table>
    <div class="result-section-title">Post Concepts</div>
    ${posts}
    <div class="result-section">
      <div class="result-section-title">Repurposing Plan</div>
      <div class="result-text">${r.repurposing_plan}</div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}
