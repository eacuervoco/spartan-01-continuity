// Pruebas de lógica con DOM mínimo simulado. No validan renderizado ni accesibilidad real.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");

async function setup() {
  const nodes = new Map();
  let focused;
  const get = (selector) => {
    if (!nodes.has(selector)) nodes.set(selector, {
      hidden: true, disabled: false, textContent: "", value: "", handlers: {}, attrs: {},
      classList: {toggle() {}},
      addEventListener(type, fn) { this.handlers[type] = fn; },
      setAttribute(key, value) { this.attrs[key] = value; },
      setCustomValidity(value) { this.validationMessage = value; },
      focus() { focused = selector; }
    });
    return nodes.get(selector);
  };
  const fields = [["name", "nombre", 150, true], ["city", "ciudad", 100, true],
                  ["nit", "nit", 20, false], ["sector", "sector", 100, false]];
  const inputs = fields.map(([id, name, maxLength, required]) =>
    Object.assign(get(`#company-${id}`), {name, maxLength, required}));
  const form = get("#company-form");
  form.querySelectorAll = () => inputs;
  form.reportValidity = () => inputs.every(i => !i.validationMessage);
  form.reset = () => inputs.forEach(i => { i.value = ""; });
  get("#show-company").attrs["aria-expanded"] = "false";
  const calls = [];
  const replies = [];
  const redirects = [];
  const context = vm.createContext({
    document: {querySelector: get},
    window: {location: {replace: path => redirects.push(path)}},
    fetch: async (path, options) => {
      calls.push({path, options});
      if (path === "/auth/me") return response(200, {nombre: "Cliente", email: "a@example.test"});
      assert.ok(replies.length, `Respuesta no preparada para ${path}`);
      const reply = replies.shift();
      if (reply instanceof Error) throw reply;
      return await reply;
    }
  });
  vm.runInContext(fs.readFileSync("app/static/js/common.js", "utf8"), context);
  context.Continuity = context.window.Continuity;
  vm.runInContext(fs.readFileSync("app/static/js/access.js", "utf8"), context);
  await new Promise(resolve => setImmediate(resolve));
  return {get, calls, replies, redirects, inputs, focus: () => focused,
    open: () => get("#show-company").handlers.click(),
    submit: () => form.handlers.submit({preventDefault() {}})};
}
function response(status, data = {}) {
  return {status, ok: status >= 200 && status < 300, json: async () => data};
}
const company = {nombre: "<img src=x onerror=alert(1)>", ciudad: "Bogotá", nit: null, sector: "Tecnología"};
async function registration() {
  const app = await setup();
  app.replies.push(response(404));
  await app.open();
  app.get("#company-name").value = " Empresa ";
  app.get("#company-city").value = " Bogotá ";
  return app;
}

