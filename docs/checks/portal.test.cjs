/* Node built-ins only. DOM double: verifies routing and handlers, not browser rendering. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');

function load(stored = null, failStorage = false) {
  const elements = new Map();
  const routes = {};
  const storage = new Map(stored ? [['continuity-academic-evaluations-v1', stored]] : []);
  const snapshots = [];
  let html = '';
  function element(id) {
    if (elements.has(id)) return elements.get(id);
    const node = {value:'',textContent:'',listeners:{},focus(){},setAttribute(){},removeAttribute(){},reportValidity(){return true;},click(){this.onclick?.();},addEventListener(event,fn){this.listeners[event]=fn;}};
    Object.defineProperty(node,'innerHTML',{get(){return node.markup || '';},set(value){
      node.markup = value;
      if (id === 'main') { elements.clear(); elements.set('main',node); html = value; snapshots.push(value); }
      // Minimal parsing for control initial values. Real semantics checked independently in Python.
      for (const match of value.matchAll(/<(input|textarea|select|button|form|div|p|span)\b([^>]*\bid="([^"]+)"[^>]*)>/g)) {
        const child = element(match[3]);
        child.value = /\bvalue="([^"]*)"/.exec(match[2])?.[1] || '';
        if(match[1] === 'select') {
          const tail=value.slice(match.index+match[0].length).split('</select>')[0];
          child.value= /<option[^>]* selected[^>]*>([^<]*)/.exec(tail)?.[1] || /<option[^>]*>([^<]*)/.exec(tail)?.[1] || '';
        }
      }
    }});
    elements.set(id,node);return node;
  }
  const main=element('main');
  main.querySelector=()=>({textContent: /<h1>([\s\S]*?)<\/h1>/.exec(html)?.[1].replace(/<[^>]*>/g,'') || ''});
  const nav = ['inicio','prototipo','requisitos','diseno','evidencias','evaluacion'].map(p=>({hash:'#'+p,setAttribute(){},removeAttribute(){}}));
  const window={addEventListener(event,fn){routes[event]=fn;},scrollTo(){},print(){window.printed=true;}};
  const location={hash:''};
  const context=vm.createContext({window,location,document:{querySelector:()=>main,querySelectorAll:()=>nav,getElementById:id=>elements.get(id),createElement:()=>({click(){}})},localStorage:{getItem:k=>storage.get(k)||null,setItem(k,v){if(failStorage)throw Error('denied');storage.set(k,v);}},URL:{createObjectURL:()=> 'blob:demo',revokeObjectURL(){}},Blob,setTimeout(){}});
  for(const file of ['data.js','demo.js','app.js']) vm.runInContext(fs.readFileSync(path.join(root,'js',file),'utf8'),context,{filename:file});
  return {window,storage,elements,snapshots,html:()=>html,go(hash){location.hash='#'+hash;routes.hashchange();},submit(id){const form=elements.get(id);const event={preventDefault(){},currentTarget:form};(form.onsubmit || form.listeners.submit)(event);}};
}

test('RF01/RF02: validation, normalized duplicates, expiry, ownership and read-after-login',()=>{
  const {window}=load();const demo=new window.ContinuityDemo();
  const account={name:' Práctica ',email:' USER@EXAMPLE.TEST ',password:'ClaveFicticia12!',confirmation:'ClaveFicticia12!'};
  assert.equal(demo.accountState('user@example.test'),'NO EXISTE');
  assert.throws(()=>demo.company(),/EXPIRADA/);
  assert.throws(()=>demo.register({...account,name:'   '}),/ficticio/);
  assert.throws(()=>demo.register({...account,email:'persona@dominio.local'}),/ficticio/);
  assert.throws(()=>demo.register({...account,confirmation:'distinta'}),/coincidir/);
  demo.register(account);assert.equal(demo.accountState('user@example.test'),'ACTIVA');
  assert.throws(()=>demo.register(account),/registrado/);
  assert.throws(()=>demo.login(account.email,'incorrecta'),/incorrectos/);
  demo.login(account.email,account.password);assert.equal(demo.sessionState(),'VIGENTE');
  assert.throws(()=>demo.registerCompany({nombre:' ',ciudad:'Bogotá'}),/nombre/);
  assert.throws(()=>demo.registerCompany({nombre:'TecniRed',ciudad:'X'.repeat(101)}),/ciudad/);
  assert.throws(()=>demo.registerCompany({nombre:'TecniRed',ciudad:'Bogotá',nit:'X'.repeat(21)}),/nit/);
  demo.registerCompany({nombre:' TecniRed Sabana ',ciudad:' Bogotá '});
  assert.equal(demo.company().nit,'');assert.equal(demo.company().nombre,'TecniRed Sabana');
  assert.throws(()=>demo.registerCompany({}),/Ya tienes/);
  demo.logout();assert.equal(demo.sessionState(),'EXPIRADA');assert.throws(()=>demo.registerCompany({}),/EXPIRADA/);
  demo.register({...account,email:'otro@example.test'});demo.login('otro@example.test',account.password);assert.equal(demo.company(),null);
  demo.logout();demo.login(account.email,account.password);assert.equal(demo.company().ciudad,'Bogotá');
});

test('all six areas and twelve academic sheets render with one H1',()=>{
  const app=load();
  for(const route of ['inicio','prototipo','requisitos','diseno','evidencias','evaluacion',...Array.from({length:12},(_,i)=>`requisitos/RF${String(i+1).padStart(2,'0')}`)]) {
    app.go(route);assert.equal((app.html().match(/<h1>/g)||[]).length,1,route);
    if(route.startsWith('requisitos/'))for(const part of ['A. Requisito','B. Historia','C. Matriz','D. Ciclo','E. Prototipo','F. Evaluación','G. Trazabilidad'])assert.ok(app.html().includes(part),part);
  }
  assert.equal(app.window.PortalData.requirements.filter(r=>r.implemented).length,2);
  app.go('desconocida');assert.match(app.html(),/Vista no encontrada/);
});

test('form handlers complete registration, login, company and logout',()=>{
  const app=load();app.go('prototipo');app.elements.get('tab-register').click();
  app.elements.get('demo-password').value='ClaveFicticia12!';app.elements.get('demo-confirm').value='ClaveFicticia12!';app.submit('demo-auth');
  assert.match(app.html(),/Cuenta creada correctamente/);
  app.elements.get('demo-password').value='ClaveFicticia12!';app.submit('demo-auth');
  assert.match(app.elements.get('demo-content').innerHTML,/VIGENTE/);app.submit('demo-company');
  assert.match(app.elements.get('demo-content').innerHTML,/TecniRed Sabana/);
  app.elements.get('demo-duplicate').click();assert.match(app.elements.get('demo-feedback').textContent,/Ya tienes/);
  app.elements.get('demo-logout').click();assert.match(app.html(),/Sesión cerrada/);
  assert.equal(app.storage.size,0,'demo must never persist keys or credentials');
});

test('evaluation starts empty, persists, reloads, escapes stored input and exports/prints',()=>{
  const app=load();app.go('evaluacion/RF02');assert.equal(app.elements.get('eval-status').value,'Sin evaluar');
  app.elements.get('eval-status').value='Requiere ajustes';app.elements.get('eval-observations').value='<img src=x onerror=alert(1)>';
  app.submit('evaluation-form');
  const saved=app.storage.get('continuity-academic-evaluations-v1');assert.equal(JSON.parse(saved).RF02.status,'Requiere ajustes');
  const restored=load(saved);restored.go('evaluacion/RF02');assert.match(restored.html(),/&lt;img/);assert.ok(!restored.html().includes('<img src=x'));
  restored.elements.get('download').click();restored.elements.get('print').click();assert.equal(restored.window.printed,true);
  const blocked=load(null,true);blocked.go('evaluacion');blocked.submit('evaluation-form');assert.match(blocked.elements.get('eval-feedback').textContent,/No se pudo guardar/);
  const corrupt=load('{broken');corrupt.go('evaluacion');assert.match(corrupt.html(),/Almacenamiento local no disponible/);
});

// Python static checker consumes all rendered views, including both auth states.
if(process.argv.includes('--snapshots')){
  const app=load();
  for(const page of ['inicio','prototipo','requisitos','diseno','evidencias',...Array.from({length:12},(_,i)=>`requisitos/RF${String(i+1).padStart(2,'0')}`),...Array.from({length:12},(_,i)=>`evaluacion/RF${String(i+1).padStart(2,'0')}`)])app.go(page);
  // Include dynamic form markup as well as the outer page for semantic/link checks.
  app.go('prototipo');
  function captureDemo(){app.snapshots.push(app.html().replace('<div id="demo-content"></div>',`<div id="demo-content">${app.elements.get('demo-content').innerHTML}</div>`));}
  captureDemo();app.elements.get('tab-register').click();captureDemo();
  app.elements.get('demo-password').value='ClaveFicticia12!';app.elements.get('demo-confirm').value='ClaveFicticia12!';app.submit('demo-auth');
  app.elements.get('demo-password').value='ClaveFicticia12!';app.submit('demo-auth');captureDemo();app.submit('demo-company');captureDemo();
  // Emit a separate JSON file via caller-supplied /tmp path, never test data into portal output.
  fs.writeFileSync(process.argv[process.argv.indexOf('--snapshots')+1],JSON.stringify(app.snapshots));
}
