fetch("/health")
  .then((res) => res.json())
  .then((data) => {
    document.getElementById("status").textContent = `${data.status} (v${data.version})`;
  })
  .catch(() => {
    document.getElementById("status").textContent = "unreachable";
  });
