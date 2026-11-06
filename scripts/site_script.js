'use strict';
const DATA=JSON.parse(document.getElementById('library-data').textContent);
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const external=(url,label,cls='')=>`<a class="${cls}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
const runnable=p=>['code','toolbox','unofficial'].includes(p.status);
const categoryMap=Object.fromEntries(DATA.categories.map(c=>[c.id,c]));
const venues=[...new Set(DATA.papers.map(p=>p.venue))].sort((a,b)=>a.localeCompare(b));
const packageName=w=>w.package;
const packages=[...new Set(DATA.papers.flatMap(p=>p.implementations.map(packageName)))].sort((a,b)=>a.localeCompare(b));
const defaults={view:'papers',topic:'all',q:'',alignment:'all',color:'all',status:'all',sort:'newest',year:'all',output:'all',package:'all',paper:''};
let state={...defaults,venues:[]},limit=24;

function readState(){
  const q=new URLSearchParams(location.search);
  state={...defaults,venues:[]};
  for(const key of Object.keys(defaults))if(q.has(key))state[key]=q.get(key);
  state.venues=[...new Set(q.getAll('venue').filter(v=>venues.includes(v)))];
  if(!['papers','datasets','tools','learn'].includes(state.view))state.view='papers';
  if(state.topic!=='all'&&!categoryMap[state.topic])state.topic='all';
  for(const [key,allowed] of Object.entries({alignment:Object.keys(UI.alignments),color:Object.keys(UI.colors),
      status:['runnable','spec','unreleased'],sort:['newest','ready','az'],year:DATA.papers.map(p=>String(p.year)),
      output:Object.keys(UI.outputs),package:['official',...packages]})){
    if(state[key]!=='all'&&!allowed.includes(state[key]))state[key]=defaults[key];
  }
  if(state.paper&&!DATA.papers.some(p=>p.name===state.paper))state.paper='';
}
function urlState(){
  const q=new URLSearchParams();
  for(const [key,value] of Object.entries(state)){
    if(key==='venues')continue;
    if(value!==defaults[key]&&value!=='')q.set(key,value);
  }
  state.venues.forEach(v=>q.append('venue',v));
  return q.toString();
}
function saveState(){
  const q=urlState();
  history.replaceState(null,'',location.pathname+(q?'?'+q:'')+location.hash);
  $('languageLink').href=ALT_FILE+(q?'?'+q:'')+location.hash;
}
function matches(value){
  const terms=state.q.toLocaleLowerCase().split(/\s+/).filter(Boolean);
  const hay=String(value).toLocaleLowerCase();
  return terms.every(t=>hay.includes(t));
}
function hasPackage(p){
  return state.package==='all'||(state.package==='official'?Boolean(p.code)&&p.status==='code':
    p.implementations.some(w=>packageName(w)===state.package));
}
function filteredPapers(){
  return DATA.papers.filter(p=>(!state.paper||p.name===state.paper)&&
    (state.topic==='all'||p.category===state.topic)&&(!state.venues.length||state.venues.includes(p.venue))&&
    (state.alignment==='all'||p.align===state.alignment)&&(state.color==='all'||p.color===state.color)&&
    (state.year==='all'||String(p.year)===state.year)&&(state.output==='all'||p.output===state.output)&&hasPackage(p)&&
    (state.status==='all'||(state.status==='runnable'?runnable(p):state.status==='spec'?p.status==='spec':!runnable(p)&&p.status!=='spec'))&&
    matches([p.name,p.title,p.translation,p.summary,p.note,p.venue,p.search,categoryMap[p.category].title,
      ...p.implementations.map(w=>w.label)].join(' ')))
    .sort((a,b)=>{
      if(state.sort==='az')return a.title.localeCompare(b.title);
      if(state.sort==='ready'&&runnable(a)!==runnable(b))return runnable(a)?-1:1;
      return b.year-a.year||a.title.localeCompare(b.title);
    });
}
function nav(){
  const counts=Object.fromEntries(DATA.categories.map(c=>[c.id,DATA.papers.filter(p=>p.category===c.id).length]));
  const button=(id,label,count)=>`<button type="button" class="topic" data-topic="${id}" aria-current="${state.view==='papers'&&state.topic===id}"><span>${esc(label)}</span><b>${count}</b></button>`;
  $('topicNav').innerHTML=button('all',UI.all,DATA.papers.length)+DATA.navigation.map(g=>
    `<div class="nav-label">${esc(g.title)}</div>${g.categories.map(id=>button(id,categoryMap[id].short,counts[id])).join('')}`).join('');
}
function paperCard(p){
  const tags=[UI.alignments[p.align]?.[0],UI.colors[p.color]?.[0],UI.outputs[p.output]].filter(Boolean);
  const link=p.code?external(p.code,p.code.includes('github.com')?'GitHub ↗':UI.codeLink+' ↗','code-link'):'';
  const impl=p.implementations.map(w=>external(w.url,w.label));
  const datasets=DATA.datasets.filter(ds=>ds.source&&p.name.toLowerCase().includes(ds.source.toLowerCase()));
  const resources=[...impl,...datasets.map(ds=>external(ds.url,ds.name+' ↗'))];
  return `<article class="paper-card" data-paper="${esc(p.name)}"><div class="paper-meta"><span class="paper-publication">${p.year} · ${esc(p.venue)}</span><span>${esc(categoryMap[p.category].short)}</span>${tags.map(t=>`<span class="method-tag">${esc(t)}</span>`).join('')}<span class="paper-release"><span class="status status-${esc(p.status)}">${esc(UI.statuses[p.status])}</span>${link}</span></div><h3 class="paper-name">${external(p.paper,p.title)}</h3>${p.translation?`<p class="paper-translation">${esc(p.translation)}</p>`:''}<p class="paper-summary">${esc(p.summary)}</p>${resources.length?`<div class="paper-links">${resources.join('')}</div>`:''}${p.note?`<details class="paper-note"><summary>${esc(UI.notes)}</summary><p>${esc(p.note)}</p></details>`:''}</article>`;
}
function empty(){return `<div class="empty"><h3>${esc(UI.empty)}</h3><p>${esc(UI.emptyHelp)}</p></div>`;}
function resourceCards(items,kind){
  return `<div class="resource-grid">${items.map(x=>kind==='datasets'?
    `<article class="resource-card"><div class="resource-meta">${x.year} · ${esc(x.source||'')}</div><h3>${esc(x.name)}</h3><p>${esc(x.capture||'')}</p><dl><dt>${esc(UI.size)}</dt><dd>${esc(x.size||'—')}</dd><dt>${esc(UI.use)}</dt><dd>${esc(x.use)}</dd></dl>${external(x.url,UI.download,'resource-link')}</article>`:
    `<article class="resource-card"><div class="resource-meta">${esc(x.language||'')}</div><h3>${external(x.url,x.name)}</h3><p>${esc(x.description)}</p>${external(x.url,x.name+' ↗','resource-link')}</article>`).join('')}</div>`;
}
function renderResults(){
  const papers=state.view==='papers';
  $('paperFilters').hidden=!papers;
  $('categoryDescription').hidden=!papers||state.topic==='all';
  $('categoryDescription').textContent=categoryMap[state.topic]?.description||'';
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===state.view)));
  let items=[],content='';
  if(papers){
    items=filteredPapers();content=`<div class="paper-list">${items.slice(0,limit).map(paperCard).join('')}</div>`;
    $('resultTitle').textContent=state.paper||categoryMap[state.topic]?.title||UI.all;
  }else if(state.view==='learn'){
    const groups={tutorials:UI.tutorials,books:UI.books,related_lists:UI.related};
    for(const [kind,resources] of Object.entries(DATA.resources)){
      const filtered=resources.filter(x=>matches([x.name,x.description].join(' ')));items.push(...filtered);
      if(filtered.length)content+=`<div class="learning-group"><h3>${esc(groups[kind]||UI.learn)}</h3>${filtered.map(x=>`<article class="learning-item">${external(x.url,x.name+' ↗')}<p>${esc(x.description)}</p></article>`).join('')}</div>`;
    }
    $('resultTitle').textContent=UI.learn;
  }else{
    items=DATA[state.view].filter(x=>matches(Object.values(x).join(' ')));
    if(state.view==='datasets')items.sort((a,b)=>b.year-a.year||a.name.localeCompare(b.name));
    content=resourceCards(items,state.view);$('resultTitle').textContent=state.view==='datasets'?UI.datasetsTab:UI.tools;
  }
  $('results').innerHTML=items.length?content:empty();
  $('resultCount').textContent=`${items.length} ${UI.results}`;
  $('showMore').hidden=!papers||items.length<=limit;
  $('showMore').textContent=`${UI.more} (${Math.min(24,Math.max(0,items.length-limit))}) ↓`;
  nav();chips();saveState();
}
function chips(){
  const entries=[];
  if(state.q)entries.push(['q',state.q]);
  if(state.view==='papers'){
    if(state.topic!=='all')entries.push(['topic',categoryMap[state.topic].short]);
    if(state.paper)entries.push(['paper',state.paper]);
    for(const key of ['alignment','color','status','year','output','package'])if(state[key]!=='all'){
      const select=$(key);entries.push([key,select.options[select.selectedIndex]?.textContent||state[key]]);
    }
    state.venues.forEach(v=>entries.push(['venue',v]));
  }
  $('activeFilters').hidden=!entries.length;
  $('activeFilters').innerHTML=entries.map(([key,value])=>`<button type="button" class="filter-chip" data-remove="${key}" data-value="${esc(value)}" aria-label="${esc(UI.remove+': '+value)}">${esc(value)} ×</button>`).join('');
}
function sync(){
  $('search').value=state.q;
  for(const key of ['alignment','color','status','sort','year','output','package'])$(key).value=state[key];
  $('venueSummary').textContent=state.venues.length?`${state.venues.length} ${UI.selectedVenues}`:UI.venues;
  $('venueOptions').querySelectorAll('input').forEach(x=>{x.checked=state.venues.includes(x.value);});
}
function change(){limit=24;sync();renderResults();}
function menu(open){
  $('sidebar').classList.toggle('open',open);$('backdrop').classList.toggle('open',open);
  $('menuButton').setAttribute('aria-expanded',String(open));
  if(open)$('topicNav').querySelector('button')?.focus();
}
function initialize(){
  for(const [id,options] of Object.entries({alignment:Object.entries(UI.alignments).map(([k,v])=>[k,v[0]]),
    color:Object.entries(UI.colors).map(([k,v])=>[k,v[0]]),output:Object.entries(UI.outputs),
    year:[...new Set(DATA.papers.map(p=>p.year))].sort((a,b)=>b-a).map(y=>[String(y),String(y)]),
    package:[['official',UI.official],...packages.map(p=>[p,p==='this repo'?UI.ownRepo:p])]})){
    $(id).insertAdjacentHTML('beforeend',options.map(([value,label])=>`<option value="${esc(value)}">${esc(label)}</option>`).join(''));
  }
  $('venueOptions').innerHTML=venues.map((v,i)=>`<label for="venue-${i}"><input id="venue-${i}" type="checkbox" value="${esc(v)}">${esc(v)}</label>`).join('');
  $('labelGuide').innerHTML=[...Object.values(UI.alignments),...Object.values(UI.colors)].map(([label,desc])=>`<p><b>${esc(label)}</b> · ${esc(desc)}</p>`).join('')+`<p class="signal">${esc(UI.signal)}</p>`;
  $('trends').innerHTML=DATA.trends.map((t,i)=>`<article class="trend"><span class="trend-num">${String(i+1).padStart(2,'0')}</span><h3>${esc(t.title)}</h3><p>${esc(t.text)}</p><p class="examples">${esc(t.examples)}</p></article>`).join('');
  $('topicNav').addEventListener('click',e=>{
    const b=e.target.closest('[data-topic]');if(!b)return;
    state.topic=b.dataset.topic;state.view='papers';state.paper='';menu(false);change();
    $('library').scrollIntoView({block:'start'});
  });
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{state.view=b.dataset.view;state.paper='';change();}));
  $('search').addEventListener('input',e=>{state.q=e.target.value.trim();state.paper='';limit=24;renderResults();});
  for(const key of ['alignment','color','status','sort','year','output','package'])$(key).addEventListener('change',e=>{state[key]=e.target.value;change();});
  $('venueOptions').addEventListener('change',()=>{state.venues=[...$('venueOptions').querySelectorAll('input:checked')].map(x=>x.value);change();});
  $('venueClear').addEventListener('click',()=>{state.venues=[];change();});
  $('venuePreset').addEventListener('click',()=>{state.venues=['CVPR','ICCV','ECCV'].filter(v=>venues.includes(v));change();});
  $('activeFilters').addEventListener('click',e=>{
    const b=e.target.closest('[data-remove]');if(!b)return;
    if(b.dataset.remove==='venue')state.venues=state.venues.filter(v=>v!==b.dataset.value);
    else state[b.dataset.remove]=defaults[b.dataset.remove];change();
  });
  $('reset').addEventListener('click',()=>{state={...defaults,venues:[]};change();});
  $('showMore').addEventListener('click',()=>{limit+=24;renderResults();});
  $('menuButton').addEventListener('click',()=>menu(!$('sidebar').classList.contains('open')));
  $('backdrop').addEventListener('click',()=>{menu(false);$('menuButton').focus();});
  document.addEventListener('click',e=>{if(!$('venueFilter').contains(e.target))$('venueFilter').open=false;});
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if($('sidebar').classList.contains('open')){menu(false);$('menuButton').focus();}if($('venueFilter').open){$('venueFilter').open=false;$('venueSummary').focus();}}
    if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)&&!e.ctrlKey&&!e.metaKey&&!e.altKey){e.preventDefault();$('search').focus();}
  });
  window.addEventListener('popstate',()=>{readState();change();});
  readState();change();
}
initialize();
