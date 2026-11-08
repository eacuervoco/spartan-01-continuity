/* Modelo independiente de la interfaz: solo datos ficticios, sin red ni contraseñas persistidas. */
"use strict";
(() => {
  class Demo {
    constructor() { this.users = []; this.active = null; }
    register({name, email, password, confirmation}) {
      name = name.trim(); email = email.trim().toLowerCase();
      if (!name || name.length > 120 || !/^[^\s@]+@example\.(test|com|org)$/.test(email) || email.length > 254)
        throw Error("Usa un nombre ficticio y un correo @example.test, @example.com o @example.org.");
      if (password.length < 12 || password.length > 1024 || password !== confirmation)
        throw Error("La clave de práctica debe tener entre 12 y 1024 caracteres y coincidir con su confirmación.");
      if (this.users.some(u => u.email === email)) throw Error("Este correo ya está registrado.");
      // Permanece solo en memoria durante esta pestaña; nunca se escribe a almacenamiento local.
      this.users.push({name, email, practiceKey: password, company: null});
    }
    login(email, password) {
      const user = this.users.find(u => u.email === email.trim().toLowerCase() && u.practiceKey === password);
      if (!user) throw Error("Correo o clave de práctica incorrectos.");
      this.active = user;
    }
    logout() { this.active = null; }
    accountState(email) { return this.users.some(u => u.email === email.trim().toLowerCase()) ? "ACTIVA" : "NO EXISTE"; }
    sessionState() { return this.active ? "VIGENTE" : "EXPIRADA"; }
    company() {
      if (!this.active) throw Error("Sesión EXPIRADA: inicia sesión para consultar tu empresa.");
      return this.active.company;
    }
    registerCompany(values) {
      if (!this.active) throw Error("Sesión EXPIRADA: inicia sesión para registrar tu empresa.");
      if (this.active.company) throw Error("Ya tienes una empresa registrada. No puedes crear otra en el MVP.");
      const company = {};
      for (const [key, max, required] of [["nombre",150,true],["ciudad",100,true],["nit",20,false],["sector",100,false]]) {
        const value = (values[key] || "").trim();
        if ((required && !value) || value.length > max) throw Error(`Revisa ${key}: ${required ? "obligatorio, " : "opcional, "}máximo ${max} caracteres.`);
        company[key] = value;
      }
      this.active.company = company;
      return company;
    }
  }
  window.ContinuityDemo = Demo;
})();
