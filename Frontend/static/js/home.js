(function () {
  var api = window.drinkoo.api;
  var grid = document.getElementById('featured-grid');
  if (!grid) return;

  function tag(text, color) {
    var el = document.createElement('span');
    el.className = 'tag ' + (color || '');
    el.textContent = text;
    return el;
  }

  async function load() {
    try {
      var data = await api('/api/catalog/products');
      var pick = data.products.slice(0, 6);
      grid.innerHTML = '';
      pick.forEach(function (p) {
        var node = document.createElement('article');
        node.className = 'product-card';
        var bottle = document.createElement('div');
        bottle.className = 'bottle ' + (p.category || '');
        node.appendChild(bottle);
        var h = document.createElement('h4');
        h.textContent = p.name;
        node.appendChild(h);
        var tagRow = document.createElement('div');
        tagRow.className = 'tag-row';
        tagRow.appendChild(tag(p.category, 'cyan'));
        if (p.is_sparkling) tagRow.appendChild(tag('sparkling', 'orange'));
        if (p.sugar_g_per_100ml < 4) tagRow.appendChild(tag('low sugar', 'green'));
        node.appendChild(tagRow);
        var desc = document.createElement('p');
        desc.className = 'desc';
        desc.textContent = p.description || '';
        node.appendChild(desc);
        grid.appendChild(node);
      });
    } catch (err) {
      grid.innerHTML = '<p class="muted">Featured picks unavailable.</p>';
    }
  }
  load();
})();
