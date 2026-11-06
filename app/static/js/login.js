"use strict";
const form = document.querySelector("#login-form");
const feedback = document.querySelector("#form-feedback");
const submit = document.querySelector("#submit-login");
Continuity.togglePassword(document.querySelector("#show-password"), document.querySelector("#password"));
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  submit.disabled = true;
  feedback.textContent = "";
  try {
    const {response} = await Continuity.api("/auth/login", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({email: document.querySelector("#email").value.trim(), password: document.querySelector("#password").value})
    });
    if (response.ok) { window.location.assign("/access"); return; }
    const message = response.status === 429 ? "Demasiados intentos. Inténtalo en 15 minutos." :
      response.status === 401 ? "Correo o contraseña incorrectos." : "No fue posible iniciar sesión. Inténtalo nuevamente.";
    Continuity.show(feedback, message);
  } catch (_) { Continuity.show(feedback, "Sin conexión con el servidor. Inténtalo nuevamente."); }
  finally { submit.disabled = false; }
});
