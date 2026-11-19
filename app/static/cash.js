const accountForm = document.getElementById("account-form");
const transactionForm = document.getElementById("transaction-form");
const picker = document.getElementById("account-picker");
const accountError = document.getElementById("error");
const transactionError = document.getElementById("transaction-error");

const ACCOUNT_TYPES = { cash: "Cash in hand", bank: "Bank account", wallet: "Wallet" };

function tableHead(...titles) {
  return el("thead", {}, el("tr", {}, ...titles.map((title) => el("th", { textContent: title }))));
}

async function loadAccounts() {
  const accounts = await api("/api/cash");
  const selected = picker.value;
  const rows = accounts.map((account) => {
    const remove = el("button", { textContent: "Delete", type: "button", className: "link danger" });
    remove.addEventListener("click", async () => {
      if (!confirm("Delete this account and its history?")) return;
      await api(`/api/cash/${account.id}`, { method: "DELETE" });
      await loadAccounts();
    });
    return el("tr", {},
      el("td", { textContent: account.name }),
      el("td", { textContent: ACCOUNT_TYPES[account.type] }),
      el("td", { textContent: rupees(account.balance) }),
      el("td", {}, remove));
  });
  document.getElementById("account-table").replaceChildren(
    tableHead("Name", "Type", "Balance", "Actions"), el("tbody", {}, ...rows));
  picker.replaceChildren(...accounts.map((account) =>
    el("option", { value: account.id, textContent: account.name })));
  if (selected) picker.value = selected;
  await loadTransactions();
}

async function loadTransactions() {
  const table = document.getElementById("transaction-table");
  if (!picker.value) {
    table.replaceChildren();
    return;
  }
  const transactions = await api(`/api/cash/${picker.value}/transactions`);
  const rows = transactions.map((item) => el("tr", {},
    el("td", { textContent: new Date(`${item.created_at}Z`).toLocaleString("en-IN") }),
    el("td", { textContent: item.type }),
    el("td", { textContent: rupees(item.amount) }),
    el("td", { textContent: item.note })));
  table.replaceChildren(tableHead("Date", "Type", "Amount", "Note"), el("tbody", {}, ...rows));
}

accountForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  accountError.textContent = "";
  try {
    const body = Object.fromEntries(new FormData(accountForm));
    await api("/api/cash", { method: "POST", body });
    accountForm.reset();
    await loadAccounts();
  } catch (error) {
    accountError.textContent = error.message;
  }
});

transactionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  transactionError.textContent = "";
  const { account, ...body } = Object.fromEntries(new FormData(transactionForm));
  try {
    await api(`/api/cash/${account}/transactions`, { method: "POST", body });
    transactionForm.reset();
    picker.value = account;
    await loadAccounts();
  } catch (error) {
    transactionError.textContent = error.message;
  }
});

picker.addEventListener("change", loadTransactions);
loadAccounts();
