(function () {
  var dropzone = document.getElementById('dropzone');
  var input = document.getElementById('upload-file');
  var form = document.getElementById('upload-form');
  var errorEl = document.getElementById('upload-error');
  var result = document.getElementById('upload-result');
  var ACCEPTED = ['image/png', 'image/jpeg', 'image/webp'];
  var MAX_BYTES = 5 * 1024 * 1024;

  ['dragenter', 'dragover'].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) { e.preventDefault(); dropzone.classList.add('hover'); });
  });
  ['dragleave', 'drop'].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) { e.preventDefault(); dropzone.classList.remove('hover'); });
  });
  dropzone.addEventListener('drop', function (e) {
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
    }
  });

  function validate(file) {
    if (!file) return 'Pick an image file.';
    if (ACCEPTED.indexOf(file.type) === -1) return 'Only PNG, JPEG, and WebP are accepted.';
    if (file.size > MAX_BYTES) return 'File exceeds the 5 MB limit.';
    return null;
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    errorEl.textContent = '';
    var file = input.files && input.files[0];
    var problem = validate(file);
    if (problem) { errorEl.textContent = problem; return; }
    var fd = new FormData();
    fd.append('file', file);
    try {
      var response = await fetch('/api/upload', { method: 'POST', body: fd, credentials: 'include' });
      var data = await response.json();
      if (!response.ok) {
        errorEl.textContent = data.detail || 'Upload failed';
        if (response.status === 401) { setTimeout(function () { window.location.href = '/login'; }, 500); }
        return;
      }
      document.getElementById('r-filename').textContent = data.filename;
      document.getElementById('r-ctype').textContent = data.content_type;
      document.getElementById('r-size').textContent = data.size_bytes + ' bytes';
      var img = document.getElementById('r-preview');
      img.src = data.url;
      result.hidden = false;
      window.drinkoo.toast('Image uploaded', 'success');
    } catch (err) {
      errorEl.textContent = err.message || 'Upload failed';
    }
  });
})();
