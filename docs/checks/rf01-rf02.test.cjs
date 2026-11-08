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
  const storage = new Map(stored ? [['continuity-academic-rf01-rf02-v2', stored]] : []);
  const snapshots = [];
  let html = '';
  function element(id) {
    if (elements.has(id)) return elements.get(id);
    const node = {value:'',textContent:'',listeners:{},focus(){},before(){},setAttribute(){},removeAttribute(){},reportValidity(){return true;},click(){this.onclick?.();},addEventListener(event,fn){this.listeners[event]=fn;}};
    Object.defineProperty(node,'innerHTML',{get(){return node.markup || '';},set(value){
      node.markup = value;
      if (id === 'main') { elements.clear(); elements.set('main',node); html = value; snapshots.push(value); }
      // Minimal parsing for control initial values. Real semantics checked independently in Python.
      for (const match of value.matchAll(/<(input|textarea|select|button|form|div|p|span|h3|dd|strong)\b([^>]*\bid="([^"]+)"[^>]*)>/g)) {
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
  main.querySelector=()=>({before(){},textContent: /<h1>([\s\S]*?)<\/h1>/.exec(html)?.[1].replace(/<[^>]*>/g,'') || ''});
  const nav = ['inicio','prototipo','requisitos','diseno','evidencias','evaluacion'].map(p=>({hash:'#'+p,setAttribute(){},removeAttribute(){}}));
  const window={addEventListener(event,fn){routes[event]=fn;},scrollTo(){},print(){window.printed=true;}};
  const location={hash:''};
  const context=vm.createContext({window,location,document:{querySelector:()=>main,querySelectorAll:()=>nav,getElementById:id=>elements.get(id),createElement:()=>({click(){},setAttribute(){}})},localStorage:{getItem:k=>storage.get(k)||null,setItem(k,v){if(failStorage)throw Error('denied');storage.set(k,v);}},URL:{createObjectURL:()=> 'blob:demo',revokeObjectURL(){}},Blob,setTimeout(){}});
  for(const file of ['data.js','demo.js','prototype.js','app.js']) vm.runInContext(fs.readFileSync(path.join(root,'js',file),'utf8'),context,{filename:file});
  return {window,storage,elements,snapshots,html:()=>html,go(hash){location.hash='#'+hash;routes.hashchange();},submit(id){const form=elements.get(id);const event={preventDefault(){},currentTarget:form};(form.onsubmit || form.listeners.submit)(event);}};
}


const snapshots=[];
test('alcance exclusivo: dos RF, seis apartados y sin rutas académicas adicionales',()=>{
  const app=load(); assert.equal(app.window.PortalData.requirements.length,2);
  for(const id of ['RF01','RF02']) {
    app.go('requisitos/'+id); const html=app.html();
    assert.equal((html.match(/<h1>/g)||[]).length,1);
    assert.equal((html.match(/<h2>[A-F]\. /g)||[]).length,6);
    assert.ok(!html.includes('G. Trazabilidad'));
    for(const col of ['Precondición','Acción','Evidencia verificable'])assert.ok(html.includes(col));
    assert.ok(html.includes('assets/data-model.svg'));
    assert.equal(app.elements.get('eval-status').value,'Sin evaluar');
    assert.equal(app.elements.get('eval-conclusion').value,''); // textarea contents tested in HTML below
    assert.match(app.elements.get('evaluation-host').innerHTML,/Sin evaluar/);
    for(const r of app.window.PortalData.requirements)for(const c of r.criteria)assert.ok(c.action && c.evidence);
    capture(app);
  }
  for(const route of ['requisitos/RF03','requisitos/RF12','diseno','evidencias','prototipo','evaluacion']){
    app.go(route);assert.match(app.html(),/Vista no encontrada/);capture(app);
  }
  app.go('inicio'); assert.match(app.html(),/incrementos posteriores/);capture(app);
});
function capture(app){
  let html=app.html();
  for(const id of ['prototype-host','evaluation-host']) html=html.replace(`<div id="${id}"></div>`,`<div id="${id}">${app.elements.get(id)?.innerHTML||''}</div>`);
  html=html.replace('<div id="demo-content"></div>',`<div id="demo-content">${app.elements.get('demo-content')?.innerHTML||''}</div>`);
  html=html.replace('<div id="demo-company-panel"></div>', `<div id="demo-company-panel">${app.elements.get('demo-company-panel')?.innerHTML||''}</div>`);
  html=html.replace('<div id="eval-summary"></div>',`<div id="eval-summary">${app.elements.get('eval-summary')?.innerHTML||''}</div>`);
  snapshots.push(html);
}
function account(app, email='consultor@example.test', password='DemoContinuitY12!') {
 app.elements.get('demo-email').value=email;
 app.elements.get('demo-password').value=password;
 if(app.elements.get('demo-name')) app.elements.get('demo-name').value='Consultor de práctica';
 if(app.elements.get('demo-confirm')) app.elements.get('demo-confirm').value=password;
}
test('prototipo: cuatro vistas, errores, cierre y lectura posterior; sin credenciales persistidas',()=>{
 const app=load();app.go('requisitos/RF01'); capture(app);
 app.elements.get('tab-register').click();account(app);
 app.elements.get('demo-password').value='corta';app.submit('demo-auth');
 assert.match(app.elements.get('demo-feedback').textContent,/12 y 1024/);
 account(app);app.elements.get('demo-confirm').value='distinta';app.submit('demo-auth');
 assert.match(app.elements.get('demo-feedback').textContent,/coincidir/);capture(app);
 account(app);app.submit('demo-auth');
 assert.match(app.elements.get('demo-feedback').textContent,/Cuenta creada correctamente/);
 account(app,undefined,'incorrecta');app.submit('demo-auth');
 assert.match(app.elements.get('demo-feedback').textContent,/incorrectos/);
 account(app);app.submit('demo-auth');capture(app);
 assert.equal(app.elements.get('demo-account-email').textContent,'consultor@example.test');
 app.elements.get('demo-show-company').click();capture(app);
 app.elements.get('company-name').value='TecniRed Sabana';app.elements.get('company-city').value='Bogotá';
 app.submit('demo-company');capture(app);
 assert.equal(app.elements.get('company-value-name').textContent,'TecniRed Sabana');
 app.go('requisitos/RF02');
 assert.equal(app.elements.get('company-value-name').textContent,'TecniRed Sabana');
 app.elements.get('demo-back').click();capture(app);
 app.elements.get('demo-logout').click();capture(app);assert.equal(app.storage.size,0);
 assert.ok(!app.elements.get('demo-content').innerHTML.includes('demo-logout'));
 account(app);app.submit('demo-auth');app.elements.get('demo-show-company').click();capture(app);
 assert.equal(app.elements.get('company-value-name').textContent,'TecniRed Sabana');
});
test('modelo: límites, duplicados normalizados, privacidad y asociación por usuario',()=>{
 const {window}=load(), demo=new window.ContinuityDemo();
 const a={name:'Práctica',email:'a@example.test',password:'DemoContinuitY12!',confirmation:'DemoContinuitY12!'};
 assert.throws(()=>demo.company(),/EXPIRADA/);assert.throws(()=>demo.registerCompany({}),/EXPIRADA/);
 for(const changes of [{name:' '},{name:'x'.repeat(121)},{email:'invalido'},{email:'a@real.local'},{email:'x'.repeat(250)+'@example.test'},{password:'x'.repeat(11)},{password:'x'.repeat(1025)},{confirmation:'distinta'}]) assert.throws(()=>demo.register({...a,...changes}));
 demo.register({...a,name:'x'.repeat(120),password:'x'.repeat(12),confirmation:'x'.repeat(12)});
 assert.throws(()=>demo.register({...a,email:' A@EXAMPLE.TEST '}),/registrado/);
 assert.throws(()=>demo.login(a.email,'incorrecta'),/incorrectos/);assert.equal(demo.active,null);
 demo.login(a.email,'x'.repeat(12));
 for(const [key,max] of [['nombre',150],['ciudad',100],['nit',20],['sector',100]]) {
  assert.throws(()=>demo.registerCompany({nombre:'Demo',ciudad:'Cali',[key]:'x'.repeat(max+1)}),new RegExp(key));
 }
 for(const key of ['nombre','ciudad']) assert.throws(()=>demo.registerCompany({nombre:'Demo',ciudad:'Cali',[key]:'   '}),new RegExp(key));
 demo.registerCompany({nombre:'x'.repeat(150),ciudad:'x'.repeat(100),nit:'x'.repeat(20),sector:'x'.repeat(100)});
 assert.throws(()=>demo.registerCompany({}),/Ya tienes/);
 demo.logout();demo.register({...a,email:'b@example.test'});demo.login('b@example.test',a.password);assert.equal(demo.company(),null);
 demo.registerCompany({nombre:' B ',ciudad:' Cali '});assert.equal(demo.company().nit,'');assert.equal(demo.company().nombre,'B');
 demo.logout();demo.login(a.email,'x'.repeat(12));assert.equal(demo.company().nombre.length,150);
 demo.logout();assert.throws(()=>demo.company(),/EXPIRADA/);
 assert.equal(new window.ContinuityDemo().accountState(a.email),'NO EXISTE');
});
test('evaluación: escape, guardado, descarga, impresión y almacenamiento denegado',()=>{
 const app=load();app.go('requisitos/RF02');
 app.elements.get('eval-status').value='Requiere ajustes';app.elements.get('eval-observations').value='<img onerror=x>';
 app.elements.get('eval-conclusion').value='Revisión académica';app.submit('evaluation-form');
 const saved=app.storage.get('continuity-academic-rf01-rf02-v2');assert.equal(JSON.parse(saved).RF02.conclusion,'Revisión académica');
 const restored=load(saved);restored.go('requisitos/RF02');
 assert.match(restored.elements.get('evaluation-host').innerHTML,/&lt;img/);
 restored.elements.get('download').click();restored.elements.get('print').click();assert.equal(restored.window.printed,true);capture(restored);
 const denied=load(null,true);denied.go('requisitos/RF01');denied.submit('evaluation-form');assert.match(denied.elements.get('eval-feedback').textContent,/No se pudo guardar/);
});
test('matrices referencian archivos y funciones reales, con estados limitados a la evidencia',()=>{
 const app=load();
 for(const rf of app.window.PortalData.requirements)for(const c of rf.criteria){
  for(const reference of c.evidence.split('; ')){
   const [file,fn]=reference.split('::');const source=fs.readFileSync(path.join(root,'..',file),'utf8');
   if(fn)assert.ok(source.includes('def '+fn+'('),reference);
  }
  if(c.status.startsWith('Cumple'))assert.ok(!c.evidence.includes('test_postgres') && !c.evidence.includes('test_bd0'));
 }
});
process.on('beforeExit',()=>{if(process.argv.includes('--snapshots'))fs.writeFileSync(process.argv[process.argv.indexOf('--snapshots')+1],JSON.stringify(snapshots));});
