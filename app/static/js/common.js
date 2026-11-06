"use strict";
// Respuestas controladas sin filtrar detalles del servidor ni datos sensibles.
window.Continuity = Object.freeze({
  async api(path, options = {}) {
    const response = await fetch(path, {credentials: "same-origin", cache: "no-store", ...options});
    let data = {};
    try { data = await response.json(); } catch (_) { /* Error no JSON. */ }
    return {response, data};
  },
  show(feedback, message, isError = true) {
    feedback.textContent = message;
    feedback.hidden = false;
    feedback.classList.toggle("is-success", !isError);
    if (isError) feedback.setAttribute("role", "alert");
    else feedback.setAttribute("role", "status");
  },
  togglePassword(toggle, password) {
    if (!toggle || !password) return;
    toggle.addEventListener("click", () => {
      const showing = password.type === "password";
      password.type = showing ? "text" : "password";
      toggle.textContent = showing ? "Ocultar" : "Mostrar";
      toggle.setAttribute("aria-label", showing ? "Ocultar contraseña" : "Mostrar contraseña");
      toggle.setAttribute("aria-pressed", String(showing));
    });
  }
});
