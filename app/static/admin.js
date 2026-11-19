const errorBox = document.getElementById("error");

async function changeStatus(user) {
  errorBox.textContent = "";
  const action = user.is_active ? "deactivate" : "reactivate";
  try {
    await api(`/api/admin/users/${user.id}/${action}`, { method: "POST" });
    await loadUsers();
  } catch (error) {
    errorBox.textContent = error.message;
  }
}

async function loadUsers() {
  const users = await api("/api/admin/users");
  const head = el("thead", {}, el("tr", {}, ...["Name", "Email", "Role", "Status", "Action"]
    .map((title) => el("th", { textContent: title }))));
  const rows = users.map((user) => {
    const button = el("button", {
      textContent: user.is_active ? "Deactivate" : "Reactivate",
      type: "button",
      className: user.is_active ? "link danger" : "link",
    });
    button.addEventListener("click", () => changeStatus(user));
    return el("tr", {},
      el("td", { textContent: user.name }),
      el("td", { textContent: user.email }),
      el("td", { textContent: user.is_admin ? "Administrator" : "User" }),
      el("td", { textContent: user.is_active ? "Active" : "Deactivated" }),
      el("td", {}, button));
  });
  document.getElementById("user-table").replaceChildren(head, el("tbody", {}, ...rows));
}

loadUsers().catch((error) => {
  errorBox.textContent = error.message;
});
