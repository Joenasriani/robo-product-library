
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
    const p = document.getElementById('platform').value.trim();
    const n = document.getElementById('packageName').value.trim();
    if (!p || !n) { showAlert(alertEl, 'Platform and package name are required.'); return null; }
    return { target_platform: p, package_name: n,
             package_version: document.getElementById('packageVersion').value || null,
             os_version: document.getElementById('osVersion').value || null,
             environment_type: document.getElementById('envType').value,
             constraints: document.getElementById('constraints').value || null };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/install/analyze', {
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
  container.innerHTML = renderInstall(res.data);
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
  const res = await apiFetch('/api/v1/install/history');
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
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">POST /api/v1/install/analyze — Generate installation guide</div>
  <div class="code-block">curl -X POST http://localhost:8006/api/v1/install/analyze \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
  "target_platform": "ROS2 Humble on Ubuntu 22.04",
  "package_name": "nav2_bringup",
  "package_version": "1.1.5",
  "os_version": "Ubuntu 22.04 LTS",
  "environment_type": "production",
  "constraints": "air-gapped network, no sudo access"
}'</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /api/v1/install/history — List analysis history</div>
  <div class="code-block">curl http://localhost:8006/api/v1/install/history \\
  -H "X-API-Key: YOUR_API_KEY"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /api/v1/account/me — Get account &amp; credit balance</div>
  <div class="code-block">curl http://localhost:8006/api/v1/account/me \\
  -H "X-API-Key: YOUR_API_KEY"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /health — Health check (no auth)</div>
  <div class="code-block">curl http://localhost:8006/health</div>
</div>
`;

function compatBadge(s) { return s==='compatible'?'badge-green':s==='incompatible'?'badge-red':'badge-yellow'; }

function renderInstall(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  const prereqs = (r.prerequisites||[]).map(p=>`<li>${p}</li>`).join('');
  const steps = (r.install_steps||[]).map(s =>
    `<div style="border-left:3px solid var(--primary);padding-left:14px;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span style="background:var(--primary);color:#fff;border-radius:4px;padding:2px 8px;font-size:12px;font-weight:700">Step ${s.step_number}</span>
        <span style="font-weight:600;font-size:14px">${s.title}</span>
      </div>
      ${s.command ? `<div style="background:#1e293b;color:#94a3b8;padding:10px;border-radius:6px;font-family:monospace;font-size:13px;margin:8px 0">${s.command}</div>` : ''}
      <div style="font-size:13px;color:var(--muted)">${s.description}</div>
      ${s.notes ? `<div style="font-size:12px;color:var(--warning);margin-top:4px">⚠️ ${s.notes}</div>` : ''}
    </div>`).join('');
  const compat = (r.compatibility_notes||[]).map(c =>
    `<tr><td style="padding:8px;font-size:13px">${c.component}</td>
     <td style="padding:8px"><span class="badge ${compatBadge(c.status)}">${c.status}</span></td>
     <td style="padding:8px;font-size:13px;color:var(--muted)">${c.details}</td></tr>`).join('');
  return `<div class="result-card">
    <div class="result-header">
      <div class="result-title">Installation Guide</div>
      <div class="result-meta">
        <span class="badge badge-blue">~${r.estimated_install_time}</span>
        <span class="badge badge-green">Confidence: ${Math.round((r.confidence_score||0)*100)}%</span>
      </div>
    </div>
    ${prereqs ? `<div class="result-section"><div class="result-section-title">Prerequisites</div><ul class="req-list">${prereqs}</ul></div>` : ''}
    <div class="result-section">
      <div class="result-section-title">Installation Steps</div>
      ${steps}
    </div>
    ${compat ? `<div class="result-section"><div class="result-section-title">Compatibility Notes</div>
      <table style="width:100%;border-collapse:collapse">
        <thead><tr><th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">Component</th><th style="padding:8px;font-size:12px;color:var(--muted)">Status</th><th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">Details</th></tr></thead>
        <tbody>${compat}</tbody>
      </table></div>` : ''}
    <div class="result-section">
      <div class="result-section-title">Troubleshooting Guide</div>
      <div class="result-text">${r.troubleshooting_guide}</div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}
