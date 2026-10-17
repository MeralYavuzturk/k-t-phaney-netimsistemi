const API_BASE = window.location.origin.includes("5500") || window.location.origin.includes("8080")
  ? "http://127.0.0.1:8000/api"
  : `${window.location.origin}/api`;

const state = {
  token: localStorage.getItem("library_token"),
  role: localStorage.getItem("library_role"),
  name: localStorage.getItem("library_name"),
};

const els = {
  toast: document.getElementById("toast"),
  sessionInfo: document.getElementById("sessionInfo"),
  logoutBtn: document.getElementById("logoutBtn"),
  authView: document.getElementById("authView"),
  adminView: document.getElementById("adminView"),
  studentView: document.getElementById("studentView"),
  loginForm: document.getElementById("loginForm"),
  registerForm: document.getElementById("registerForm"),
  booksGrid: document.getElementById("booksGrid"),
  searchInput: document.getElementById("searchInput"),
  searchBtn: document.getElementById("searchBtn"),
  refreshBooksBtn: document.getElementById("refreshBooksBtn"),
  loansList: document.getElementById("loansList"),
  addBookForm: document.getElementById("addBookForm"),
  overdueBtn: document.getElementById("overdueBtn"),
  overdueReport: document.getElementById("overdueReport"),
};

function toast(msg, type = "success") {
  els.toast.textContent = msg;
  els.toast.className = `toast ${type}`;
  els.toast.classList.remove("hidden");
  clearTimeout(els._toastTimer);
  els._toastTimer = setTimeout(() => els.toast.classList.add("hidden"), 4000);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg;
    if (typeof data.detail === "string") {
      msg = data.detail;
    } else if (Array.isArray(data.detail)) {
      // Pydantic validation hataları: [{loc, msg, type}, ...]
      msg = data.detail.map(e => e.msg || JSON.stringify(e)).join(" · ");
    } else if (data.detail) {
      msg = JSON.stringify(data.detail);
    } else {
      msg = "İstek başarısız";
    }
    throw new Error(msg);
  }
  return data;
}

function setSession(token, role, name) {
  state.token = token;
  state.role = role;
  state.name = name;
  localStorage.setItem("library_token", token);
  localStorage.setItem("library_role", role);
  localStorage.setItem("library_name", name);
  refreshUI();
}

function clearSession() {
  state.token = state.role = state.name = null;
  localStorage.removeItem("library_token");
  localStorage.removeItem("library_role");
  localStorage.removeItem("library_name");
  refreshUI();
}

function refreshUI() {
  const loggedIn = Boolean(state.token);
  const isAdmin = state.role === "admin";
  const isStudent = state.role === "student";

  els.sessionInfo.classList.toggle("hidden", !loggedIn);
  els.logoutBtn.classList.toggle("hidden", !loggedIn);

  // Sol panel içerikleri: sadece ilgili view göster
  els.authView.classList.toggle("hidden", loggedIn);
  els.adminView.classList.toggle("hidden", !isAdmin);
  els.studentView.classList.toggle("hidden", !isStudent);

  if (loggedIn) {
    els.sessionInfo.textContent = `${state.name} (${isAdmin ? "Yönetici" : "Öğrenci"})`;
    loadBooks();
    if (isStudent) {
      loadMyLoans();
    } else {
      els.loansList.innerHTML = "";
      els.overdueReport.classList.add("hidden");
    }
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("tr-TR");
}

async function loadBooks(q = "") {
  const query = q ? `?q=${encodeURIComponent(q)}` : "";
  const books = await api(`/books${query}`);
  els.booksGrid.innerHTML = books
    .map(
      (b) => `
    <article class="book-card">
      <h3>${escapeHtml(b.title)}</h3>
      <div class="meta">${escapeHtml(b.author)} · ${escapeHtml(b.category || "Genel")}</div>
      <div class="meta">ISBN: ${escapeHtml(b.isbn)}</div>
      <div class="${b.available_copies > 0 ? "stock-ok" : "stock-no"}">
        Stok: ${b.available_copies} / ${b.total_copies}
      </div>
      ${
        state.role === "student" && b.available_copies > 0
          ? `<button class="btn primary" data-borrow="${b.id}">Ödünç Al</button>`
          : ""
      }
    </article>`
    )
    .join("");

  els.booksGrid.querySelectorAll("[data-borrow]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await api("/loans/borrow", { method: "POST", body: JSON.stringify({ book_id: Number(btn.dataset.borrow) }) });
        toast("Kitap ödünç alındı");
        loadBooks(els.searchInput.value.trim());
        loadMyLoans();
      } catch (e) {
        toast(e.message, "error");
      }
    });
  });
}

