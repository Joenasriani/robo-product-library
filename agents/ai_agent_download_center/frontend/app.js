function getApiKey() { return document.getElementById('apiKey').value.trim(); }
function getAdminToken() { return document.getElementById('adminToken').value.trim(); }

function showSection(name, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  if (btn) btn.classList.add('active');
}
function setLoading(btn, loading) { btn.disabled = loading; btn.classList.toggle('loading', loading); }
function showAlert(el, msg, type='error') { el.className = 'alert show alert-' + type; el.textContent = msg; }
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
  } catch(e) { return { ok: false, status: 0, data: { detail: 'Network error: ' + e.message } }; }
}

async function adminFetch(url, options = {}) {
  const headers = options.headers || {};
  headers['X-Admin-Token'] = getAdminToken();
  options.headers = headers;
  return apiFetch(url, options);
}

// Load catalog on page load
window.addEventListener('load', loadCatalog);

async function loadCatalog() {
  const res = await fetch('/api/v1/catalog').then(r => r.json()).catch(() => []);
  const grid = document.getElementById('catalogGrid');
  if (!res.length) { grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1">No products available.</div>'; return; }
  grid.innerHTML = res.map(p => `
    <div class="card" style="cursor:pointer" onclick="showProduct(${p.id})">
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--primary);margin-bottom:6px">${p.category}</div>
      <div style="font-weight:700;font-size:15px;margin-bottom:6px">${p.name}</div>
      <div style="font-size:13px;color:var(--muted);margin-bottom:12px;line-height:1.5">${p.description.substring(0,100)}...</div>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span class="badge badge-green">v${p.version}</span>
        <span style="font-weight:700;color:var(--text)">AED ${p.price_aed?.toLocaleString()}</span>
      </div>
      ${p.file_size_mb ? `<div style="font-size:11px;color:var(--muted);margin-top:6px">${p.file_size_mb} MB</div>` : ''}
    </div>`).join('');
}

async function showProduct(productId) {
  const res = await fetch(`/api/v1/catalog/${productId}`).then(r => r.json());
  const reqs = (res.requirements||[]).map(r=>`<li>${r}</li>`).join('');
  const files = (res.included_files||[]).map(f=>`<li><code>${f}</code></li>`).join('');
  document.getElementById('modalContent').innerHTML = `
    <div style="font-size:11px;font-weight:600;text-transform:uppercase;color:var(--primary);margin-bottom:8px">${res.category} · v${res.version}</div>
    <h2 style="font-size:20px;font-weight:700;margin-bottom:12px">${res.name}</h2>
    <p style="color:var(--muted);font-size:14px;line-height:1.6;margin-bottom:16px">${res.description}</p>
    <div style="font-size:20px;font-weight:700;color:var(--text);margin-bottom:16px">AED ${res.price_aed?.toLocaleString()}</div>
    ${reqs ? `<div style="margin-bottom:12px"><div class="result-section-title">Requirements</div><ul class="req-list">${reqs}</ul></div>` : ''}
    ${files ? `<div style="margin-bottom:16px"><div class="result-section-title">Included Files</div><ul class="req-list">${files}</ul></div>` : ''}
    <button class="btn btn-primary" onclick="downloadProduct(${res.id})">
      <span class="btn-text">Access Download</span>
    </button>
    <p style="font-size:12px;color:var(--muted);margin-top:8px;text-align:center">Requires active entitlement</p>`;
  document.getElementById('productModal').style.display = 'block';
}

function closeModal() { document.getElementById('productModal').style.display = 'none'; }
window.addEventListener('click', e => { if (e.target === document.getElementById('productModal')) closeModal(); });

async function downloadProduct(productId) {
  if (!getApiKey()) { alert('Please enter your API key first.'); return; }
  const res = await apiFetch(`/api/v1/download/${productId}`);
  if (!res.ok) { alert(res.data?.detail || 'Download failed. You may need an entitlement.'); return; }
  document.getElementById('modalContent').innerHTML += `
    <div class="alert show alert-success" style="margin-top:12px">
      ✓ ${res.data.message || 'Download authorized!'}<br>
      <strong>URL:</strong> ${res.data.download_url}
    </div>`;
}

// Account
document.getElementById('loadAccount').addEventListener('click', async () => {
  const btn = document.getElementById('loadAccount');
  const alertEl = document.getElementById('accountAlert');
  setLoading(btn, true);
  hideAlert(alertEl);
  const res = await apiFetch('/api/v1/account/me');
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed to load account'); return; }
  const c = res.data.client;
  document.getElementById('accName').textContent = c.name;
  document.getElementById('accountInfo').style.display = 'block';
  document.getElementById('creditsBadge').textContent = c.name;
  document.getElementById('creditsBadge').style.display = 'inline-flex';
});

// Downloads
document.getElementById('loadDownloadsBtn').addEventListener('click', async () => {
  const btn = document.getElementById('loadDownloadsBtn');
  const alertEl = document.getElementById('downloadsAlert');
  if (!getApiKey()) { showAlert(alertEl, 'Enter your API key first.'); return; }
  setLoading(btn, true);
  const res = await apiFetch('/api/v1/my-downloads');
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed'); return; }
  const items = res.data;
  if (!items.length) { document.getElementById('downloadsList').innerHTML = '<div class="empty-state"><p>No entitlements yet.</p></div>'; return; }
  document.getElementById('downloadsList').innerHTML = items.map(e => `
    <div class="history-item">
      <div>
        <div class="history-title">${e.product_name}</div>
        <div class="history-meta">Product ID: ${e.product_id} · Granted: ${e.granted_at?.substring(0,10)}</div>
      </div>
      <span class="badge badge-green">${e.status}</span>
    </div>`).join('');
});

// Admin: grant entitlement
document.getElementById('grantBtn').addEventListener('click', async () => {
  const btn = document.getElementById('grantBtn');
  const alertEl = document.getElementById('grantAlert');
  hideAlert(alertEl);
  if (!getAdminToken()) { showAlert(alertEl, 'Enter admin token.'); return; }
  const clientId = parseInt(document.getElementById('grantClientId').value);
  const productId = parseInt(document.getElementById('grantProductId').value);
  if (!clientId || !productId) { showAlert(alertEl, 'Client ID and Product ID are required.'); return; }
  setLoading(btn, true);
  const res = await adminFetch('/api/v1/admin/entitlements', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({client_id: clientId, product_id: productId})
  });
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed'); return; }
  showAlert(alertEl, `✓ Entitlement granted! ID: ${res.data.entitlement_id}`, 'success');
});

