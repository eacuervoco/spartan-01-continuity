"use strict";
const loading = document.querySelector("#account-loading");
const content = document.querySelector("#account-content");
const feedback = document.querySelector("#form-feedback");
async function initialize() {
  try {
    const {response, data} = await Continuity.api("/auth/me");
    if (response.status === 401) { window.location.replace("/login"); return; }
    if (!response.ok) throw new Error("context");
    document.querySelector("#account-name").textContent = data.nombre;
    document.querySelector("#account-email").textContent = data.email;
    document.querySelector("#account-message").textContent = data.destino === "PANEL" ?
      "Tu acceso empresarial está autorizado. El panel estará disponible en un próximo requisito funcional." :
      "Tu cuenta está activa. La incorporación empresarial estará disponible en un próximo requisito funcional.";
    loading.hidden = true; content.hidden = false;
  } catch (_) { loading.textContent = "No se pudo consultar tu acceso. Recarga la página."; }
}
document.querySelector("#logout").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const csrf = await Continuity.api("/auth/csrf");
    if (!csrf.response.ok) throw new Error("csrf");
    const result = await Continuity.api("/auth/logout", {method:"POST", headers:{"X-CSRF-Token":csrf.data.csrf_token}});
    if (!result.response.ok) throw new Error("logout");
    window.location.replace("/login");
  } catch (_) {
    Continuity.show(feedback, "No se pudo cerrar sesión. Inténtalo de nuevo.");
    button.disabled = false;
  }
});
initialize();
