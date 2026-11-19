const COLORS = { "Real Estate": "#1d5fbf", Gold: "#c98a00", Stocks: "#16794c", Cash: "#7a4fbf" };

function drawAllocation(classes) {
  const bar = document.getElementById("allocation-bar");
  bar.replaceChildren(...classes.filter((item) => Number(item.value) > 0).map((item) => {
    const segment = el("div", { title: `${item.name}: ${item.percent}%` });
    segment.style.width = `${item.percent}%`;
    segment.style.background = COLORS[item.name];
    return segment;
  }));
  document.getElementById("allocation-legend").replaceChildren(...classes.map((item) => {
    const swatch = el("span", { className: "swatch" });
    swatch.style.background = COLORS[item.name];
    return el("li", {}, swatch, `${item.name}: ${rupees(item.value)} (${item.percent}%)`);
  }));
}

function drawHistory(snapshots) {
  const box = document.getElementById("history");
  if (snapshots.length < 2) {
    box.replaceChildren(el("p", {
      className: "muted",
      textContent: "Come back tomorrow to see how your net worth changes over time.",
    }));
    return;
  }
  const values = snapshots.map((item) => Number(item.net_worth));
  const low = Math.min(...values);
  const range = Math.max(...values) - low || 1;
  const points = values.map((value, index) => {
    const x = (index / (values.length - 1)) * 100;
    const y = 95 - ((value - low) / range) * 90;
    return `${x},${y}`;
  });
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", "0 0 100 100");
  svg.setAttribute("preserveAspectRatio", "none");
  svg.setAttribute("class", "history");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Line chart of net worth over time");
  const line = document.createElementNS(svgNS, "polyline");
  line.setAttribute("points", points.join(" "));
  line.setAttribute("fill", "none");
  line.setAttribute("stroke", COLORS["Real Estate"]);
  line.setAttribute("stroke-width", "2");
  line.setAttribute("vector-effect", "non-scaling-stroke");
  svg.append(line);
  const first = snapshots[0];
  const last = snapshots[snapshots.length - 1];
  box.replaceChildren(svg, el("p", {
    className: "muted",
    textContent: `${first.date}: ${rupees(first.net_worth)} to ${last.date}: ${rupees(last.net_worth)}`,
  }));
}

async function downloadCsv() {
  const response = await fetch("/api/dashboard/export.csv", {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const link = el("a", { href: URL.createObjectURL(await response.blob()), download: "holdings.csv" });
  link.click();
  URL.revokeObjectURL(link.href);
}

async function loadDashboard() {
  const summary = await api("/api/dashboard");
  document.getElementById("net-worth").textContent = rupees(summary.net_worth);
  drawAllocation(summary.asset_classes);
  drawHistory(await api("/api/dashboard/history"));
}

document.getElementById("export").addEventListener("click", downloadCsv);
loadDashboard();