// Admin: load entitlements
document.getElementById('loadEntitlementsBtn').addEventListener('click', async () => {
  const btn = document.getElementById('loadEntitlementsBtn');
  setLoading(btn, true);
  const res = await adminFetch('/api/v1/admin/entitlements');
  setLoading(btn, false);
  if (!res.ok) return;
  const el = document.getElementById('entitlementsList');
  el.innerHTML = (res.data||[]).map(e => `
    <div class="history-item">
      <div>
        <div class="history-title">${e.product_name} → ${e.client_name}</div>
        <div class="history-meta">Client ID: ${e.client_id} · ${e.granted_at?.substring(0,10)}</div>
      </div>
      <span class="badge badge-green">${e.status}</span>
    </div>`).join('') || '<div class="empty-state"><p>No entitlements.</p></div>';
});

// Admin: clients
document.getElementById('loadClientsBtn').addEventListener('click', async () => {
  const btn = document.getElementById('loadClientsBtn');
  setLoading(btn, true);
  const res = await adminFetch('/api/v1/admin/clients');
  setLoading(btn, false);
  if (!res.ok) return;
  const el = document.getElementById('clientsList');
  el.innerHTML = `<table style="width:100%;border-collapse:collapse">
    <thead><tr>${['ID','Name','Email','Plan','Credits'].map(h=>`<th style="text-align:left;padding:8px;font-size:12px;color:var(--muted)">${h}</th>`).join('')}</tr></thead>
    <tbody>${(res.data||[]).map(c=>`<tr>
      <td style="padding:8px;font-size:13px">${c.id}</td>
      <td style="padding:8px;font-size:13px">${c.name}</td>
      <td style="padding:8px;font-size:13px">${c.email||'—'}</td>
      <td style="padding:8px"><span class="badge badge-blue">${c.plan}</span></td>
      <td style="padding:8px;font-size:13px">${c.credits_remaining}/${c.credits_total}</td>
    </tr>`).join('')}</tbody>
  </table>`;
});
