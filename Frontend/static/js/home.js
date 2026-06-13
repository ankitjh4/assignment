/* home.js — product grid + floating chat widget */

const PRODUCTS = [
  {
    id: 1,
    name: "Citrus Burst",
    category: "citrus",
    price: 2.49,
    description: "A zesty blend of orange, lemon, and grapefruit — sunshine in a bottle.",
    sugar: 8,
    bulk: true,
    img: "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=400&q=80",
    badge: "Best Seller",
  },
  {
    id: 2,
    name: "Green Zen Smoothie",
    category: "smoothie",
    price: 3.29,
    description: "Spinach, apple, cucumber, and ginger for a clean energy boost.",
    sugar: 5,
    bulk: false,
    img: "https://images.unsplash.com/photo-1610970881699-44a5587cabec?w=400&q=80",
    badge: "Low Sugar",
  },
  {
    id: 3,
    name: "Sparkling Mint",
    category: "sparkling",
    price: 1.99,
    description: "Crisp sparkling water with a cool mint lift. Zero calories.",
    sugar: 0,
    bulk: true,
    img: "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400&q=80",
    badge: "Zero Cal",
  },
  {
    id: 4,
    name: "Mango Tango",
    category: "smoothie",
    price: 3.49,
    description: "Thick, tropical mango and passionfruit with a hint of lime.",
    sugar: 14,
    bulk: false,
    img: "https://images.unsplash.com/photo-1570696516188-ade861b84a49?w=400&q=80",
    badge: null,
  },
  {
    id: 5,
    name: "Berry Bliss",
    category: "smoothie",
    price: 3.19,
    description: "Mixed berry medley packed with antioxidants and natural sweetness.",
    sugar: 11,
    bulk: true,
    img: "https://images.unsplash.com/photo-1553530979-7ee52a2670c4?w=400&q=80",
    badge: "Bulk Available",
  },
  {
    id: 6,
    name: "Lemon Fizz",
    category: "sparkling",
    price: 2.19,
    description: "Sparkling lemon with a subtle elderflower twist.",
    sugar: 6,
    bulk: true,
    img: "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&q=80",
    badge: null,
  },
  {
    id: 7,
    name: "Matcha Zen",
    category: "tea",
    price: 3.99,
    description: "Premium Japanese matcha with oat milk. Calm energy, no crash.",
    sugar: 4,
    bulk: false,
    img: "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?w=400&q=80",
    badge: "Low Sugar",
  },
  {
    id: 8,
    name: "Peach Ice Tea",
    category: "tea",
    price: 2.79,
    description: "Cold-brewed black tea with real peach juice. Refreshingly smooth.",
    sugar: 9,
    bulk: true,
    img: "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80",
    badge: null,
  },
  {
    id: 9,
    name: "Volt Energy",
    category: "energy",
    price: 2.89,
    description: "Natural caffeine from green tea extract + B-vitamins. No crash.",
    sugar: 7,
    bulk: true,
    img: "https://images.unsplash.com/photo-1622543925917-763c34d1a86e?w=400&q=80",
    badge: "New",
  },
  {
    id: 10,
    name: "Watermelon Wave",
    category: "citrus",
    price: 2.69,
    description: "Fresh watermelon juice with a squeeze of lime. Pure summer vibes.",
    sugar: 10,
    bulk: false,
    img: "https://images.unsplash.com/photo-1563746924237-f81d0a479ebe?w=400&q=80",
    badge: null,
  },
];

/* ── Product Grid ─────────────────────────────────────── */

function getBadgeClass(badge) {
  if (!badge) return "";
  const b = badge.toLowerCase();
  if (b.includes("bulk")) return "bulk";
  if (b.includes("sugar") || b.includes("cal")) return "low-sugar";
  return "";
}

