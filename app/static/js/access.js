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
    document.querySelector("#account-message").textContent =
      "Tu cuenta está activa. En Mi empresa puedes registrar o consultar tu empresa.";
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

// RF02 comparte sesión, CSRF y mensajes de RF01; no solicita datos del propietario.
(() => {
  const open = document.querySelector("#show-company");
  const section = document.querySelector("#company-section");
  const form = document.querySelector("#company-form");
  const submit = document.querySelector("#submit-company");
  const loading = document.querySelector("#company-loading");
  const feedback = document.querySelector("#company-feedback");
  const details = document.querySelector("#company-details");
  const retry = document.querySelector("#company-retry");
  let busy = false;

  function report(message, isError = true) {
    Continuity.show(feedback, message, isError);
    feedback.focus();
  }

  function failed(response) {
    if (response.status === 401) {
      report("Tu sesión ha expirado. Inicia sesión nuevamente.");
      window.location.replace("/login");
      return;
    }
    report(response.status === 403 ? "No se pudo autorizar la operación. Vuelve a intentarlo." :
      response.status === 422 ? "Revisa los campos y sus longitudes antes de volver a enviar." :
      "No fue posible completar la operación. Inténtalo nuevamente.");
  }

  function display(data) {
    for (const [field, key] of [["name", "nombre"], ["city", "ciudad"], ["nit", "nit"], ["sector", "sector"]]) {
      document.querySelector(`#company-value-${field}`).textContent = data[key] || "No informado";
    }
    form.hidden = true;
    details.hidden = false;
  }

  async function consult() {
    form.hidden = true;
    details.hidden = true;
    retry.hidden = true;
    loading.hidden = false;
    try {
      const {response, data} = await Continuity.api("/auth/companies/me");
      if (response.status === 200) {
        display(data);
        document.querySelector("#company-details-title").focus();
      } else if (response.status === 404) {
        form.hidden = false;
        document.querySelector("#company-name").focus();
      } else {
        failed(response);
        retry.hidden = response.status === 401;
      }
    } catch (_) {
      report("Sin conexión con el servidor. Vuelve a consultar antes de registrar.");
      retry.hidden = false;
    } finally { loading.hidden = true; }
  }

  async function load() {
    if (busy) return;
    busy = true;
    open.disabled = true;
    feedback.hidden = true;
    section.hidden = false;
    open.setAttribute("aria-expanded", "true");
    try { await consult(); }
    finally { busy = false; open.disabled = false; }
  }
  open.addEventListener("click", load);
  retry.addEventListener("click", load);

  for (const input of form.querySelectorAll("input")) {
    input.addEventListener("input", () => input.setCustomValidity(""));
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    const payload = {};
    for (const input of form.querySelectorAll("input")) {
      const value = input.value.trim();
      input.setCustomValidity(input.required && !value ? "Completa este campo sin usar solo espacios." :
        value.length > input.maxLength ? `Usa como máximo ${input.maxLength} caracteres.` : "");
      payload[input.name] = value || null;
    }
    if (!form.reportValidity()) return;
    busy = true;
    submit.disabled = true;
    open.disabled = true;
    feedback.hidden = true;
    try {
      const csrf = await Continuity.api("/auth/csrf");
      if (!csrf.response.ok) { failed(csrf.response); return; }
      const {response, data} = await Continuity.api("/auth/companies", {
        method: "POST", headers: {"Content-Type": "application/json", "X-CSRF-Token": csrf.data.csrf_token},
        body: JSON.stringify(payload)
      });
      if (response.status === 201) {
        display(data);
        form.reset();
        report("Empresa registrada correctamente.", false);
      } else if (response.status === 409) {
        report("Ya tienes una empresa registrada. Consultando sus datos…", false);
        await consult();
        if (!details.hidden) Continuity.show(feedback, "Esta es tu empresa registrada.", false);
      } else { failed(response); }
    } catch (_) {
      // La respuesta puede haberse perdido después de guardar: consultar antes de reintentar.
      form.hidden = true;
      retry.hidden = false;
      report("No se pudo confirmar el registro. Consulta tu empresa antes de volver a intentarlo.");
    } finally {
      busy = false;
      submit.disabled = false;
      open.disabled = false;
    }
  });
})();
