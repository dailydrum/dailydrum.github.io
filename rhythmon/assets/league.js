(async () => {
  const box = document.getElementById('league'); const L = JSON.parse(box.dataset.t);
  try {
    const [res, names] = await Promise.all([fetch(box.dataset.api), fetch(box.dataset.names).then(r => r.json())]);
    if (!res.ok) throw 0;
    const d = await res.json();
    const col = Number(box.dataset.col), joined = col >= 2;
    const name = (code) => { const m = /^w:(\d+):(\d+)$/.exec(code || '');
      if (!m) return code || '';
      const a = names.adjectives[+m[1]], n = names.nouns[+m[2]]; if (!a || !n) return code;
      return joined ? a[col] + n[col] : a[col] + ' ' + n[col]; };
    document.getElementById('players').textContent = L.players.replace('{n}', d.players || 0);
    if (!d.top || !d.top.length) { box.innerHTML = '<p>' + L.empty + '</p>'; return; }
    const rows = d.top.map(p => `<tr><td class="rank">${p.rank}</td><td>${esc(name(p.name))}</td><td>${esc(L.tiers[p.tier] || '')}</td><td class="n">${p.xp}</td></tr>`).join('');
    box.innerHTML = `<div class="table-wrap"><table><thead><tr><th>${L.cols[0]}</th><th>${L.cols[1]}</th><th>${L.cols[2]}</th><th class="n">${L.cols[3]}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  } catch (_) { box.innerHTML = '<p>' + L.error + '</p>'; }
  function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
})();
