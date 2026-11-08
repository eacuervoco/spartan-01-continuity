/* Interfaz estática de E, adaptada de las plantillas y scripts reales; sin API. */
"use strict";
(() => {
  let screen = "login";
  const get = id => document.getElementById(id);
  const field = (id, label, attrs = '') => `<div class="field"><label for="${id}">${label}</label><input id="${id}" ${attrs} autocomplete="off"></div>`;
  const password = register => `<div class="field"><label for="demo-password">${register ? "Contraseña ficticia (mínimo 12 caracteres)" : "Contraseña ficticia"}</label><div class="password-field"><input id="demo-password" type="password" required maxlength="1024" autocomplete="off"><button class="visibility-toggle" type="button" id="demo-visibility" aria-label="Mostrar contraseña" aria-pressed="false">Mostrar</button></div></div>`;
  const shell = "<p class=\"notice\" id=\"demo-note\">Simulación sin backend. Usa solo datos ficticios y correos @example.test, @example.com o @example.org; nunca credenciales reales. Contraseña de ejemplo: DemoContinuitY12! Datos en memoria hasta recargar. No reproduce seguridad de sesiones, CSRF ni persistencia PostgreSQL.</p><div class=\"prototype\"><div class=\"app-shell\">    <header class=\"site-header\">\n      <a class=\"brand\" href=\"#inicio\" aria-label=\"ContinuitY, página de acceso\">\n        <span class=\"brand-icon\" aria-hidden=\"true\">C<span class=\"brand-dot\"></span></span>\n        <span>Continuit<span class=\"brand-y\">Y</span></span>\n      </a>\n      <span class=\"brand-caption\">SPARTAN SYSTEMS LAB</span>\n    </header><div class=\"main-layout\"><section class=\"signin\" aria-labelledby=\"demo-title\"><div class=\"signin-inner\"><p class=\"eyebrow\"><span class=\"eyebrow-mark\" aria-hidden=\"true\"></span>TU ESPACIO DE EVOLUCIÓN DIGITAL</p><div id=\"demo-content\"></div><p id=\"demo-feedback\" class=\"form-feedback\" role=\"status\" aria-live=\"polite\" tabindex=\"-1\"></p><p class=\"trust-line\">◈ Datos ficticios · demostración en memoria</p></div></section>      <aside class=\"motivation\" aria-label=\"Qué puedes lograr con ContinuitY\">\n        <div class=\"motivation-content\">\n          <div class=\"tag\"><span class=\"tag-dot\" aria-hidden=\"true\"></span> CONVIERTE POTENCIAL EN VALOR</div>\n          <div class=\"graphic\" aria-hidden=\"true\">\n            <div class=\"graphic-halo halo-one\"></div><div class=\"graphic-halo halo-two\"></div>\n            <div class=\"graphic-card card-back\"><div class=\"bar long\"></div><div class=\"bar short\"></div><div class=\"bar medium\"></div></div>\n            <div class=\"graphic-card card-front\"><span class=\"graphic-symbol\">↗</span><div class=\"graphic-card-label\">OPORTUNIDADES</div><div class=\"graphic-card-number\">+ Potencial</div><div class=\"progress-track\"><span></span></div></div>\n            <div class=\"graphic-spark spark-one\">✦</div><div class=\"graphic-spark spark-two\">✦</div>\n          </div>\n          <h3>Lo que hoy tienes,<br>puede llevarte <em>más lejos.</em></h3>\n          <p>Diagnostica. Descubre. Evoluciona. Cada paso te acerca a una infraestructura más eficiente.</p>\n          <div class=\"motivation-steps\" aria-label=\"Etapas futuras de tu recorrido\">\n            <span class=\"step active\">01 <strong>Conecta</strong></span>\n            <span class=\"step\">02 <strong>Descubre</strong></span>\n            <span class=\"step\">03 <strong>Evoluciona</strong></span>\n          </div>\n        </div>\n      </aside></div>    <footer class=\"site-footer\"><span>© ContinuitY · Spartan Systems Lab</span><span>Diseñado para avanzar con propósito.</span></footer></div></div>";
  window.ContinuityPrototype = (demo, mode = screen, message = "", focus = false) => {
    // Toda entrada a una vista privada comprueba la sesión simulada.
    if (!demo.active && ["access", "company"].includes(mode)) mode = "login";
    if (demo.active && ["login", "register"].includes(mode)) mode = "access";
    screen = mode;
    get("prototype-host").innerHTML = shell;
    const content = get("demo-content");
    const render = (next, msg = "") => window.ContinuityPrototype(demo, next, msg, true);
    const feedback = (msg, success = false) => {
      const node = get("demo-feedback");
      node.textContent = msg;
      node.className = "form-feedback" + (success ? " is-success" : "");
      node.focus();
    };
    const submit = (id, action) => get(id).addEventListener("submit", event => {
      event.preventDefault();
      if (!event.currentTarget.reportValidity()) return;
      try { action(); } catch (error) { feedback(error.message); }
    });
    if (mode === "login" || mode === "register") {
      const register = mode === "register";
      content.innerHTML = `<h3 class="screen-title" id="demo-title" tabindex="-1">${register ? 'Comienza a <span class="highlight">evolucionar.</span>' : 'El potencial de tu<br><span class="highlight">infraestructura</span><br>comienza aquí.'}</h3><p class="intro">${register ? 'Crea tu cuenta personal para dar el primer paso hacia nuevas oportunidades.' : 'Ingresa a ContinuitY y sigue transformando tus recursos tecnológicos en oportunidades para tu negocio.'}</p><form id="demo-auth" class="login-form" aria-describedby="demo-note">${register ? field("demo-name", "Nombre completo ficticio", 'required maxlength="120"') : ""}${field("demo-email", "Correo electrónico ficticio", 'type="email" required maxlength="254" placeholder="consultor@example.test" inputmode="email"')}${password(register)}${register ? field("demo-confirm", "Confirmar contraseña ficticia", 'type="password" required maxlength="1024"') : ""}<button class="primary-button" type="submit">${register ? 'Crear cuenta' : 'Continuar'} <span aria-hidden="true">→</span></button></form><p class="signup-copy">${register ? '¿Ya tienes cuenta?' : '¿Aún no tienes cuenta?'} <button id="${register ? 'tab-login' : 'tab-register'}" type="button">${register ? 'Iniciar sesión' : 'Crear cuenta'}</button></p>`;
      get(register ? "tab-login" : "tab-register").onclick = () => render(register ? "login" : "register");
      get("demo-visibility").onclick = () => {
        const input = get("demo-password"), button = get("demo-visibility");
        const visible = input.type === "password";
        input.type = visible ? "text" : "password";
        button.textContent = visible ? "Ocultar" : "Mostrar";
        button.setAttribute("aria-label", visible ? "Ocultar contraseña" : "Mostrar contraseña");
        button.setAttribute("aria-pressed", String(visible));
      };
      submit("demo-auth", () => {
        if (register) {
          demo.register({name:get("demo-name").value, email:get("demo-email").value, password:get("demo-password").value, confirmation:get("demo-confirm").value});
          render("login", "Cuenta creada correctamente. Inicia sesión con tus datos ficticios.");
        } else {
          demo.login(get("demo-email").value, get("demo-password").value);
          render("access", "Inicio de sesión simulado correcto.");
        }
      });
    } else {
      content.innerHTML = `<h3 class="screen-title" id="demo-title" tabindex="-1">Tu próximo paso en <span class="highlight">ContinuitY.</span></h3><p class="intro">Consulta tu acceso y registra los datos de tu empresa.</p><section class="account-panel" aria-label="Mi acceso"><h3>Mi acceso</h3><p>Bienvenido, <strong id="demo-account-name"></strong>.</p><p id="demo-account-email"></p><p>Cuenta ACTIVA · Sesión VIGENTE (simulada)</p><button class="primary-button" id="demo-show-company" type="button">${mode === "company" ? 'Consultar empresa' : 'Mi empresa'}</button><button class="primary-button" id="demo-logout" type="button">Cerrar sesión</button></section><div id="demo-company-panel"></div>`;
      get("demo-account-name").textContent = demo.active.name;
      get("demo-account-email").textContent = demo.active.email;
      get("demo-show-company").onclick = () => render("company");
      get("demo-logout").onclick = () => { demo.logout(); render("login", "Sesión cerrada. Los datos ficticios se conservan hasta recargar esta pestaña."); };
      if (mode === "company") {
        const company = demo.company();
        get("demo-company-panel").innerHTML = `<section class="account-panel company-panel" aria-labelledby="demo-company-title"><h3 id="demo-company-title" tabindex="-1">Mi empresa</h3>${company ? '<h3>Empresa registrada</h3><p>Ficha de solo lectura. Una empresa por usuario.</p><dl class="company-details"><dt>Nombre / razón social</dt><dd id="company-value-name"></dd><dt>Ciudad / municipio</dt><dd id="company-value-city"></dd><dt>NIT</dt><dd id="company-value-nit"></dd><dt>Sector económico</dt><dd id="company-value-sector"></dd></dl>' : `<form id="demo-company" class="login-form" aria-describedby="company-note"><p id="company-note" class="form-note">Nombre y ciudad son obligatorios. Puedes registrar una sola empresa ficticia.</p>${field('company-name','Nombre de empresa / razón social (obligatorio)','required maxlength="150"')}${field('company-city','Ciudad / municipio (obligatorio)','required maxlength="100"')}${field('company-nit','NIT (opcional, ficticio)','maxlength="20"')}${field('company-sector','Sector económico (opcional)','maxlength="100"')}<button class="primary-button" type="submit">Registrar empresa</button></form>`}<button class="back-button" id="demo-back" type="button">Volver a Mi acceso</button></section>`;
        if (company) {
          for (const [id, key] of [["name","nombre"],["city","ciudad"],["nit","nit"],["sector","sector"]]) get("company-value-" + id).textContent = company[key] || "No informado";
        } else {
          submit("demo-company", () => {
            demo.registerCompany({nombre:get("company-name").value,ciudad:get("company-city").value,nit:get("company-nit").value,sector:get("company-sector").value});
            render("company", "Empresa registrada correctamente (simulación).");
          });
        }
        get("demo-back").onclick = () => render("access");
      }
    }
    if (message) feedback(message, true);
    else if (focus) get(mode === "company" ? "demo-company-title" : "demo-title").focus();
  };
})();
