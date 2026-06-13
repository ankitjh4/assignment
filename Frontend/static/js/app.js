/* DRINKOO – shared auth utilities and API helpers */

const TOKEN_KEY = "drinkoo_token";

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }
function isLoggedIn() { return !!getToken(); }

function updateNav() {
  const loginLink = document.getElementById("nav-login");
  const signupLink = document.getElementById("nav-signup");
  const logoutLink = document.getElementById("nav-logout");
  const chatLink = document.getElementById("nav-chat");

  if (isLoggedIn()) {
    if (loginLink) loginLink.style.display = "none";
    if (signupLink) signupLink.style.display = "none";
    if (logoutLink) logoutLink.style.display = "";
    if (chatLink) chatLink.style.display = "";
  } else {
    if (loginLink) loginLink.style.display = "";
    if (signupLink) signupLink.style.display = "";
    if (logoutLink) logoutLink.style.display = "none";
    if (chatLink) chatLink.style.display = "none";
  }
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "/login.html";
  }
}

async function apiFetch(url, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    window.location.href = "/login.html";
    return null;
  }
  return res;
}

function showAlert(elId, message, type = "error") {
  const el = document.getElementById(elId);
  if (!el) return;
  el.textContent = message;
  el.className = `alert alert-${type} show`;
}

function hideAlert(elId) {
  const el = document.getElementById(elId);
  if (el) el.className = "alert";
}

/* ── Page inits ──────────────────────────────────────── */

function initSignup() {
  updateNav();
  const form = document.getElementById("signup-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("signup-alert");
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Signing up…';

    const body = {
      username: form.username.value.trim(),
      email: form.email.value.trim(),
      password: form.password.value,
    };

    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        showAlert("signup-alert", data.detail || "Signup failed.", "error");
      } else {
        showAlert("signup-alert", "Account created! Redirecting to login…", "success");
        setTimeout(() => window.location.href = "/login.html", 1200);
      }
    } catch {
      showAlert("signup-alert", "Network error. Please try again.", "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Create Account";
    }
  });
}

function initLogin() {
  updateNav();
  const form = document.getElementById("login-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("login-alert");
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Logging in…';

    const body = {
      username: form.username.value.trim(),
      password: form.password.value,
    };

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        showAlert("login-alert", data.detail || "Login failed.", "error");
      } else {
        setToken(data.access_token);
        window.location.href = "/?chat=1";
      }
    } catch {
      showAlert("login-alert", "Network error. Please try again.", "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Log In";
    }
  });
}

