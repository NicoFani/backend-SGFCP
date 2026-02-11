const $ = (id) => document.getElementById(id);

let theme = localStorage.getItem('sgfcp_theme') || 'light';

function initTheme() {
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon();
}

function updateThemeIcon() {
  const sunIcon = document.getElementById('sunIcon');
  const moonIcon = document.getElementById('moonIcon');
  if (theme === 'dark') {
    sunIcon.style.display = 'none';
    moonIcon.style.display = 'block';
  } else {
    sunIcon.style.display = 'block';
    moonIcon.style.display = 'none';
  }
}

function toggleTheme() {
  theme = theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('sgfcp_theme', theme);
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon();
}

function setStatus(message, tone = "info") {
  const status = $("status");
  status.textContent = message;
  status.dataset.tone = tone;
}

function getBaseUrl() {
  const stored = localStorage.getItem("sgfcp_base_url") || "";
  const value = stored || "http://localhost:5000";
  localStorage.setItem("sgfcp_base_url", value);
  return value.replace(/\/$/, "");
}

function setToken(token) {
  localStorage.setItem("sgfcp_token", token);
}

function clearToken() {
  localStorage.removeItem("sgfcp_token");
}

async function login() {
  const baseUrl = getBaseUrl();
  const email = $("email").value.trim();
  const password = $("password").value.trim();

  if (!email || !password) {
    setStatus("Completa email y password", "warn");
    return;
  }

  setStatus("Autenticando...", "info");
  try {
    const response = await fetch(`${baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error("Login invalido");
    }

    const data = await response.json();
    if (!data.user || !data.user.is_admin) {
      clearToken();
      setStatus("Acceso denegado. Solo admin", "warn");
      return;
    }

    setToken(data.access_token);
    setStatus("Login OK. Redireccionando...", "ok");
    window.location.href = "index.html";
  } catch (error) {
    setStatus("No se pudo autenticar", "error");
  }
}


$("loginBtn").addEventListener("click", login);
$("clearBtn").addEventListener("click", () => {
  $("email").value = "";
  $("password").value = "";
  setStatus("Formulario limpio", "info");
});
$("themeToggle").addEventListener("click", toggleTheme);

initTheme();
