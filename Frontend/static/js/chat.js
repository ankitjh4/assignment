(function () {
  var api = window.drinkoo.api;
  var window_ = document.getElementById('chat-window');
  var form = document.getElementById('chat-form');
  var input = document.getElementById('chat-message');
  var errorEl = document.getElementById('chat-error');
  var contextList = document.getElementById('context-list');
  var contextPanel = document.getElementById('context-panel');
  var contextToggle = document.getElementById('toggle-context');
  var grid = document.querySelector('.chat-grid');
  var sessionId = null;

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function addUser(text) {
    var msg = el('div', 'msg user');
    msg.appendChild(el('div', 'avatar', 'YOU'));
    var bubble = el('div', 'bubble');
    bubble.appendChild(el('span', '', text));
    msg.appendChild(bubble);
    window_.appendChild(msg);
    window_.scrollTop = window_.scrollHeight;
  }

  function addThinking() {
    var msg = el('div', 'msg assistant pending');
    msg.appendChild(el('div', 'avatar', 'DR'));
    var bubble = el('div', 'bubble');
    var t = el('div', 'thinking');
    t.appendChild(el('span'));
    t.appendChild(el('span'));
    t.appendChild(el('span'));
    bubble.appendChild(t);
    msg.appendChild(bubble);
    window_.appendChild(msg);
    window_.scrollTop = window_.scrollHeight;
    return msg;
  }

  function addAnswer(text, citations, refused) {
    var msg = el('div', 'msg assistant');
    msg.appendChild(el('div', 'avatar', 'DR'));
    var bubble = el('div', refused ? 'bubble refusal' : 'bubble');
    bubble.appendChild(el('p', '', text));
    if (citations && citations.length) {
      var row = el('div', 'citations');
      citations.forEach(function (c) {
        row.appendChild(el('span', 'cite-chip', c.citation));
      });
      bubble.appendChild(row);
    }
    msg.appendChild(bubble);
    window_.appendChild(msg);
    window_.scrollTop = window_.scrollHeight;
  }

  function renderContext(citations) {
    contextList.innerHTML = '';
    if (!citations || !citations.length) {
      var li = document.createElement('li');
      li.className = 'empty muted';
      li.textContent = 'No relevant context found.';
      contextList.appendChild(li);
      return;
    }
    citations.forEach(function (c) {
      var li = document.createElement('li');
      var head = document.createElement('div');
      head.innerHTML = '<span class="src">' + c.source + ':' + c.source_id + '</span> <span class="muted">(score ' + c.score + ')</span>';
      var body = document.createElement('div');
      body.className = 'muted';
      body.textContent = c.body;
      li.appendChild(head);
      li.appendChild(body);
      contextList.appendChild(li);
    });
  }

  document.querySelectorAll('.suggestions .chip').forEach(function (btn) {
    btn.addEventListener('click', function () {
      input.value = btn.textContent || '';
      form.dispatchEvent(new Event('submit', { cancelable: true }));
    });
  });

  if (contextToggle) {
    contextToggle.addEventListener('click', function () {
      grid.classList.toggle('no-context');
      var hidden = grid.classList.contains('no-context');
      contextToggle.innerHTML =
        '<span class="material-symbols-outlined" style="font-size:18px;">' +
        (hidden ? 'visibility_off' : 'visibility') +
        '</span> ' + (hidden ? 'Show context' : 'Hide context');
    });
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    errorEl.textContent = '';
    var message = (input.value || '').trim();
    if (!message) return;
    addUser(message);
    input.value = '';
    var pending = addThinking();

    try {
      var data = await api('/api/chat', {
        method: 'POST',
        body: { message: message, session_id: sessionId },
      });
      sessionId = data.session_id;
      window_.removeChild(pending);
      addAnswer(data.answer, data.citations, data.refused);
      renderContext(data.citations);
    } catch (err) {
      window_.removeChild(pending);
      errorEl.textContent = err.message || 'Chat failed';
      if (err.status === 401) {
        setTimeout(function () { window.location.href = '/login'; }, 600);
      }
    }
  });
})();
