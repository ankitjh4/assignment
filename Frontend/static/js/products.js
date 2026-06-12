(function () {
  var api = window.drinkoo.api;
  var grid = document.getElementById('product-grid');
  var fCat = document.getElementById('filter-category');
  var fSpark = document.getElementById('filter-sparkling');
  var fBulk = document.getElementById('filter-bulk');
  var fSugar = document.getElementById('filter-max-sugar');

  function bottleClass(category) {
    return ['cola','tea','water','kids','sports','berry','herbal','coffee','citrus'].indexOf(category) >= 0 ? category : '';
  }

  function card(p) {
    var node = document.createElement('article');
    node.className = 'product-card';
    var bottle = document.createElement('div');
    bottle.className = 'bottle ' + bottleClass(p.category);
    node.appendChild(bottle);
    var h = document.createElement('h4');
    h.textContent = p.name;
    node.appendChild(h);
    var tags = document.createElement('div');
    tags.className = 'tag-row';
    tags.appendChild(tagEl(p.category, 'cyan'));
    if (p.is_sparkling) tags.appendChild(tagEl('sparkling', 'orange'));
    if (p.supports_bulk) tags.appendChild(tagEl('bulk-friendly', 'green'));
    if (p.sugar_g_per_100ml === 0) tags.appendChild(tagEl('zero sugar', 'green'));
    else if (p.sugar_g_per_100ml < 4) tags.appendChild(tagEl('low sugar', 'green'));
    node.appendChild(tags);
    var desc = document.createElement('p');
    desc.className = 'desc';
    desc.textContent = p.description || '';
    node.appendChild(desc);
    var meta = document.createElement('div');
    meta.className = 'meta-row';
    meta.innerHTML = '<span>Sugar ' + p.sugar_g_per_100ml + ' g / 100ml</span><span class="price">$' + (p.price_cents / 100).toFixed(2) + '</span>';
    node.appendChild(meta);
    return node;
  }

  function tagEl(text, color) {
    var el = document.createElement('span');
    el.className = 'tag ' + (color || '');
    el.textContent = text;
    return el;
  }

  async function refresh() {
    var params = new URLSearchParams();
    if (fCat.value) params.set('category', fCat.value);
    if (fSpark.checked) params.set('sparkling', 'true');
    if (fBulk.checked) params.set('bulk', 'true');
    if (fSugar.value) params.set('max_sugar', fSugar.value);
    try {
      var data = await api('/api/catalog/products?' + params.toString());
      grid.innerHTML = '';
      data.products.forEach(function (p) { grid.appendChild(card(p)); });
      if (!data.products.length) {
        grid.innerHTML = '<p class="muted">No products match these filters.</p>';
      }
    } catch (err) {
      grid.innerHTML = '<p class="error">' + (err.message || 'Failed to load') + '</p>';
    }
  }

  [fCat, fSpark, fBulk, fSugar].forEach(function (el) {
    el.addEventListener('change', refresh);
  });
  refresh();
})();
