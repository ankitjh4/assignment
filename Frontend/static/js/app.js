/* DRINKOO — shared Alpine.js stores and helpers */

const API = '/api'

/* ─── HTTP helpers ─────────────────────────────────────────────────── */
function getToken() { return localStorage.getItem('drinkoo_token') }
function getUser()  {
  try { return JSON.parse(localStorage.getItem('drinkoo_user') || 'null') }
  catch { return null }
}

async function apiFetch(path, opts = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (opts.body instanceof FormData) delete headers['Content-Type']

  const res = await fetch(API + path, { ...opts, headers })

  if (res.status === 401) {
    localStorage.removeItem('drinkoo_token')
    localStorage.removeItem('drinkoo_user')
    window.location.href = '/login'
    return null
  }
  return res
}

/* ─── Global auth Alpine component (used in base.html) ─────────────── */
function auth() {
  return {
    user: getUser(),
    init() { this.user = getUser() },
    logout() {
      localStorage.removeItem('drinkoo_token')
      localStorage.removeItem('drinkoo_user')
      this.user = null
      window.location.href = '/'
    }
  }
}

/* ─── Login page ────────────────────────────────────────────────────── */
function loginPage() {
  return {
    email: '', password: '', error: '', loading: false,
    async submit() {
      this.error = ''; this.loading = true
      try {
        const form = new URLSearchParams({ username: this.email, password: this.password })
        const res = await fetch(API + '/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form
        })
        const data = await res.json()
        if (!res.ok) { this.error = data.detail || 'Login failed.'; return }

        localStorage.setItem('drinkoo_token', data.access_token)

        const me = await (await apiFetch('/auth/me')).json()
        localStorage.setItem('drinkoo_user', JSON.stringify(me))
        window.location.href = '/chat'
      } catch { this.error = 'Network error. Please try again.' }
      finally  { this.loading = false }
    }
  }
}

/* ─── Signup page ───────────────────────────────────────────────────── */
function signupPage() {
  return {
    fullName: '', email: '', password: '', confirm: '', error: '', loading: false,
    async submit() {
      this.error = ''
      if (this.password !== this.confirm) { this.error = 'Passwords do not match.'; return }
      if (this.password.length < 8)       { this.error = 'Password must be at least 8 characters.'; return }
      this.loading = true
      try {
        const res = await fetch(API + '/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email, password: this.password, full_name: this.fullName })
        })
        const data = await res.json()
        if (!res.ok) { this.error = data.detail || 'Signup failed.'; return }

        // Auto-login after signup
        const form = new URLSearchParams({ username: this.email, password: this.password })
        const lr = await fetch(API + '/auth/login', {
          method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: form
        })
        const ld = await lr.json()
        localStorage.setItem('drinkoo_token', ld.access_token)
        const me = await (await apiFetch('/auth/me')).json()
        localStorage.setItem('drinkoo_user', JSON.stringify(me))
        window.location.href = '/chat'
      } catch { this.error = 'Network error. Please try again.' }
      finally  { this.loading = false }
    }
  }
}

/* ─── Chat page ─────────────────────────────────────────────────────── */
function chatPage() {
  return {
    user: getUser(),
    messages: [],
    input: '',
    loading: false,
    error: '',
    suggested: [
      'Which DRINKOO products are low sugar?',
      'What ingredients are in the citrus drinks?',
      'Are there active promotions for sparkling beverages?',
      'What should I do if my order arrives damaged?',
    ],

    init() {
      if (!getToken()) { window.location.href = '/login'; return }
      const name = this.user?.full_name?.split(' ')[0] || 'there'
      this.messages = [{ role: 'bot', text: `Hi ${name}! 👋 Ask me anything about DRINKOO products, ingredients, promotions, or support.` }]
    },

    async send(text) {
      const q = (text || this.input).trim()
      if (!q || this.loading) return
      this.input = ''; this.error = ''
      this.messages.push({ role: 'user', text: q })
      this.loading = true
      this.$nextTick(() => this.scrollBottom())

      try {
        const res = await apiFetch('/chat', {
          method: 'POST',
          body: JSON.stringify({ question: q })
        })
        if (!res) return
        const data = await res.json()
        if (!res.ok) { this.error = data.detail || 'Error.'; return }
        this.messages.push({ role: 'bot', text: data.answer, context: data.retrieved_context })
      } catch { this.error = 'Network error. Please try again.' }
      finally  { this.loading = false; this.$nextTick(() => this.scrollBottom()) }
    },

    handleKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send() }
    },

    scrollBottom() {
      const el = document.getElementById('chat-bottom')
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    }
  }
}

/* ─── Upload page ───────────────────────────────────────────────────── */
function uploadPage() {
  return {
    file: null, preview: null, result: null, error: '', loading: false,
    ALLOWED: ['image/jpeg','image/png','image/gif','image/webp'],
    MAX_MB: 5,

    init() { if (!getToken()) window.location.href = '/login' },

    pick(e) {
      const f = e.target.files?.[0] || e.dataTransfer?.files?.[0]
      this.error = ''; this.result = null
      if (!f) return
      if (!this.ALLOWED.includes(f.type)) { this.error = `File type "${f.type}" not allowed.`; return }
      if (f.size > this.MAX_MB * 1024 * 1024) { this.error = `File too large (max ${this.MAX_MB} MB).`; return }
      this.file = f
      this.preview = URL.createObjectURL(f)
    },

    drop(e) { e.preventDefault(); this.pick({ target: { files: e.dataTransfer.files } }) },

    async upload() {
      if (!this.file) return
      this.loading = true; this.error = ''; this.result = null
      const fd = new FormData(); fd.append('file', this.file)
      try {
        const res = await apiFetch('/upload', { method: 'POST', body: fd, headers: {} })
        if (!res) return
        const data = await res.json()
        if (!res.ok) { this.error = data.detail || 'Upload failed.'; return }
        this.result = data
      } catch { this.error = 'Network error.' }
      finally  { this.loading = false }
    },

    reset() { this.file = null; this.preview = null; this.result = null; this.error = '' }
  }
}

/* ─── Status page ───────────────────────────────────────────────────── */
function statusPage() {
  return {
    data: null, error: '', loading: true, lastChecked: null,

    async init() { await this.refresh() },

    async refresh() {
      this.loading = true; this.error = ''
      try {
        const res = await fetch(API + '/status')
        this.data = await res.json()
        this.lastChecked = new Date().toLocaleTimeString()
      } catch { this.error = 'Could not reach the DRINKOO API.' }
      finally  { this.loading = false }
    },

    badgeClass(v) {
      const ok = ['ok','ready','healthy'].includes(v)
      return ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
    },
    badgeText(v) {
      return ['ok','ready','healthy'].includes(v) ? '● OK' : '● Issue'
    }
  }
}