test("empresa oculta y sin consulta hasta seleccionarla; 200 muestra texto literal", async () => {
  const app = await setup();
  assert.equal(app.get("#company-section").hidden, true);
  assert.deepEqual(app.calls.map(c => c.path), ["/auth/me"]);
  app.replies.push(response(200, company));
  await app.open();
  assert.equal(app.get("#company-section").hidden, false);
  assert.equal(app.get("#show-company").attrs["aria-expanded"], "true");
  assert.equal(app.get("#company-details").hidden, false);
  assert.equal(app.get("#company-form").hidden, true);
  assert.equal(app.get("#company-value-name").textContent, company.nombre);
  assert.equal(app.get("#company-value-nit").textContent, "No informado");
});
test("404 abre formulario; 201 usa cookies, CSRF, normaliza y confirma", async () => {
  const app = await registration();
  assert.equal(app.get("#company-form").hidden, false);
  app.replies.push(response(200, {csrf_token: "token"}), response(201, company));
  await app.submit();
  const post = app.calls.at(-1);
  assert.equal(post.path, "/auth/companies");
  assert.equal(post.options.credentials, "same-origin");
  assert.equal(post.options.headers["X-CSRF-Token"], "token");
  assert.deepEqual(JSON.parse(post.options.body), {nombre: "Empresa", ciudad: "Bogotá", nit: null, sector: null});
  assert.equal(app.get("#company-details").hidden, false);
  assert.equal(app.get("#company-feedback").textContent, "Empresa registrada correctamente.");
  assert.equal(app.focus(), "#company-feedback");
});
test("espacios y longitud inválida impiden enviar y se pueden corregir", async () => {
  const app = await registration();
  for (const input of app.inputs) {
    const original = input.value;
    for (const value of ["a".repeat(input.maxLength + 1), ...(input.required ? ["   "] : [])]) {
      input.value = value;
      const count = app.calls.length;
      await app.submit();
      assert.equal(app.calls.length, count);
      assert.ok(input.validationMessage);
      input.value = original;
      input.handlers.input();
      assert.equal(input.validationMessage, "");
    }
  }
});
test("límites inclusivos y opcionales completos se envían", async () => {
  const app = await registration();
  for (const input of app.inputs) input.value = "á".repeat(input.maxLength);
  app.replies.push(response(200, {csrf_token: "token"}), response(201, company));
  await app.submit();
  const payload = JSON.parse(app.calls.at(-1).options.body);
  for (const input of app.inputs) assert.equal(payload[input.name].length, input.maxLength);
});
test("bloquea envíos simultáneos durante petición pendiente", async () => {
  const app = await registration();
  let resolve;
  app.replies.push(new Promise(done => { resolve = done; }), response(201, company));
  const pending = app.submit();
  assert.equal(app.get("#submit-company").disabled, true);
  const count = app.calls.length;
  await app.submit();
  assert.equal(app.calls.length, count);
  resolve(response(200, {csrf_token: "token"}));
  await pending;
  assert.equal(app.get("#submit-company").disabled, false);
});
test("409 consulta empresa existente", async () => {
  const app = await registration();
  app.replies.push(response(200, {csrf_token: "token"}), response(409), response(200, company));
  await app.submit();
  assert.equal(app.calls.at(-1).path, "/auth/companies/me");
  assert.equal(app.get("#company-details").hidden, false);
  assert.equal(app.get("#company-form").hidden, true);
});
for (const status of [401, 403, 422, 500]) {
  test(`POST ${status} muestra mensaje controlado`, async () => {
    const app = await registration();
    app.replies.push(response(200, {csrf_token: "token"}), response(status, {detail: "secreto-interno"}));
    await app.submit();
    assert.ok(app.get("#company-feedback").textContent);
    assert.equal(app.get("#company-feedback").textContent.includes("secreto-interno"), false);
    assert.equal(app.get("#submit-company").disabled, false);
    assert.deepEqual(app.redirects, status === 401 ? ["/login"] : []);
  });
}
for (const status of [401, 403, 422, 500]) {
  test(`GET ${status} nunca abre formulario`, async () => {
    const app = await setup();
    app.replies.push(response(status));
    await app.open();
    assert.equal(app.get("#company-form").hidden, true);
    assert.equal(app.get("#company-details").hidden, true);
    assert.deepEqual(app.redirects, status === 401 ? ["/login"] : []);
    assert.equal(app.get("#company-retry").hidden, status === 401);
  });
}
for (const status of [401, 403, 500]) {
  test(`CSRF ${status} impide POST`, async () => {
    const app = await registration();
    app.replies.push(response(status));
    await app.submit();
    assert.equal(app.calls.at(-1).path, "/auth/csrf");
    assert.equal(app.get("#company-feedback").hidden, false);
  });
}
test("error de red en consulta permite reintentar sin ofrecer registro", async () => {
  const app = await setup();
  app.replies.push(new Error("red"));
  await app.open();
  assert.equal(app.get("#company-form").hidden, true);
  assert.equal(app.get("#company-retry").hidden, false);
  app.replies.push(response(404));
  await app.get("#company-retry").handlers.click();
  assert.equal(app.get("#company-form").hidden, false);
});
test("respuesta POST perdida obliga a consultar y recupera empresa guardada", async () => {
  const app = await registration();
  app.replies.push(response(200, {csrf_token: "token"}), new Error("red"));
  await app.submit();
  assert.equal(app.get("#company-form").hidden, true);
  assert.equal(app.get("#company-retry").hidden, false);
  app.replies.push(response(200, company));
  await app.get("#company-retry").handlers.click();
  assert.equal(app.get("#company-details").hidden, false);
});
