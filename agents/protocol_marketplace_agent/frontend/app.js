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

function riskBadge(r) { return r==='low'?'badge-green':r==='high'?'badge-red':'badge-yellow'; }
function catColor(c) {
  const m = {Royal:'badge-red','Privacy & Security':'badge-red',Healthcare:'badge-blue',Hospitality:'badge-green',Retail:'badge-yellow'};
  return m[c] || 'badge-blue';
}

window.addEventListener('load', loadCatalog);

async function loadCatalog() {
  const products = await fetch('/api/v1/products').then(r => r.json()).catch(() => []);
  const grid = document.getElementById('catalogGrid');
  if (!products.length) { grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1">No protocols available.</div>'; return; }
  grid.innerHTML = products.map(p => `
    <div class="card" style="cursor:pointer;transition:box-shadow .2s" onmouseenter="this.style.boxShadow='0 4px 20px rgba(37,99,235,.15)'" onmouseleave="this.style.boxShadow=''" onclick="showProduct(${p.id})">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
        <span class="badge ${catColor(p.category)}">${p.category}</span>
        <span class="badge ${riskBadge(p.risk_level)}" style="font-size:11px">${p.risk_level} risk</span>
      </div>
      <div style="font-weight:700;font-size:15px;margin-bottom:6px;line-height:1.3">${p.name}</div>
      <div style="font-size:12px;color:var(--muted);margin-bottom:10px">📍 ${p.region} · v${p.version}</div>
      <div style="font-size:13px;color:var(--muted);line-height:1.5;margin-bottom:14px">${p.description.substring(0,120)}...</div>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:700;font-size:17px;color:var(--text)">AED ${p.price_aed?.toLocaleString()}</span>
        <button class="btn btn-primary" style="width:auto;margin:0;padding:7px 14px;font-size:13px" onclick="event.stopPropagation();openInquiry(${p.id},'${p.name}',${p.price_aed})">Inquire / Buy</button>
      </div>
    </div>`).join('');
}

async function showProduct(productId) {
  const p = await fetch(`/api/v1/products/${productId}`).then(r => r.json()).catch(() => null);
  if (!p) return;
  const hw = (p.hardware_requirements||[]).map(h=>`<li>${h}</li>`).join('');
  const files = (p.included_files||[]).map(f=>`<li><code>${f}</code></li>`).join('');
  document.getElementById('modalContent').innerHTML = `
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
      <span class="badge ${catColor(p.category)}">${p.category}</span>
      <span class="badge ${riskBadge(p.risk_level)}">${p.risk_level} risk</span>
      <span class="badge badge-blue">v${p.version}</span>
      <span style="font-size:13px;color:var(--muted)">📍 ${p.region}</span>
    </div>
    <h2 style="font-size:20px;font-weight:700;margin-bottom:12px">${p.name}</h2>
    <p style="color:var(--muted);font-size:14px;line-height:1.6;margin-bottom:16px">${p.description}</p>
    <div style="font-size:22px;font-weight:700;color:var(--text);margin-bottom:20px">AED ${p.price_aed?.toLocaleString()}</div>
    ${hw ? `<div style="margin-bottom:12px"><div class="result-section-title">Hardware Requirements</div><ul class="req-list">${hw}</ul></div>` : ''}
    ${files ? `<div style="margin-bottom:20px"><div class="result-section-title">Included Files</div><ul class="req-list">${files}</ul></div>` : ''}
    <button class="btn btn-primary" onclick="closeModal();openInquiry(${p.id},'${p.name}',${p.price_aed})">
      <span class="btn-text">Inquire / Buy →</span>
    </button>
    <p style="font-size:12px;color:var(--muted);text-align:center;margin-top:8px">Delivery: ${p.delivery_type} · Response within 1 business day</p>`;
  document.getElementById('productModal').style.display = 'block';
}

function closeModal() { document.getElementById('productModal').style.display = 'none'; }
window.addEventListener('click', e => { if (e.target === document.getElementById('productModal')) closeModal(); });

function openInquiry(productId, productName, price) {
  document.getElementById('inquiryProductId').value = productId;
  document.getElementById('inquiryProductInfo').innerHTML = `<strong>${productName}</strong> — AED ${price?.toLocaleString()}`;
  document.getElementById('inquiryModal').style.display = 'block';
  hideAlert(document.getElementById('inquiryAlert'));
}
function closeInquiryModal() { document.getElementById('inquiryModal').style.display = 'none'; }
window.addEventListener('click', e => { if (e.target === document.getElementById('inquiryModal')) closeInquiryModal(); });

document.getElementById('submitInquiryBtn').addEventListener('click', async () => {
  const btn = document.getElementById('submitInquiryBtn');
  const alertEl = document.getElementById('inquiryAlert');
  hideAlert(alertEl);
  const productId = parseInt(document.getElementById('inquiryProductId').value);
  const name = document.getElementById('inquiryName').value.trim();
  const email = document.getElementById('inquiryEmail').value.trim();
  const org = document.getElementById('inquiryOrg').value.trim();
  if (!name || !email || !org) { showAlert(alertEl, 'Name, email, and organization are required.'); return; }
  setLoading(btn, true);
  const res = await fetch('/api/v1/inquiries', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ product_id: productId, buyer_name: name, buyer_email: email,
      buyer_organization: org, message: document.getElementById('inquiryMessage').value || null,
      deployment_context: document.getElementById('inquiryContext').value || null })
  }).then(async r => { const t = await r.text(); let d; try{d=JSON.parse(t);}catch{d=t;} return {ok:r.ok,data:d}; })
    .catch(e => ({ok:false,data:{detail:e.message}}));
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Submission failed.'); return; }
  showAlert(alertEl, `✓ Inquiry #${res.data.inquiry_id} submitted! We'll respond within 1 business day.`, 'success');
  document.getElementById('inquiryName').value = '';
  document.getElementById('inquiryEmail').value = '';
  document.getElementById('inquiryOrg').value = '';
  document.getElementById('inquiryMessage').value = '';
  document.getElementById('inquiryContext').value = '';
});

