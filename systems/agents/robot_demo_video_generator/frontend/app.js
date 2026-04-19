
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
    const n = document.getElementById('robotName').value.trim();
    const t = document.getElementById('robotType').value.trim();
    const features = document.getElementById('featureList').value.split('\n').map(s=>s.trim()).filter(Boolean);
    if (!n || !t || !features.length) { showAlert(alertEl, 'Robot name, type, and at least one feature are required.'); return null; }
    return { robot_name: n, robot_type: t, feature_list: features,
             visual_style: document.getElementById('visualStyle').value || 'professional corporate',
             target_duration: parseInt(document.getElementById('duration').value) || 90,
             target_audience: document.getElementById('audience').value || 'enterprise buyers',
             use_case: document.getElementById('useCase').value || null };
  })();
  if (!payload) return;
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/video/analyze', {
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
  container.innerHTML = renderVideo(res.data);
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
  const res = await apiFetch('/api/v1/video/history');
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
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">POST /api/v1/video/analyze — Generate robot demo video production plan</div>
  <div class="code-block">curl -X POST http://localhost:8005/api/v1/video/analyze \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
  "robot_name": "UR5e",
  "robot_type": "cobot",
  "feature_list": ["6-DOF articulation", "force-torque sensing", "tool changer"],
  "visual_style": "cinematic",
  "target_duration": 90,
  "target_audience": "industrial automation buyers",
  "use_case": "automotive assembly line"
}'</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /api/v1/video/history — List analysis history</div>
  <div class="code-block">curl http://localhost:8005/api/v1/video/history \\
  -H "X-API-Key: YOUR_API_KEY"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /api/v1/account/me — Get account &amp; credit balance</div>
  <div class="code-block">curl http://localhost:8005/api/v1/account/me \\
  -H "X-API-Key: YOUR_API_KEY"</div>
</div>
<div style="margin-bottom:20px">
  <div style="font-weight:600;margin-bottom:8px;font-size:14px">GET /health — Health check (no auth)</div>
  <div class="code-block">curl http://localhost:8005/health</div>
</div>
`;

function renderVideo(data) {
  const r = data.result || data;
  const cr = data.credits_remaining;
  const scenes = (r.storyboard||[]).map(s =>
    `<div style="border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <div style="background:var(--primary);color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0">${s.scene_number}</div>
        <div style="font-weight:600">${s.title}</div>
        <span class="badge badge-blue">${s.duration_seconds}s</span>
        <span style="font-size:12px;color:var(--muted)">${s.camera_angle}</span>
      </div>
      <div class="result-text">${s.description}</div>
      <div style="margin-top:8px;background:#1e293b;color:#94a3b8;padding:10px;border-radius:6px;font-size:12px;font-family:monospace">${s.ai_image_prompt}</div>
    </div>`).join('');
  return `<div class="result-card">
    <div class="result-header">
      <div class="result-title">Video Storyboard</div>
      <div class="result-meta">
        <span class="badge badge-blue">~${r.total_estimated_duration}s total</span>
        <span class="badge badge-green">Confidence: ${Math.round((r.confidence_score||0)*100)}%</span>
      </div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Scene Plan</div>
      <div class="result-text">${r.scene_plan_summary}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Scenes</div>
      ${scenes}
    </div>
    <div class="result-section">
      <div class="result-section-title">Voiceover Script</div>
      <div class="result-text" style="background:#f8faff;padding:12px;border-radius:8px;border:1px solid #dbeafe">${r.voiceover_script}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Production Notes</div>
      <div class="result-text">${r.production_notes}</div>
    </div>
    ${cr != null ? `<div class="credits-note">⚡ ${cr} credits remaining</div>` : ''}
  </div>`;
}
