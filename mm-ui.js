// Machine Manager — small helpers every tool page uses. Load before the page's own script.
(() => {
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
  const uid = () => Math.random().toString(36).slice(2, 8) + Date.now().toString(36).slice(-4);
  const clone = o => JSON.parse(JSON.stringify(o));

  // The page's #toast: a short message, optionally with one action button ({ label, fn }).
  let toastT;
  function toast(msg, action){
    const t = document.getElementById('toast'); if (!t) return;
    t.textContent = msg; t.classList.toggle('act', !!action);
    if (action){ const b = el('button', '', action.label); b.addEventListener('click', () => { t.classList.remove('show'); action.fn(); }); t.appendChild(b); }
    t.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), action ? 7000 : 2800);
  }
  // Same, but the same message twice in a row (e.g. several live updates at once) shows once.
  let lastSoft = '';
  function toastSoft(msg){ if (msg !== lastSoft){ lastSoft = msg; toast(msg); setTimeout(() => { lastSoft = ''; }, 1500); } }

  window.MMUI = { el, esc, uid, clone, toast, toastSoft };
})();
