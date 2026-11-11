// Draws the navigation bar at the top of every logged-in page.
(async function () {
  if (!getToken()) {
    location.href = "/";
    return;
  }
  const pages = [
    ["Dashboard", "dashboard.html"],
    ["Real Estate", "real-estate.html"],
    ["Gold", "gold.html"],
    ["Stocks", "stocks.html"],
    ["Cash", "cash.html"],
  ];
  const nav = document.getElementById("nav");
  const current = location.pathname.split("/").pop();
  const addLink = ([label, page]) =>
    nav.append(el("a", {
      textContent: label,
      href: `/static/${page}`,
      className: page === current ? "active" : "",
    }));

  pages.forEach(addLink);
  const logout = el("button", { textContent: "Log out", className: "link", type: "button" });
  logout.addEventListener("click", async () => {
    await api("/api/auth/logout", { method: "POST" }).catch(() => {});
    setToken(null);
    location.href = "/";
  });
  nav.append(logout);

  const user = await api("/api/auth/me");
  if (user.is_admin) {
    logout.before(el("a", {
      textContent: "Admin",
      href: "/static/admin.html",
      className: current === "admin.html" ? "active" : "",
    }));
  }
})();
