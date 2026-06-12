(function () {
  var api = window.drinkoo.api;
  var toast = window.drinkoo.toast;

  var signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      var errorEl = document.getElementById('signup-error');
      errorEl.textContent = '';
      var form = new FormData(signupForm);
      try {
        await api('/api/auth/signup', {
          method: 'POST',
          body: {
            email: form.get('email'),
            password: form.get('password'),
            full_name: form.get('full_name'),
          },
        });
        toast('Welcome to DRINKOO!', 'success');
        setTimeout(function () { window.location.href = '/chat'; }, 200);
      } catch (err) {
        errorEl.textContent = err.message || 'Signup failed';
      }
    });
  }

  var loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      var errorEl = document.getElementById('login-error');
      errorEl.textContent = '';
      var form = new FormData(loginForm);
      try {
        await api('/api/auth/login', {
          method: 'POST',
          body: { email: form.get('email'), password: form.get('password') },
        });
        toast('Logged in', 'success');
        setTimeout(function () { window.location.href = '/chat'; }, 200);
      } catch (err) {
        errorEl.textContent = err.message || 'Login failed';
      }
    });
  }
})();