// My Entitlements
document.getElementById('loadEntitlementsBtn').addEventListener('click', async () => {
  const btn = document.getElementById('loadEntitlementsBtn');
  const alertEl = document.getElementById('entitlementsAlert');
  const email = document.getElementById('buyerEmail').value.trim();
  if (!email) { showAlert(alertEl, 'Enter your email address.'); return; }
  hideAlert(alertEl);
  setLoading(btn, true);
  const res = await fetch(`/api/v1/my-entitlements?email=${encodeURIComponent(email)}`).then(async r => {
    const t = await r.text(); let d; try{d=JSON.parse(t);}catch{d=t;} return {ok:r.ok,data:d};
  });
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed'); return; }
  const items = res.data;
  const list = document.getElementById('entitlementsList');
  if (!items.length) { list.innerHTML = '<div class="empty-state"><p>No protocol access found for this email.</p></div>'; return; }
  list.innerHTML = items.map(e => `
    <div class="history-item">
      <div>
        <div class="history-title">${e.product_name}</div>
        <div class="history-meta">Granted: ${e.granted_at?.substring(0,10)} ${e.expires_at ? '· Expires: '+e.expires_at.substring(0,10) : ''}</div>
      </div>
      <span class="badge badge-green">${e.status}</span>
    </div>`).join('');
});

// Admin: load inquiries
document.getElementById('loadInquiriesBtn').addEventListener('click', async () => {
  const btn = document.getElementById('loadInquiriesBtn');
  setLoading(btn, true);
  const res = await fetch('/api/v1/admin/inquiries', { headers: {'X-Admin-Token': getAdminToken()} })
    .then(async r => {const t=await r.text();let d;try{d=JSON.parse(t);}catch{d=t;}return{ok:r.ok,data:d};});
  setLoading(btn, false);
  if (!res.ok) { document.getElementById('inquiriesList').innerHTML = '<p style="color:var(--danger);font-size:13px">Failed. Check admin token.</p>'; return; }
  const el = document.getElementById('inquiriesList');
  el.innerHTML = (res.data||[]).map(i => `
    <div style="border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div style="font-weight:600;font-size:14px">#${i.id} — ${i.product_name}</div>
          <div style="font-size:12px;color:var(--muted);margin-top:2px">${i.buyer_name} · ${i.buyer_organization}</div>
          <div style="font-size:12px;color:var(--muted)">${i.buyer_email}</div>
        </div>
        <span class="badge ${i.status==='approved'?'badge-green':i.status==='pending'?'badge-yellow':'badge-red'}">${i.status}</span>
      </div>
      ${i.message ? `<div style="font-size:13px;color:var(--muted);margin-top:8px">${i.message}</div>` : ''}
    </div>`).join('') || '<div class="empty-state"><p>No inquiries.</p></div>';
});

// Admin: approve inquiry
document.getElementById('approveBtn').addEventListener('click', async () => {
  const btn = document.getElementById('approveBtn');
  const alertEl = document.getElementById('approveAlert');
  hideAlert(alertEl);
  const inquiryId = parseInt(document.getElementById('approveInquiryId').value);
  if (!inquiryId) { showAlert(alertEl, 'Enter inquiry ID.'); return; }
  setLoading(btn, true);
  const res = await fetch(`/api/v1/admin/inquiries/${inquiryId}/approve`, {
    method: 'POST',
    headers: {'Content-Type':'application/json','X-Admin-Token': getAdminToken()},
    body: JSON.stringify({inquiry_id: inquiryId, delivery_notes: document.getElementById('deliveryNotes').value || null})
  }).then(async r => {const t=await r.text();let d;try{d=JSON.parse(t);}catch{d=t;}return{ok:r.ok,data:d};});
  setLoading(btn, false);
  if (!res.ok) { showAlert(alertEl, res.data?.detail || 'Failed'); return; }
  showAlert(alertEl, `✓ Approved! Entitlement ID: ${res.data.entitlement_id}`, 'success');
});