function renderProducts(category) {
  const grid = document.getElementById("product-grid");
  if (!grid) return;

  const filtered = category === "all"
    ? PRODUCTS
    : PRODUCTS.filter(p => p.category === category);

  grid.innerHTML = filtered.map(p => {
    const sugarClass = p.sugar <= 5 ? "low" : "";
    const badgeHtml = p.badge
      ? `<span class="product-badge ${getBadgeClass(p.badge)}">${p.badge}</span>`
      : "";

    return `
      <div class="product-card" data-category="${p.category}">
        <div class="product-img-wrap">
          <img src="${p.img}" alt="${p.name}" loading="lazy" />
          ${badgeHtml}
        </div>
        <div class="product-body">
          <div class="product-category">${p.category}</div>
          <div class="product-name">${p.name}</div>
          <div class="product-desc">${p.description}</div>
          <div class="product-footer">
            <span class="product-price">£${p.price.toFixed(2)}</span>
            <span class="product-sugar ${sugarClass}">${p.sugar}g sugar</span>
          </div>
        </div>
      </div>`;
  }).join("");
}

function initProductGrid() {
  const grid = document.getElementById("product-grid");
  if (!grid) return;

  renderProducts("all");

  document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderProducts(btn.dataset.cat);
    });
  });
}

/* ── Floating Chat Widget ─────────────────────────────── */

function initFabChat() {
  const fabToggle = document.getElementById("fab-toggle");
  const fabClose  = document.getElementById("fab-close");
  const fabPanel  = document.getElementById("fab-panel");
  const fabWindow = document.getElementById("fab-window");
  const fabInput  = document.getElementById("fab-input");
  const fabSend   = document.getElementById("fab-send");
  const fabLogin  = document.getElementById("fab-login-hint");
  const iconOpen  = fabToggle ? fabToggle.querySelector(".fab-icon-open") : null;
  const iconClose = fabToggle ? fabToggle.querySelector(".fab-icon-close") : null;

  if (!fabToggle || !fabPanel) return;

  let open = false;

  function openPanel() {
    open = true;
    fabPanel.style.display = "flex";
    fabPanel.style.flexDirection = "column";
    if (iconOpen) iconOpen.style.display = "none";
    if (iconClose) iconClose.style.display = "";
    updateLoginHint();
    fabInput.focus();
  }

  function closePanel() {
    open = false;
    fabPanel.style.display = "none";
    if (iconOpen) iconOpen.style.display = "";
    if (iconClose) iconClose.style.display = "none";
  }

  function updateLoginHint() {
    if (!fabLogin) return;
    if (typeof isLoggedIn === "function" && isLoggedIn()) {
      fabLogin.style.display = "none";
      fabInput.disabled = false;
      fabSend.disabled = false;
      fabInput.placeholder = "Ask about products…";
    } else {
      fabLogin.style.display = "block";
      fabInput.disabled = true;
      fabSend.disabled = true;
      fabInput.placeholder = "Log in to chat";
    }
  }

  function appendMessage(text, role) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    fabWindow.appendChild(div);
    fabWindow.scrollTop = fabWindow.scrollHeight;
  }

  async function sendMessage() {
    const q = fabInput.value.trim();
    if (!q) return;
    fabInput.value = "";
    appendMessage(q, "user");

    const thinkingEl = document.createElement("div");
    thinkingEl.className = "message bot";
    thinkingEl.textContent = "…";
    fabWindow.appendChild(thinkingEl);
    fabWindow.scrollTop = fabWindow.scrollHeight;

    try {
      const resp = await apiFetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await resp.json();
      thinkingEl.textContent = data.answer || "Sorry, no answer returned.";
    } catch (err) {
      thinkingEl.textContent = "Error: could not reach the chatbot.";
    }
    fabWindow.scrollTop = fabWindow.scrollHeight;
  }

  fabToggle.addEventListener("click", () => open ? closePanel() : openPanel());
  fabClose.addEventListener("click", closePanel);

  fabSend.addEventListener("click", sendMessage);
  fabInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // Welcome message
  appendMessage("👋 Hi! I'm the DRINKOO assistant. Ask me anything about products, ingredients, or promotions.", "bot");

  // Auto-open after login redirect (?chat=1)
  if (new URLSearchParams(window.location.search).get("chat") === "1") {
    openPanel();
    history.replaceState(null, "", "/");
  }
}

/* ── Bootstrap ─────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {
  if (typeof updateNav === "function") updateNav();
  initProductGrid();
  initFabChat();
});
