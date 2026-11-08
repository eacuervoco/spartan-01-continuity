"use strict";
(() => {
  const {requirements, statuses, dimensions} = window.PortalData;
  const main = document.querySelector("main");
  const demo = new window.ContinuityDemo();
  let companyOpen = false;
  const key = "continuity-academic-rf01-rf02-v2";
  let storageAvailable = true;
  let evaluations = {};
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
  const get = id => document.getElementById(id);
  const badge = rf => `<span class="badge ${rf.implemented ? "" : "pending"}">${rf.implemented ? "Implementado en main · demo simulada" : "Propuesta conceptual pendiente de validación"}</span>`;
  const title = (label, heading, intro) => `<p class="eyebrow">${label}</p><h1>${heading}</h1><p class="intro">${intro}</p>`;
  const options = (values, selected) => values.map(s => `<option${s === selected ? " selected" : ""}>${esc(s)}</option>`).join("");
  const table = (headers, rows, caption) => `<div class="table-wrap"><table><caption>${caption}</caption><thead><tr>${headers.map(h => `<th scope="col">${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  const acceptance = rf => table(["ID", "Escenario", "Precondición", "Acción", "Resultado esperado", "Evidencia verificable", "Estado"], rf.criteria.map(c => [c.id, c.scenario, c.condition, c.action, c.expected, c.evidence.split("; ").map(ref => `<a href="evidence/sources.md#${rf.id.toLowerCase()}">${esc(ref)}</a>`).join("<br>"), c.status]), "Matriz técnica · HU-" + rf.id + "-01 → criterios → pruebas");
  const evidenceLink = '<a href="evidence/revision.md">Registro de revisión y pruebas</a>';
  function cleanEvaluation(value, rf) {
    if (!value || typeof value !== "object") return null;
    const state = s => statuses.includes(s) ? s : statuses[0];
    return {status: state(value.status), conclusion: typeof value.conclusion === "string" ? value.conclusion.slice(0,4000) : "Sin evaluar", observations: typeof value.observations === "string" ? value.observations.slice(0,4000) : "Sin evaluar", dimensions: dimensions.map((_,i) => state(value.dimensions?.[i])), criteria: Object.fromEntries(rf.criteria.map(c => [c.id, state(value.criteria?.[c.id])]))};
  }
  try {
    const stored = JSON.parse(localStorage.getItem(key) || "{}");
    for (const rf of requirements) { const value = cleanEvaluation(stored?.[rf.id], rf); if (value) evaluations[rf.id] = value; }
  } catch { storageAvailable = false; }
  function home() {
    main.innerHTML = `<section class="hero"><div><p class="eyebrow">ContinuitY V3.0 · Portal académico</p><h1>Conoce el presente.<br><span class="highlight">Diseña la evolución.</span></h1><p class="intro">El MVP de ContinuitY tiene previsto alcanzar el diagnóstico técnico de infraestructura tecnológica y la interacción con un modelo de inteligencia artificial, para identificar riesgos, activos subutilizados y oportunidades de optimización. RF01 y RF02 proporcionan la base de identidad y registro empresarial. El diagnóstico y la integración de IA pertenecen a incrementos posteriores y no se consideran implementados en esta entrega.</p><p class="notice">Demostración estática con datos ficticios. No utiliza API ni PostgreSQL. La evaluación docente empieza Sin evaluar.</p></div><aside class="journey"><p class="eyebrow">Tu espacio de evolución digital</p><h2>Lo que hoy tienes,<br>puede llevarte más lejos.</h2><p>Dos requisitos, seis apartados por ficha. Diseño y seguridad vinculados al software existente.</p><p><a class="button" href="#requisitos/RF01">RF01 · Identidad y sesiones →</a></p><p><a class="button" href="#requisitos/RF02">RF02 · Registro empresarial →</a></p></aside></section><p>${evidenceLink} · <a href="evidence/sources.md">Fuentes vigentes y precedencia documental</a></p>`;
  }
  function detail(rf) {
    main.innerHTML = title(`Ficha académica · ${rf.id}`, `${rf.id} · ${rf.name}`, rf.objective) + `<p>${badge(rf)}</p><div class="rf-detail">
      <section class="card"><h2>A. Requisito funcional</h2><dl>${[["ID",rf.id],["Nombre",rf.name],["Objetivo",rf.objective],["Actor",rf.actor],["Descripción",rf.description],["Precondiciones",rf.preconditions],["Entradas",rf.inputs],["Salidas",rf.outputs],["Postcondiciones",rf.postconditions]].map(([k,v])=>`<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl><h3 class="section">Reglas de negocio</h3><ul>${rf.rules.map(r=>`<li>${r}</li>`).join("")}</ul><a href="${rf.source}">Fuentes verificables</a></section>
      <section class="card"><h2>B. Historia de usuario</h2><p class="eyebrow">HU-${rf.id}-01</p><p>${rf.story}</p><p>La historia cubre los criterios ${rf.criteria[0].id} a ${rf.criteria.at(-1).id}; se sintetiza del comportamiento implementado.</p></section>
      <section><h2>C. Criterios de aceptación con matriz</h2>${acceptance(rf)}<p class="muted">Cumple se limita al alcance de las pruebas ejecutadas indicadas en el <a href="evidence/revision.md">registro de revisión</a>. No representa aceptación docente ni validación de PostgreSQL por la demo.</p></section>
      <section class="card"><h2>D. Ciclo de vida</h2><p>Levantamiento → Análisis → Diseño → Implementación → Pruebas → Evaluación.</p>${table(["Etapa","Artefacto real y alcance"],[
      ["Levantamiento",`<a href="evidence/sources.md#${rf.id.toLowerCase()}">${rf.id === "RF01" ? "README_RF01.md" : "CONTINUITY_RF02_REGISTRO_EMPRESA.md"}</a>; antecedentes, sin actas de entrevista acreditadas.`],
      ["Análisis",`app/core/${rf.id === "RF01" ? "registration.py, login.py, session_service.py" : "company_service.py, models.py"}; reglas resumidas en A.`],
      ["Diseño","Esquema SQL y repositorios descritos debajo; API y frontend existentes. No implica aprobación de diseño."],
      ["Implementación","Servicios, API, frontend y adaptadores presentes en main, 1f858c0; portal simulado por separado."],
      ["Pruebas",`${evidenceLink}; pruebas automatizadas y omisiones explícitas. PostgreSQL y revisión visual pendientes.`],
      ["Evaluación","Formulario F: Sin evaluar al iniciar; aceptación docente pendiente. Sin fechas ni cierres de sprint inferidos."]
      ],"Artefactos por etapa")}${design()}${rf.id === "RF01" ? security() : ""}</section>
      <section class="card"><h2>E. Prototipo interactivo</h2><div id="prototype-host"></div></section>
      <section class="card"><h2>F. Evaluación del prototipado</h2><p>Pruebas técnicas: consultar C y el registro de ejecución. Valoración académica: registrar dimensiones, criterios, observaciones y conclusión. La automatización no evalúa claridad ni usabilidad docente.</p><div id="evaluation-host"></div></section></div>`;
    prototype(); evaluation(rf.id);
  }
  function prototype(mode = "login", message = "") {
    get("prototype-host").innerHTML = `<h3>Tu próximo paso en ContinuitY.</h3>` + `<p class="notice">Demostración estática. Usa exclusivamente datos ficticios. Utiliza la clave pública de práctica DemoContinuitY12!; no introduzcas credenciales reales. Los datos permanecen solo en memoria hasta recargar. Esta simulación no ofrece autenticación segura ni reproduce cookies, CSRF, concurrencia o temporizadores reales.</p><div class="demo-layout section"><section class="card demo-panel"><div id="demo-content"></div><p id="demo-feedback" class="form-feedback" role="status" aria-live="polite" tabindex="-1">${esc(message)}</p></section><aside class="journey"><p class="eyebrow">Conecta · Asocia · Consulta</p><h3>Un recorrido sencillo,<br>con reglas visibles.</h3><ol><li>Crea una cuenta ficticia.</li><li>Inicia sesión con tu clave de práctica.</li><li>Registra TecniRed Sabana.</li><li>Cierra e inicia sesión para consultar de nuevo.</li></ol><p>Una empresa por usuario. Nombre y ciudad obligatorios; NIT y sector opcionales.</p><p>Los datos de demostración se pierden al recargar. Las evaluaciones docentes se guardan por separado en este navegador.</p><div class="actions"><a class="button" href="#requisitos/RF01">Ficha RF01</a><a class="button" href="#requisitos/RF02">Ficha RF02</a></div></aside></div>`;
    const field = (id,label,type="text",attrs="") => `<div class="field"><label for="${id}">${label}</label><input id="${id}" name="${id}" type="${type}" ${attrs}></div>`;
    const feedback = msg => { get("demo-feedback").textContent = msg; get("demo-feedback").focus(); };
    const submit = (id, action) => get(id).addEventListener("submit", event => { event.preventDefault(); if (!event.currentTarget.reportValidity()) return; try { action(); } catch(e) { feedback(e.message); } });
    const content = get("demo-content");
    if (!demo.active) {
      content.innerHTML = `<div class="demo-tabs" aria-label="Acceso simulado"><button id="tab-login" aria-pressed="${mode !== "register"}">Iniciar sesión</button><button id="tab-register" aria-pressed="${mode === "register"}">Crear cuenta</button></div><h3>${mode === "register" ? 'Comienza a <span class="highlight">evolucionar.</span>' : 'Bienvenido de <span class="highlight">nuevo.</span>'}</h3><form id="demo-auth">${mode === "register" ? field("demo-name","Nombre completo","text",'required maxlength="120" value="Consultor de práctica"') : ""}${field("demo-email","Correo ficticio (@example.test)","email",'required maxlength="254" value="consultor@example.test" autocomplete="off"')}${field("demo-password","Contraseña (mínimo 12 caracteres) · ficticia","password",'required maxlength="1024" autocomplete="off" readonly value="DemoContinuitY12!"')}${mode === "register" ? field("demo-confirm","Confirmar contraseña · ficticia","password",'required maxlength="1024" autocomplete="off" readonly value="DemoContinuitY12!"') : ""}<button id="demo-invalid" type="button">Probar clave inválida / restaurar</button>${mode === "register" ? '<button id="demo-mismatch" type="button">Probar confirmación distinta / restaurar</button>' : ""}<button class="primary" type="submit">${mode === "register" ? "Crear cuenta" : "Continuar"} →</button></form><p class="muted section">Sesión: ${demo.sessionState()}. Cuenta consultada: <span id="account-state">${demo.accountState("consultor@example.test")}</span>.</p>`;
      get("demo-invalid").onclick = () => { get("demo-password").value = get("demo-password").value === "corta" ? "DemoContinuitY12!" : "corta"; };
      if (mode === "register") get("demo-mismatch").onclick = () => { get("demo-confirm").value = get("demo-confirm").value === "distinta" ? "DemoContinuitY12!" : "distinta"; };
      get("tab-login").onclick = () => prototype("login"); get("tab-register").onclick = () => prototype("register");
      get("demo-email").addEventListener("input", e => { get("account-state").textContent = demo.accountState(e.target.value); });
      submit("demo-auth", () => {
        if (mode === "register") { demo.register({name:get("demo-name").value,email:get("demo-email").value,password:get("demo-password").value,confirmation:get("demo-confirm").value}); prototype("login","Cuenta creada correctamente. Inicia sesión con el correo y la clave de práctica que elegiste."); }
        else { demo.login(get("demo-email").value,get("demo-password").value); prototype("login","Inicio de sesión simulado correcto."); }
      });
    } else {
      const company = demo.company();
      content.innerHTML = `<h3>Mi acceso</h3><p>Bienvenido, <strong>${esc(demo.active.name)}</strong>.</p><p>${esc(demo.active.email)}</p><p><span class="badge">Cuenta ACTIVA · Sesión VIGENTE</span></p><div class="actions"><button id="demo-logout">Cerrar sesión</button><button id="demo-expire">Simular expiración</button><button id="demo-session">Consultar sesión</button></div><button id="demo-show-company" aria-expanded="${companyOpen}" aria-controls="demo-company-panel">Mi empresa</button><div id="demo-company-panel" ${companyOpen ? "" : "hidden"}><h3>Mi empresa</h3>${company ? `<dl>${[["Nombre",company.nombre],["Ciudad",company.ciudad],["NIT",company.nit || "No informado"],["Sector",company.sector || "No informado"]].map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join("")}</dl><p class="muted section">Asociada a ${esc(demo.active.email)}. Vista de solo lectura.</p><button id="demo-duplicate">Comprobar prevención de duplicidad</button>` : `<form id="demo-company"><p class="muted">Una empresa por usuario. Los datos precargados son ficticios.</p>${field("company-name","Nombre de empresa / razón social (obligatorio)","text",'required maxlength="150" value="TecniRed Sabana"')}${field("company-city","Ciudad / municipio (obligatorio)","text",'required maxlength="100" value="Bogotá"')}${field("company-nit","NIT (opcional, ficticio)","text",'maxlength="20"')}${field("company-sector","Sector económico (opcional)","text",'maxlength="100" value="Servicios tecnológicos"')}<button class="primary" type="submit">Registrar empresa</button></form>`}</div>`;
      get("demo-show-company").onclick = () => { companyOpen = !companyOpen; get("demo-company-panel").hidden = !companyOpen; get("demo-show-company").setAttribute("aria-expanded",String(companyOpen)); };
      get("demo-session").onclick = () => feedback(`Consulta simulada: ${demo.sessionState()} · ${demo.active.email}.`);
      get("demo-logout").onclick = () => { demo.logout(); companyOpen = false; prototype("login","Sesión cerrada. Estado: EXPIRADA. Los datos ficticios permanecen hasta recargar esta pestaña."); };
      get("demo-expire").onclick = () => { demo.logout(); companyOpen = false; prototype("login","Expiración simulada: sesión EXPIRADA. Inicia sesión de nuevo."); };
      if (company) get("demo-duplicate").onclick = () => { try { demo.registerCompany(company); } catch(e) { feedback(e.message); } };
      else submit("demo-company", () => { demo.registerCompany({nombre:get("company-name").value,ciudad:get("company-city").value,nit:get("company-nit").value,sector:get("company-sector").value}); prototype("login","Empresa registrada correctamente (simulación)."); });
    }
  }
  function design() {
    return `<h3 class="section">Diseño de persistencia · RF01 y RF02</h3><p>Esquema definido en <code>database/001_schema.sql</code>, <code>003_sesiones_revocacion.sql</code> y <code>004_empresas.sql</code>, con adaptadores reales. No acredita el estado de una instancia PostgreSQL desplegada.</p><img class="diagram" src="assets/data-model.svg" alt="Usuarios se relaciona con cero o una credencial, cero o muchas sesiones y cero o una empresa. Cada registro dependiente pertenece a un usuario."><p><a href="assets/data-model.mmd">Diagrama fuente Mermaid</a> · <a href="evidence/sources.md#diseno">Fuentes y restricciones</a></p>
      ${table(["Tabla / RF", "Columnas esenciales", "Claves y restricciones"], [
        ["usuarios · RF01", "id UUID; nombre VARCHAR(120); email_normalizado TEXT; creado_en TIMESTAMPTZ; estado TEXT; rol TEXT", "PK id; correo UNIQUE, minúsculas y sin espacios exteriores; nombre no vacío; estado ACTIVA; rol CLIENTE"],
        ["credenciales · RF01", "usuario_id UUID; password_hash TEXT (solo nombre de columna; sin valores)", "PK/FK usuario_id → usuarios.id; ON DELETE CASCADE; valor requerido y no vacío"],
        ["sesiones · RF01", "token_digest CHAR(64); usuario_id UUID; creado_en, expira_en, ultima_actividad_en y revocada_en TIMESTAMPTZ", "PK token_digest; FK usuario_id → usuarios.id CASCADE; digest hexadecimal; fechas coherentes; revocada_en nullable; índice por usuario"],
        ["empresas · RF02", "id UUID; usuario_id UUID; nombre VARCHAR(150); ciudad VARCHAR(100); nit VARCHAR(20) nullable; sector VARCHAR(100) nullable; creado_en TIMESTAMPTZ", "PK id; FK usuario_id → usuarios.id RESTRICT; usuario_id UNIQUE; nombre y ciudad no vacíos; NIT sin unicidad"]
      ], "Esquema implementado en scripts SQL (sin registros ni datos sensibles)")}
      <p class="section">Todos los campos son NOT NULL excepto los indicados como opcionales. La relación usuarios–credenciales es 1 a 0..1 a nivel SQL; el servicio crea ambas filas transaccionalmente. Usuarios–empresas es 1 a 0..1 y usuarios–sesiones es 1 a 0..N.</p><p>Persistencia transaccional: crear_cuenta inserta usuario y credencial en una transacción Psycopg; confirma ambas o revierte ante error. Empresas y sesiones usan una conexión y transacción por operación. UNIQUE(usuario_id) protege la empresa ante colisiones; revocada_en impide reactivar sesiones mediante UPSERT. La verificación completa en PostgreSQL queda pendiente. El backend usa memoria por defecto; PostgreSQL se selecciona explícitamente.</p>`;
  }
  function security() {
    return `<h3 class="section">Seguridad implementada de RF01</h3>${table(["Control","Riesgo mitigado","Implementación real","Evidencia"], window.PortalData.controls.map(row => [...row.slice(0,3), `<a href="evidence/sources.md#seguridad">${row[3]}</a>`]),"Controles encontrados en el repositorio")}<p>Alcance restrictivo: las rutas privadas exigen sesión; registro, login y páginas de entrada son públicos. No existe una política global que proteja automáticamente rutas futuras. Origen ausente no se rechaza por sí solo. Pendiente: limitador compartido entre procesos, revisión de permisos SQL existentes y comprobación HTTPS, navegador y PostgreSQL en despliegue. No se acredita inmunidad ante ataques ni certificación de seguridad.</p>`;
  }
  function evaluation(id = "RF01") {
    const rf = requirements.find(r=>r.id === id) || requirements[0];
    const value = evaluations[rf.id] || cleanEvaluation({},rf);
    get("evaluation-host").innerHTML = `<p>Todos los campos docentes inician Sin evaluar.</p>` + `<p class="notice">Las evaluaciones se guardan en este navegador y no se sincronizan entre dispositivos. Descarga una copia para conservarla. No incluyas datos personales ni información sensible.</p><form id="evaluation-form" class="card section"><h3>Evaluación de ${rf.id}</h3><p>Evaluación docente global y observaciones; no reemplazan la ejecución de pruebas técnicas.</p><div class="field"><label for="eval-status">Estado de evaluación</label><select id="eval-status">${options(statuses,value.status)}</select></div><fieldset><legend>Dimensiones del prototipo</legend>${dimensions.map((d,i)=>`<div class="assessment-row"><label for="dimension-${i}">${d}</label><select id="dimension-${i}">${options(statuses,value.dimensions[i])}</select></div>`).join("")}</fieldset><fieldset><legend>Criterios de aceptación</legend>${rf.criteria.map(c=>`<div class="assessment-row"><label for="${c.id}">${c.id} · ${c.scenario}</label><select id="${c.id}">${options(statuses,value.criteria[c.id])}</select></div>`).join("")}</fieldset><div class="field"><label for="eval-observations">Observaciones (máximo 4000 caracteres)</label><textarea id="eval-observations" maxlength="4000">${esc(value.observations)}</textarea></div><div class="field"><label for="eval-conclusion">Conclusión docente</label><textarea id="eval-conclusion" maxlength="4000">${esc(value.conclusion)}</textarea></div><button class="primary" type="submit">Guardar evaluación local</button><p id="eval-feedback" class="form-feedback" role="status" aria-live="polite">${storageAvailable ? "" : "Almacenamiento local no disponible o datos inválidos. Puedes trabajar en memoria y descargar resultados."}</p></form><section class="section"><h3>Matriz resumen de evaluación</h3><div id="eval-summary"></div><div class="actions no-print"><button id="download">Descargar resultados JSON</button><button id="print">Imprimir resultados</button></div><p class="muted">Guarda el formulario antes de descargar o imprimir. La descarga incluye dimensiones, criterios y observaciones. La impresión incluye el resumen completo.</p></section>`;
    const summary = () => {
      get("eval-summary").innerHTML = table(["RF", "Estado", "Dimensiones", "Criterios", "Observaciones", "Conclusión"], requirements.map(r => {
        const v = evaluations[r.id] || cleanEvaluation({},r);
        return [r.id, esc(v.status), dimensions.map((d,i)=>`${d}: ${esc(v.dimensions[i])}`).join("<br>"), r.criteria.map(c=>`${c.id}: ${esc(v.criteria[c.id])}`).join("<br>"), esc(v.observations || "Sin evaluar"), esc(v.conclusion)];
      }), "Resumen local · sin calificaciones automáticas");
    };
    summary();
    get("evaluation-form").onsubmit = e => {
      e.preventDefault();
      evaluations[rf.id] = {status:get("eval-status").value, conclusion:get("eval-conclusion").value, observations:get("eval-observations").value, dimensions:dimensions.map((_,i)=>get(`dimension-${i}`).value),criteria:Object.fromEntries(rf.criteria.map(c=>[c.id,get(c.id).value]))};
      try { localStorage.setItem(key,JSON.stringify(evaluations)); storageAvailable = true; get("eval-feedback").textContent = "Evaluación guardada en este navegador."; }
      catch { storageAvailable = false; get("eval-feedback").textContent = "No se pudo guardar en el navegador. Los resultados siguen en memoria; descárgalos antes de salir."; }
      summary();
    };
    get("print").onclick = () => window.print();
    get("download").onclick = () => {
      const output = {project:"ContinuitY",type:"Evaluación docente local; no certifica pruebas backend",exportedAt:new Date().toISOString(),evaluations:Object.fromEntries(requirements.map(r=>[r.id,evaluations[r.id] || cleanEvaluation({},r)]))};
      const url = URL.createObjectURL(new Blob([JSON.stringify(output,null,2)],{type:"application/json;charset=utf-8"}));
      const a = document.createElement("a"); a.href=url; a.download="continuity-evaluacion.json"; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
    };
  }
  function route() {
    const [page,id] = location.hash.slice(1).split("/");
    const current = page || "inicio";
    if (current === "inicio") home();
    else if (current === "requisitos" && requirements.some(r=>r.id===id)) detail(requirements.find(r=>r.id===id));
    else { main.innerHTML = title("Navegación", "Vista no encontrada", 'Vuelve a <a href="#inicio">Inicio</a> para continuar.'); }
    document.querySelectorAll("nav a").forEach(a => { if(a.hash === `#${current}${id ? "/"+id : ""}`) a.setAttribute("aria-current","page"); else a.removeAttribute("aria-current"); });
    document.title = `${main.querySelector("h1").textContent} | ContinuitY`;
    main.focus({preventScroll:true}); window.scrollTo(0,0);
  }
  window.addEventListener("hashchange",route);
  route();
})();