async function loadMyLoans() {
  const loans = await api("/loans/me");
  els.loansList.innerHTML = loans
    .map((l) => {
      const statusClass = l.status === "overdue" ? "overdue" : l.status === "active" ? "active" : "returned";
      const statusLabel = l.status === "overdue" ? "Gecikmiş" : l.status === "active" ? "Aktif" : "İade";
      const returnBtn =
        l.status !== "returned"
          ? `<button class="btn ghost" data-return="${l.id}">İade Et</button>`
          : "";
      return `<div class="loan-item">
        <div>
          <strong>${escapeHtml(l.book_title || "Kitap")}</strong>
          <div class="meta">Alınış: ${formatDate(l.borrowed_at)} · Son: ${formatDate(l.due_date)}</div>
        </div>
        <span class="badge ${statusClass}">${statusLabel}</span>
        ${returnBtn}
      </div>`;
    })
    .join("");

  els.loansList.querySelectorAll("[data-return]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await api(`/loans/${btn.dataset.return}/return`, { method: "POST" });
        toast("İade tamamlandı");
        loadBooks(els.searchInput.value.trim());
        loadMyLoans();
      } catch (e) {
        toast(e.message, "error");
      }
    });
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const isLogin = tab.dataset.tab === "login";
    els.loginForm.classList.toggle("hidden", !isLogin);
    els.registerForm.classList.toggle("hidden", isLogin);
  });
});

els.loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: fd.get("email"),
        password: fd.get("password"),
        as_admin: fd.get("as_admin") === "on",
      }),
    });
    setSession(data.access_token, data.role, data.display_name);
    toast("Giriş başarılı");
  } catch (err) {
    toast(err.message, "error");
  }
});

els.registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const data = await api("/auth/register", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(fd.entries())),
    });
    setSession(data.access_token, data.role, data.display_name);
    toast("Kayıt tamamlandı");
  } catch (err) {
    toast(err.message, "error");
  }
});

els.logoutBtn.addEventListener("click", () => {
  clearSession();
  toast("Çıkış yapıldı");
});

els.searchBtn.addEventListener("click", () => loadBooks(els.searchInput.value.trim()).catch((e) => toast(e.message, "error")));
els.refreshBooksBtn.addEventListener("click", () => {
  els.searchInput.value = "";
  loadBooks().catch((e) => toast(e.message, "error"));
});

els.addBookForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = Object.fromEntries(fd.entries());

  // Tip dönüşümleri
  payload.total_copies = Number(payload.total_copies) || 1;
  // Boş string alanları null'a çevir
  if (!payload.description) payload.description = null;
  if (!payload.category) payload.category = null;

  const btn = e.target.querySelector("button[type=submit]");
  btn.disabled = true;
  btn.textContent = "Ekleniyor...";
  try {
    await api("/books", { method: "POST", body: JSON.stringify(payload) });
    e.target.reset();
    toast("✅ Kitap eklendi");
    loadBooks();
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Kitap Ekle";
  }
});

els.overdueBtn.addEventListener("click", async () => {
  try {
    const rows = await api("/loans/reports/overdue");
    if (!rows.length) {
      els.overdueReport.textContent = "Gecikmiş ödünç yok.";
    } else {
      els.overdueReport.innerHTML = `<table style="width:100%;border-collapse:collapse">
        <tr><th align="left">Öğrenci</th><th>Kitap</th><th>Gecikme</th></tr>
        ${rows
          .map(
            (r) =>
              `<tr><td>${escapeHtml(r.student_name)} (${escapeHtml(r.student_number)})</td><td>${escapeHtml(r.book_title)}</td><td>${r.days_overdue} gün</td></tr>`
          )
          .join("")}
      </table>`;
    }
    els.overdueReport.classList.remove("hidden");
  } catch (err) {
    toast(err.message, "error");
  }
});

refreshUI();
if (!state.token) {
  loadBooks().catch(() => {});
}
