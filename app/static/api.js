// Helpers shared by every page: the session token, API calls, and safe page building.
const TOKEN_KEY = "pwm_token";

function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Storage is blocked; the user will simply have to log in again.
  }
}

async function api(path, { method = "GET", body } = {}) {
  const headers = {};
  if (getToken()) headers.Authorization = `Bearer ${getToken()}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const response = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status === 401 && !path.startsWith("/api/auth/log")) {
    setToken(null);
    location.href = "/";
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const error = new Error(typeof data.detail === "string" ? data.detail : "Please check the form");
    error.fields = Array.isArray(data.detail) ? data.detail : [];
    throw error;
  }
  return response.status === 204 ? null : response.json();
}

function rupees(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(value));
}

function signedRupees(value, percent) {
  const sign = Number(value) > 0 ? "+" : "";
  return `${sign}${rupees(value)} (${sign}${percent}%)`;
}

// Builds an element. Text always goes through textContent, so saved data can't inject HTML.
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  Object.assign(node, props);
  node.append(...children);
  return node;
}
