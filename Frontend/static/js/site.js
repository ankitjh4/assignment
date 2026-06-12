(function () {
  function toast(message, kind) {
    var container = document.getElementById('toasts');
    if (!container) return;
    var el = document.createElement('div');
    el.className = 'toast ' + (kind || '');
    el.textContent = message;
    container.appendChild(el);
    setTimeout(function () { el.style.opacity = '0'; }, 2200);
    setTimeout(function () { container.removeChild(el); }, 2800);
  }

  async function api(path, opts) {
    opts = opts || {};
    opts.credentials = 'include';
    opts.headers = Object.assign({ 'Accept': 'application/json' }, opts.headers || {});
    if (opts.body && typeof opts.body !== 'string' && !(opts.body instanceof FormData)) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(opts.body);
    }
    var response = await fetch(path, opts);
    var text = await response.text();
    var data;
    try { data = text ? JSON.parse(text) : null; } catch (err) { data = text; }
    if (!response.ok) {
      var error = new Error((data && data.detail) || ('Request failed: ' + response.status));
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  }

  window.drinkoo = { api: api, toast: toast };

  var logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async function () {
      try {
        await api('/api/auth/logout', { method: 'POST' });
        toast('Logged out', 'success');
        setTimeout(function () { window.location.href = '/'; }, 200);
      } catch (err) {
        toast(err.message || 'Logout failed', 'error');
      }
    });
  }
})();
