// Powers the asset pages: a form that adds or edits records, and a table that lists them.
// crudPage({ url, columns, onLoad }) expects #record-form, #record-table and #error on the page.
function crudPage({ url, columns, onLoad }) {
  const form = document.getElementById("record-form");
  const table = document.getElementById("record-table");
  const errorBox = document.getElementById("error");
  const submit = form.querySelector("button[type=submit]");
  const addLabel = submit.textContent;
  let editing = null;

  function clearErrors() {
    errorBox.textContent = "";
    form.querySelectorAll(".field-error").forEach((node) => node.remove());
  }

  function showError(error) {
    errorBox.textContent = error.message;
    for (const issue of error.fields || []) {
      const input = form.elements[issue.loc[issue.loc.length - 1]];
      if (input) input.after(el("span", { className: "field-error", textContent: issue.msg }));
    }
  }

  function resetForm() {
    editing = null;
    form.reset();
    submit.textContent = addLabel;
  }

  function startEdit(record) {
    editing = record.id;
    for (const input of form.elements) {
      if (input.name && record[input.name] !== undefined) input.value = record[input.name];
    }
    submit.textContent = "Save changes";
    form.scrollIntoView({ behavior: "smooth" });
  }

  async function load() {
    const records = await api(url);
    const head = el("tr", {}, ...columns.map(([title]) => el("th", { textContent: title })));
    head.append(el("th", { textContent: "Actions" }));
    const rows = records.map((record) => {
      const row = el("tr", {}, ...columns.map(([title, format]) =>
        el("td", { textContent: format(record) ?? "" })));
      const edit = el("button", { textContent: "Edit", type: "button", className: "link" });
      const remove = el("button", { textContent: "Delete", type: "button", className: "link danger" });
      edit.addEventListener("click", () => startEdit(record));
      remove.addEventListener("click", async () => {
        if (!confirm("Delete this record?")) return;
        await api(`${url}/${record.id}`, { method: "DELETE" });
        await load();
      });
      row.append(el("td", {}, edit, " ", remove));
      return row;
    });
    table.replaceChildren(el("thead", {}, head), el("tbody", {}, ...rows));
    if (onLoad) onLoad(records);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors();
    const body = Object.fromEntries(new FormData(form));
    try {
      await api(editing ? `${url}/${editing}` : url, { method: editing ? "PUT" : "POST", body });
      resetForm();
      await load();
    } catch (error) {
      showError(error);
    }
  });

  load();
  return { load };
}
