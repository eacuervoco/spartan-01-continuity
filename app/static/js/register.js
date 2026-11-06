"use strict";
const form = document.querySelector("#register-form");
const feedback = document.querySelector("#form-feedback");
const submit = document.querySelector("#submit-register");
Continuity.togglePassword(document.querySelector("#show-password"), document.querySelector("#password"));
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const password = document.querySelector("#password").value;
  const confirmacion_password = document.querySelector("#confirmacion_password").value;
  if (password !== confirmacion_password) {
    Continuity.show(feedback, "Las contraseñas no coinciden.");
    document.querySelector("#confirmacion_password").focus();
    return;
  }
  submit.disabled = true;
  feedback.textContent = "";
  try {
    const {response} = await Continuity.api("/auth/register", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({nombre: document.querySelector("#nombre").value.trim(),
        email: document.querySelector("#email").value.trim(), password, confirmacion_password})
    });
    if (response.status === 201) {
      form.reset();
      Continuity.show(feedback, "Cuenta creada correctamente. Ahora puedes iniciar sesión.", false);
      const link = document.createElement("a"); link.href = "/login";
      link.textContent = " Ir al inicio de sesión";
      feedback.append(link); feedback.focus();
    } else {
      Continuity.show(feedback, response.status === 409 ? "Este correo ya está registrado. Inicia sesión." :
        response.status === 422 ? "Revisa los datos y los requisitos de la contraseña." :
        "No fue posible crear la cuenta. Inténtalo nuevamente.");
    }
  } catch (_) { Continuity.show(feedback, "Sin conexión con el servidor. Inténtalo nuevamente."); }
  finally { submit.disabled = false; }
});
