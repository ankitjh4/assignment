(function () {
  var api = window.drinkoo.api;
  var grid = document.getElementById('promo-grid');

  async function load() {
    try {
      var data = await api('/api/catalog/promotions?only_active=true');
      grid.innerHTML = '';
      if (!data.promotions.length) {
        grid.innerHTML = '<p class="muted">No active promotions right now.</p>';
        return;
      }
      data.promotions.forEach(function (p) {
        var node = document.createElement('article');
        node.className = 'promo-card';
        node.innerHTML =
          '<span class="code">' + p.code + '</span>' +
          '<h3>' + p.title + '</h3>' +
          '<p>' + p.description + '</p>' +
          '<p class="muted">Discount ' + p.discount_pct + '% &middot; ' + (p.applies_to_category || 'all categories') + ' &middot; ends ' + p.ends_at + '</p>';
        grid.appendChild(node);
      });
    } catch (err) {
      grid.innerHTML = '<p class="error">' + (err.message || 'Failed to load') + '</p>';
    }
  }
  load();
})();