function initChat() {
  requireAuth();
  updateNav();

  const window_ = document.getElementById("chat-window");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");
  if (!window_ || !input || !sendBtn) return;

  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    window_.appendChild(div);
    window_.scrollTop = window_.scrollHeight;
    return div;
  }

  function appendSqlPanel(sqlQuery, sqlRows) {
    if (!sqlQuery && (!sqlRows || sqlRows.length === 0)) return;

    const details = document.createElement("details");
    details.className = "sql-panel";

    const summary = document.createElement("summary");
    const rowCount = sqlRows ? sqlRows.length : 0;
    summary.textContent = `SQL Query  •  ${rowCount} row${rowCount !== 1 ? "s" : ""}`;
    details.appendChild(summary);

    if (sqlQuery) {
      const pre = document.createElement("pre");
      pre.className = "sql-code";
      pre.textContent = sqlQuery;
      details.appendChild(pre);
    }

    if (sqlRows && sqlRows.length > 0) {
      const wrap = document.createElement("div");
      wrap.className = "sql-table-wrap";

      const table = document.createElement("table");
      table.className = "sql-table";

      // Header row
      const thead = document.createElement("thead");
      const headerRow = document.createElement("tr");
      Object.keys(sqlRows[0]).forEach((col) => {
        const th = document.createElement("th");
        th.textContent = col;
        headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);

      // Data rows
      const tbody = document.createElement("tbody");
      sqlRows.forEach((row) => {
        const tr = document.createElement("tr");
        Object.values(row).forEach((val) => {
          const td = document.createElement("td");
          td.textContent = val === null ? "—" : String(val);
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      wrap.appendChild(table);
      details.appendChild(wrap);
    }

    window_.appendChild(details);
    window_.scrollTop = window_.scrollHeight;
  }

  appendMessage("Hello! I'm the DRINKOO assistant. Ask me about our products, ingredients, promotions, or orders.", "bot");

  async function sendMessage() {
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    sendBtn.disabled = true;

    appendMessage(question, "user");
    const loadingDiv = appendMessage("Thinking…", "bot loading");

    try {
      const res = await apiFetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({ question }),
      });
      if (!res) return;
      const data = await res.json();
      loadingDiv.remove();
      if (!res.ok) {
        appendMessage("Sorry, I encountered an error. Please try again.", "bot");
      } else {
        appendMessage(data.answer, "bot");
        appendSqlPanel(data.sql_query, data.sql_rows);
      }
    } catch {
      loadingDiv.remove();
      appendMessage("Network error. Please check your connection.", "bot");
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
}

function initUpload() {
  requireAuth();
  updateNav();

  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("upload-file");
  const uploadBox = document.getElementById("upload-box");
  if (!form || !fileInput) return;

  uploadBox?.addEventListener("click", () => fileInput.click());

  uploadBox?.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.classList.add("drag-over");
  });
  uploadBox?.addEventListener("dragleave", () => uploadBox.classList.remove("drag-over"));
  uploadBox?.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadBox.classList.remove("drag-over");
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      updateFileLabel();
    }
  });

  function updateFileLabel() {
    const label = document.getElementById("file-label");
    if (label && fileInput.files.length) {
      label.textContent = fileInput.files[0].name;
    }
  }

  fileInput.addEventListener("change", updateFileLabel);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("upload-alert");
    const btn = form.querySelector("button[type=submit]");
    if (!fileInput.files.length) {
      showAlert("upload-alert", "Please select a file first.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Uploading…';

    try {
      const token = getToken();
      const res = await fetch("/api/upload", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        showAlert("upload-alert", data.detail || "Upload failed.", "error");
      } else {
        showAlert("upload-alert", `Uploaded: ${data.filename} (${(data.size / 1024).toFixed(1)} KB)`, "success");
        form.reset();
        const label = document.getElementById("file-label");
        if (label) label.textContent = "Click or drag an image here";
      }
    } catch {
      showAlert("upload-alert", "Network error. Please try again.", "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Upload Image";
    }
  });
}

function initStatus() {
  updateNav();
  fetch("/api/status")
    .then((r) => r.json())
    .then((data) => {
      function setStatus(id, ok, label) {
        const dot = document.getElementById(id + "-dot");
        const text = document.getElementById(id + "-text");
        if (dot) dot.className = `status-dot ${ok ? "green" : "red"}`;
        if (text) text.textContent = label;
      }
      setStatus("api", data.api_healthy, data.api_healthy ? "Healthy" : "Degraded");
      setStatus("db", data.database_connected, data.database_connected ? "Connected" : "Disconnected");
      setStatus("rag", data.rag_ready, data.rag_ready ? "Ready" : "API key missing");

      const verEl = document.getElementById("app-version");
      if (verEl) verEl.textContent = `v${data.version} (${data.environment})`;
      const tsEl = document.getElementById("status-timestamp");
      if (tsEl) tsEl.textContent = new Date(data.timestamp).toLocaleString();
    })
    .catch(() => {
      ["api", "db", "rag"].forEach((id) => {
        const dot = document.getElementById(id + "-dot");
        if (dot) dot.className = "status-dot red";
        const text = document.getElementById(id + "-text");
        if (text) text.textContent = "Error";
      });
    });
}

function initLogout() {
  const btn = document.getElementById("logout-btn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    clearToken();
    window.location.href = "/";
  });
}
