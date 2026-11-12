if (getToken()) location.href = "/static/dashboard.html";

const form = document.getElementById("auth-form");
const errorBox = document.getElementById("error");
let registering = false;

document.getElementById("mode-switch").addEventListener("click", (event) => {
  registering = !registering;
  document.getElementById("name-field").hidden = !registering;
  document.getElementById("mode-title").textContent = registering ? "Create account" : "Log in";
  document.getElementById("submit-button").textContent = registering ? "Create account" : "Log in";
  event.target.textContent = registering
    ? "Already have an account? Log in"
    : "New here? Create an account";
  errorBox.textContent = "";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";
  const { name, email, password } = Object.fromEntries(new FormData(form));
  try {
    if (registering) {
      await api("/api/auth/register", { method: "POST", body: { name, email, password } });
    }
    const { token } = await api("/api/auth/login", { method: "POST", body: { email, password } });
    setToken(token);
    location.href = "/static/dashboard.html";
  } catch (error) {
    errorBox.textContent = error.message;
  }
});
