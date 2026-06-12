(function () {
  var api = window.drinkoo.api;
  var raw = document.getElementById('status-raw');
  var grid = document.getElementById('status-grid');

  function setValue(key, value, cls) {
    var node = grid.querySelector('[data-key="' + key + '"]');
    if (!node) return;
    node.textContent = value;
    node.classList.remove('ok', 'bad', 'warn');
    if (cls) node.classList.add(cls);
  }
  function setDetail(key, value) {
    var node = grid.querySelector('[data-key="' + key + '"]');
    if (node) node.textContent = value;
  }

  async function refresh() {
    try {
      var data = await api('/api/status');
      raw.textContent = JSON.stringify(data, null, 2);
      setValue('api', 'Operational', 'ok');
      var db = data.components.database;
      setValue('database', db.ok ? 'Operational' : 'Down', db.ok ? 'ok' : 'bad');
      setDetail('database-detail', db.ok ? db.products + ' products, ' + db.users + ' users' : (db.error || 'Connection failed'));
      var rag = data.components.rag;
      setValue('rag', rag.ok ? 'Ready' : 'Building', rag.ok ? 'ok' : 'warn');
      setDetail('rag-detail', rag.documents + ' documents indexed');
      var llm = data.components.llm;
      setValue('llm', llm.configured ? 'Configured' : 'Offline fallback', llm.configured ? 'ok' : 'warn');
      setDetail('llm-detail', 'mode: ' + llm.mode);
    } catch (err) {
      raw.textContent = 'Status fetch failed: ' + err.message;
      setValue('api', 'Down', 'bad');
    }
  }

  refresh();
  setInterval(refresh, 15000);
})();
