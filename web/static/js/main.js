/* Botersson – Main JavaScript */

// ── Toast helper ──────────────────────────────────────────────────────────────
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const colorMap = {
    success: "bg-success text-white",
    warning: "bg-warning text-dark",
    danger:  "bg-danger text-white",
    info:    "bg-info text-dark",
  };
  const colorClass = colorMap[type] || colorMap.info;

  const toastEl = document.createElement("div");
  toastEl.id = `toast-${Date.now()}`;
  toastEl.className = `toast align-items-center ${colorClass} border-0`;
  toastEl.setAttribute("role", "alert");
  toastEl.setAttribute("aria-live", "assertive");

  const wrapper = document.createElement("div");
  wrapper.className = "d-flex";

  const body = document.createElement("div");
  body.className = "toast-body";
  body.textContent = String(message);

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "btn-close btn-close-white me-2 m-auto";
  closeBtn.setAttribute("data-bs-dismiss", "toast");

  wrapper.appendChild(body);
  wrapper.appendChild(closeBtn);
  toastEl.appendChild(wrapper);
  container.appendChild(toastEl);

  const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
  toast.show();
  toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}

// ── SocketIO connection status ─────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  if (typeof io === "undefined") return;

  const dot  = document.getElementById("status-dot");
  const text = document.getElementById("status-text");

  try {
    const socket = io({ transports: ["websocket", "polling"] });

    socket.on("connect", () => {
      if (dot)  { dot.classList.remove("text-danger"); dot.classList.add("text-success"); }
      if (text) text.textContent = "Connected";
    });

    socket.on("disconnect", () => {
      if (dot)  { dot.classList.remove("text-success"); dot.classList.add("text-danger"); }
      if (text) text.textContent = "Disconnected";
    });
  } catch (_) {
    // SocketIO not critical
  }
});

// ── Confirm before destructive actions ────────────────────────────────────────
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-confirm]");
  if (!btn) return;
  if (!confirm(btn.dataset.confirm)) {
    e.preventDefault();
    e.stopPropagation();
  }
});
