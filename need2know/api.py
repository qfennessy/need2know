from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .config import Settings
from .service import make_store, query

settings = Settings.from_env()
store = make_store(settings)
app = FastAPI(title="Need2Know audit API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

DEMO_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Need to Know</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f1e8;color:#17221c;font:18px/1.55 ui-sans-serif,system-ui}main{max-width:1160px;margin:auto;padding:48px 24px 80px}h1{font:700 64px/1 Georgia;margin:8px 0 12px;letter-spacing:-2px}h2{font:700 36px/1.15 Georgia;margin:0 0 8px}h3{font-size:24px;margin:0 0 8px}.tag{color:#526159;font-size:23px;max-width:820px;margin:0 0 34px}.eyebrow{color:#286248;font-size:14px;font-weight:800;letter-spacing:.12em}.map{background:#17221c;color:#fff;border-radius:24px;padding:28px;margin-bottom:26px}.map-title{font:700 27px Georgia;margin:0 0 5px}.map-intro{color:#cbd5cf;margin:0 0 22px}.entities{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}.entity{min-height:245px;border-radius:17px;padding:20px;color:#17221c;position:relative}.entity.memory-box{background:#dceae3}.entity.agent-box{background:#dce7f2}.entity.question-box{background:#f4e5be}.entity-kind{font-size:13px;font-weight:900;letter-spacing:.1em;text-transform:uppercase;margin-bottom:7px}.entity h3{font:700 27px Georgia;margin:0 0 7px}.entity-copy{font-size:16px;line-height:1.4;margin:0 0 15px}.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{font-size:13px;font-weight:750;padding:4px 8px;border-radius:99px;background:#ffffffa8}.agent-mini{padding:8px 10px;background:#ffffff9c;border-radius:9px;margin-top:7px;font-size:14px;line-height:1.3}.agent-mini b{display:block}.live-question{background:#fff9e9;border:1px solid #dbc47f;padding:11px;border-radius:10px;font-weight:750;font-size:15px}.stable{position:absolute;bottom:15px;left:20px;font-size:13px;font-weight:800;opacity:.64}.flow{display:grid;grid-template-columns:1fr auto 1.25fr auto 1fr;align-items:center;gap:12px;margin-top:16px;text-align:center}.flow-node{background:#26352d;border:1px solid #43564a;border-radius:13px;padding:13px}.flow-node b{display:block}.flow-node span{font-size:14px;color:#bdcbc2}.arrow{font-size:24px;color:#a6b8ad}.card{background:#fff;border:1px solid #d9d5ca;border-radius:20px;padding:32px;margin:20px 0;box-shadow:0 4px 22px #1520190d}.section-intro{color:#59665e;font-size:19px;margin:0 0 22px}.run{display:grid;grid-template-columns:260px 1fr auto;gap:12px}label{display:block;font-size:14px;font-weight:800;margin:0 0 7px;color:#425047}select,input,button{width:100%;font:inherit;font-size:17px;padding:14px 15px;border-radius:11px;border:1px solid #aeb9b1;background:white}button{width:auto;align-self:end;background:#174b38;color:white;border:0;font-weight:800;cursor:pointer;padding-inline:22px}button:disabled{opacity:.5}.pill{display:inline-block;background:#e2eee6;color:#174b38;padding:6px 12px;border-radius:99px;font-size:15px;font-weight:800}.withhold{background:#eeeae2;color:#665d53}.soft{background:#fff0bd;color:#6e5200}.full{background:#dbeee2;color:#174b38}.purpose{margin:16px 0 0;padding:14px 16px;background:#f3f6f3;border-radius:12px}.result{margin-top:20px;border-top:1px solid #e5e3dc;padding-top:20px}.muted{color:#637067;font-size:16px}.legend{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 24px}.empty{padding:20px;background:#f5f3ee;border-radius:12px}.status-copy{font-size:21px;font-weight:750}.query-group{border:1px solid #ddd9cf;border-radius:16px;padding:22px;margin-top:16px}.query-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px}.query-head b{font-size:21px}.query-text{font:700 25px/1.3 Georgia;margin:8px 0 18px}.release-row{background:#f2f7f3;border-radius:12px;padding:15px 17px;margin-top:10px}.release-row .memory-text{font-size:21px;font-weight:750}.query-summary{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:14px;color:#59665e;font-size:16px}.count{font-size:16px;color:#637067}@media(max-width:760px){main{padding:28px 16px}body{font-size:17px}h1{font-size:46px}.tag{font-size:20px}.run,.entities,.flow{grid-template-columns:1fr}.entity{min-height:auto;padding-bottom:48px}.arrow{transform:rotate(90deg)}button{width:100%}}
/* Keep the persistent/temporary labels clear of the example content. */
.entity{min-height:270px}
@media(max-width:760px){.entity{min-height:auto}}
</style></head><body><main><div class="eyebrow">YOUR PRIVATE AI MEMORY</div><h1>Need to Know</h1><p class="tag">Memories are what you know. Agent roles define who is asking. Test questions are the temporary tasks they ask about. Need to Know keeps those three things separate.</p>
<section class="map"><div class="map-title">Three different things enter every access decision</div><p class="map-intro">They never become one shared profile. The judge compares them for one request at a time.</p><div class="entities"><article class="entity memory-box"><div class="entity-kind">1 · Private source</div><h3>Memories</h3><p class="entity-copy">Facts about you, stored locally. They stay private until a specific request justifies sharing.</p><div class="chips"><span class="chip">Health</span><span class="chip">Family</span><span class="chip">Business</span><span class="chip">Hobbies</span><span class="chip">Travel</span><span class="chip">Technical</span></div><div class="stable">25 stored facts · persistent</div></article><article class="entity agent-box"><div class="entity-kind">2 · Known requester</div><h3>Agents + roles</h3><p class="entity-copy">Each assistant has a fixed job written by you. Its role limits what it should reasonably know.</p><div id="agent-examples"><div class="agent-mini"><b>Codex</b>writes code in my projects</div><div class="agent-mini"><b>Muse</b>plans travel and restaurants</div><div class="agent-mini"><b>Claude Health</b>helps with health and medications</div></div><div class="stable">Registered once · persistent</div></article><article class="entity question-box"><div class="entity-kind">3 · Current task</div><h3>Test question</h3><p class="entity-copy">One concrete request made right now. It does not change the agent’s role or create a new permission.</p><div id="question-preview" class="live-question">“Find a good restaurant for my trip to Lisbon”</div><div class="stable">Used once · temporary</div></article></div><div class="flow"><div class="flow-node"><b>Relevant memories</b><span>Retrieved locally</span></div><div class="arrow">→</div><div class="flow-node"><b>Jev compares all three</b><span>Needed? Expected? Exact or safer?</span></div><div class="arrow">→</div><div class="flow-node"><b>Minimum access</b><span>Exact · safer · nothing</span></div></div></section>
<section class="card"><h2>Try an assistant</h2><p class="section-intro">Choose who is asking, then describe the task. The assistant’s job stays fixed, so it cannot simply claim a new reason for access.</p><div class="run"><div><label for="agent">Who is asking?</label><select id="agent"></select></div><div><label for="request">What are they trying to do?</label><input id="request" value="Find a good restaurant for my trip to Lisbon"></div><button id="ask">Check access</button></div><p id="purpose" class="purpose"></p><div id="result" class="result"></div></section>
<section class="card"><h2>Recent access decisions</h2><p class="section-intro">One card per test question. See who asked, what they asked, and what—if anything—they learned.</p><div class="legend"><span class="pill full">Shared exactly</span><span class="pill soft">Shared safely</span><span class="pill withhold">Kept private</span></div><div id="log">Loading recent decisions…</div></section></main>
<section class="protocol-docs">
  <div class="eyebrow">IMPLEMENTATION NOTES</div>
  <h2>How agents call Need to Know</h2>
  <p>Every agent launches the same local FastMCP service with its own fixed <code>N2K_AGENT_ID</code>. The identity comes from its connection configuration, not from the prompt.</p>
  <div class="config"><b>Example agent configuration</b><pre>N2K_AGENT_ID=claude-health
uv --directory /Users/quentinfennessy/src/need2know-codex-fast-prototype run need2know-mcp</pre></div>
  <div class="protocol-grid">
    <article><h3>Tool input: <code>recall</code></h3><pre>{
  "request": "What restaurant accommodations do I need while traveling?",
  "max_memories": 8
}</pre><p>The server uses the fixed agent identity and role, retrieves a short local candidate list, and sends one batched Jev request.</p></article>
    <article><h3>What Need to Know sends to Jev</h3><pre>{
  "model": "jev-latest",
  "state": { "agent_purpose": "plans travel", "agent_request": "...", "candidate_facts": ["relevant facts only"] },
  "questions": { "need_5": "Is this needed?", "expected_5": "Is this role expected to know it?", "disclosure_5": ["full", "soft", "withhold"] }
}</pre></article>
    <article><h3>Jev output → tool result</h3><pre>{
  "answers": { "need_5": { "noul": 0.89 }, "expected_5": { "noul": 0.94 }, "disclosure_5": { "choice": "soft" } }
}

→ { "memories": [{ "disclosure": "soft", "memory": "Prioritize low-fiber food…" }] }</pre></article>
  </div>
  <div class="rule"><b>Fail-closed release rule:</b> need ≥ 55%, expected access ≥ 65%, and Jev must choose <code>full</code> or <code>soft</code>. A timeout, malformed response, or any error returns no memories.</div>
</section>
<style>
.protocol-docs{max-width:1420px;margin:54px auto 70px;padding:28px;background:#fff;border:1px solid #d8d3c9;border-radius:20px}
.protocol-docs h2{font:700 36px/1.1 Georgia;margin:5px 0}.protocol-docs>p{max-width:820px;color:#59665e;font-size:19px}.config{margin:22px 0;padding:16px;border-radius:12px;background:#edf4ef}.config b{display:block;margin-bottom:8px}.protocol-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.protocol-grid article{border:1px solid #e1ded6;border-radius:13px;padding:16px}.protocol-grid h3{margin:0 0 9px;font-size:18px}.protocol-grid p{font-size:15px;color:#59665e}.protocol-docs pre{margin:0;overflow:auto;background:#17221c;color:#e2eee5;border-radius:10px;padding:13px;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}.rule{margin-top:16px;padding:15px 17px;background:#fff0bd;color:#57420a;border-radius:12px;font-size:17px}@media(max-width:700px){.protocol-docs{margin:32px 15px}.protocol-grid{grid-template-columns:1fr}}
</style>
<script>
let agents=[];const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function load(){let d=await fetch('/api/audit').then(r=>r.json());agents=d.agents;agent.innerHTML=agents.map(a=>`<option value="${esc(a.id)}">${esc(a.name)}</option>`).join('');agent.onchange=purpose;request.oninput=previewQuestion;purpose();previewQuestion();render(d.decisions)}
function purpose(){let a=agents.find(x=>x.id===agent.value);document.querySelector('#purpose').innerHTML=a?`<b>This assistant’s job:</b> ${esc(a.purpose)}`:''}
function previewQuestion(){document.querySelector('#question-preview').textContent=`“${request.value||'Type a test question below'}”`}
const labels={full:'Shared exactly',soft:'Shared safely',withhold:'Kept private'};
function render(ds){let groups=[];for(let d of ds){let g=groups.find(x=>x.id===d.query_id);if(!g){g={id:d.query_id,agent:d.agent_name,purpose:d.purpose,request:d.request,items:[]};groups.push(g)}g.items.push(d)}groups=groups.slice(0,6);log.innerHTML=groups.length?groups.map(g=>{let shared=g.items.filter(x=>x.outcome!=='withhold'),hidden=g.items.length-shared.length;return `<article class="query-group"><div class="query-head"><span class="pill">Agent</span><b>${esc(g.agent)}</b><span class="muted">${esc(g.purpose)}</span></div><div class="query-text">“${esc(g.request)}”</div>${shared.length?shared.map(d=>`<div class="release-row"><span class="pill ${d.outcome}">${labels[d.outcome]}</span> <span class="memory-text">${esc(d.released_text)}</span></div>`).join(''):`<div class="empty"><b>Nothing was shared.</b> None of the relevant memories passed both access checks.</div>`}<div class="query-summary"><span class="pill withhold">${hidden} kept private</span><span>${g.items.length} relevant memories checked · audit #${g.id}</span></div></article>`}).join(''):'<div class="empty">No decisions yet. Try an assistant above to see how the door works.</div>'}
ask.onclick=async()=>{ask.disabled=true;ask.textContent='Checking…';result.innerHTML='<p>Finding relevant memories and asking the access judge…</p>';try{let r=await fetch('/api/query',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({agent_id:agent.value,request:request.value})});let d=await r.json();if(!r.ok)throw Error(d.detail);result.innerHTML=`<h3>What this assistant learned</h3>${d.memories.length?d.memories.map(m=>`<p><span class="pill ${m.disclosure}">${labels[m.disclosure]}</span> <span class="status-copy">${esc(m.memory)}</span></p>`).join(''):'<div class="empty"><b>Nothing was shared.</b> The request did not justify access to any candidate memory.</div>'}<p class="muted">This check is saved in the decision log as audit #${d.query_id}.</p>`;await load()}catch(e){result.textContent=e.message}finally{ask.disabled=false;ask.textContent='Check access'}};load();
</script></body></html>"""

TERMINAL_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Need to Know · Agent sessions</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eee9df;color:#17221c;font:18px/1.5 ui-sans-serif,system-ui}main{max-width:1420px;margin:auto;padding:38px 28px 70px}.eyebrow{font-size:13px;font-weight:900;letter-spacing:.14em;color:#286248}.top{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:7px 0 28px}h1{font:700 57px/1 Georgia;margin:0;letter-spacing:-1.5px}.subtitle{max-width:680px;color:#58665d;font-size:21px;margin:12px 0 0}.store{background:#17221c;color:#fff;border-radius:18px;padding:16px 20px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}.store b{font-size:18px}.store span{font-size:15px;color:#c1cec6}.dot{width:10px;height:10px;border-radius:50%;background:#72d49c;box-shadow:0 0 0 4px #72d49c33}.explain{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center;gap:13px;background:#fff;border:1px solid #d8d3c9;border-radius:18px;padding:17px 20px;margin-bottom:25px}.explain b{display:block;font-size:17px}.explain span{color:#637067;font-size:15px}.arrow{font-size:25px;color:#799080}.terminal-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.terminal{background:#152019;border:1px solid #33453a;border-radius:19px;overflow:hidden;box-shadow:0 8px 24px #15201922;min-height:620px}.terminal-head{background:#24342b;padding:13px 15px;display:flex;align-items:center;gap:8px;color:#e8eee9;font-size:15px;font-weight:800}.lights{display:flex;gap:5px;margin-right:4px}.light{width:10px;height:10px;border-radius:50%;background:#e26d61}.light:nth-child(2){background:#e5c763}.light:nth-child(3){background:#70bd83}.terminal-body{padding:21px;color:#dce6df}.agent-label{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:15px}.agent-label h2{font:700 28px/1 Georgia;color:#fff;margin:0}.role{background:#284136;color:#c7e6d1;padding:8px 10px;border-radius:9px;font-size:14px;line-height:1.35;margin-bottom:18px}.role b{display:block;color:#fff}.test-label{font-size:13px;font-weight:900;letter-spacing:.08em;color:#bdcbc2;margin:0 0 7px}.test-entry{display:flex;gap:8px}.test-entry input{min-width:0;flex:1;border:1px solid #53665a;background:#0e1712;color:#fff;border-radius:9px;padding:10px;font:14px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}.test-entry button{border:0;border-radius:9px;background:#75dd9c;color:#112219;font-weight:900;padding:9px 11px;cursor:pointer}.test-entry button:disabled{opacity:.55}.command{font:16px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:#fff;margin:16px 0 12px}.prompt{color:#75dd9c}.mcp{color:#e6c66b}.reply{margin-top:18px;border-left:3px solid #75dd9c;background:#1e2b24;border-radius:0 10px 10px 0;padding:14px 15px;color:#f4f6f4;font-size:19px;font-weight:650;min-height:92px}.reply.private{border-color:#b8ada0;background:#2a2925;color:#e8e2db}.status{display:inline-flex;align-items:center;gap:7px;border-radius:99px;padding:5px 9px;font-size:12px;font-weight:900;letter-spacing:.04em;background:#234b35;color:#bce5c8}.status.waiting{background:#443d2b;color:#e9d18d}.status i{width:7px;height:7px;border-radius:50%;background:currentColor}.meta{margin-top:18px;padding-top:15px;border-top:1px solid #39483f;color:#9fac9f;font-size:14px}.note{margin-top:24px;color:#647067;font-size:16px}@media(max-width:980px){.terminal-grid{grid-template-columns:1fr}.explain{grid-template-columns:1fr}.arrow{transform:rotate(90deg)}.top{display:block}}@media(max-width:600px){main{padding:25px 15px}h1{font-size:43px}.subtitle{font-size:19px}}
</style></head><body><main><div class="eyebrow">NEED TO KNOW · SESSION WALL</div><div class="top"><div><h1>Three agents. One private door.</h1><p class="subtitle">Each terminal is a separate AI assistant. It has a fixed role, asks one temporary question, and receives only the minimum memory needed to answer it.</p></div></div>
<section class="store"><i class="dot"></i><b>One local memory store</b><span>25 private facts · SQLite + sqlite-vec · every decision is audited</span></section>
<section class="explain"><div><b>1. Agent + role</b><span>Who is asking, and what job do they have?</span></div><div class="arrow">→</div><div><b>2. Test question</b><span>What does that agent need for this one task?</span></div><div class="arrow">→</div><div><b>3. Result</b><span>Jev chooses: exact fact, safer version, or nothing.</span></div></section>
<section class="terminal-grid" id="sessions"><div class="terminal"><div class="terminal-head"><span class="lights"><i class="light"></i><i class="light"></i><i class="light"></i></span>Loading sessions…</div></div></section><p class="note">Claude is connected through the actual project MCP server. Codex and Muse are ready for their own MCP configuration next.</p><section class="facts"><div class="facts-head"><div><div class="eyebrow">LOCAL MEMORY STORE</div><h2>Everything saved here</h2><p>These are the exact private facts in your local Need to Know database. Assistants only receive a fact when the access check allows it.</p></div><span id="fact-count" class="fact-count">Loading…</span></div><div id="fact-list" class="fact-list"></div></section></main><style>.facts{margin-top:54px;background:#fff;border:1px solid #d8d3c9;border-radius:20px;padding:28px}.facts-head{display:flex;justify-content:space-between;gap:22px;align-items:start}.facts h2{font:700 36px/1.1 Georgia;margin:5px 0}.facts p{max-width:720px;color:#59665e;margin:8px 0 0}.fact-count{white-space:nowrap;background:#e1eee5;color:#1c593d;border-radius:999px;padding:8px 12px;font-size:15px;font-weight:900}.fact-list{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:24px}.fact{border:1px solid #e1ded6;border-radius:13px;padding:16px}.fact p{color:#17221c;font-weight:700;font-size:18px;line-height:1.35;margin:11px 0 9px}.fact small{display:block;color:#66736a;line-height:1.4}.fact-category,.fact-sensitivity{display:inline-block;border-radius:999px;padding:4px 8px;font-size:12px;font-weight:900}.fact-category{background:#dceae3;color:#175139;text-transform:capitalize}.fact-sensitivity{background:#eeeae2;color:#665d53;margin-left:5px}@media(max-width:700px){.facts-head,.fact-list{display:block}.fact{margin-top:10px}.fact-count{display:inline-block;margin-top:15px}}</style>
<script>
const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const panels=[{id:'claude-health',name:'Claude Health',shell:'claude@health',state:'connected',connection:'MCP connected',role:'helps with health, medications, symptoms, appointments, and food needs'},{id:'codex-code',name:'Codex',shell:'codex@projects',state:'waiting',connection:'MCP next',role:'writes code in my projects and helps with my software development setup'},{id:'muse-travel',name:'Muse',shell:'muse@travel',state:'waiting',connection:'MCP next',role:'plans travel, restaurants, lodging, and activities that fit my preferences and access needs'}];
let audit=[],tests={};
function latestGroup(p){let rows=audit.filter(d=>d.agent_id===p.id&&(p.id!=='claude-health'||d.client==='mcp'));if(!rows.length)return null;let id=Math.max(...rows.map(d=>d.query_id));return {query_id:id,request:rows.find(d=>d.query_id===id).request,items:rows.filter(d=>d.query_id===id)}}
function panel(p){let g=tests[p.id]||latestGroup(p),shared=g?.memories||g?.items.filter(x=>x.outcome!=='withhold')||[];let result=shared.length?shared.map(d=>d.memory||d.released_text).join(' '):'Nothing was shared.';let privateCount=g?.withheld_count??(g?g.items.length-shared.length:0);let request=g?.request||'';let actual=p.state==='connected'&&!tests[p.id]&&g?.items?.[0]?.client==='mcp';return `<article class="terminal"><header class="terminal-head"><span class="lights"><i class="light"></i><i class="light"></i><i class="light"></i></span>${esc(p.shell)}<span style="margin-left:auto" class="status ${p.state==='waiting'?'waiting':''}"><i></i>${esc(p.connection)}</span></header><div class="terminal-body"><div class="agent-label"><h2>${esc(p.name)}</h2><span class="status ${p.state==='waiting'?'waiting':''}">${actual?'LIVE':p.state==='waiting'?'NEXT':'TEST'}</span></div><div class="role"><b>Fixed role</b>${esc(p.role)}</div><div class="test-label">TEST PROMPT</div><div class="test-entry"><input id="input-${p.id}" value="${esc(request)}" placeholder="Ask this agent something…"><button id="run-${p.id}" onclick="runTest('${p.id}')">Run test</button></div><div class="command"><span class="prompt">${esc(p.shell)} $</span> <span class="mcp">recall</span><br>“${esc(request||'Waiting for your test prompt…')}”</div><div class="reply ${shared.length?'':'private'}"><span class="mcp">RESULT</span><br>${esc(result)}</div><div class="meta">${g?`${shared.length} memory shared · ${privateCount} kept private · audit #${g.query_id}`:'No audit entry yet'}${actual?' · real Claude MCP session':tests[p.id]?' · dashboard test':''}</div></div></article>`}
function render(){document.querySelector('#sessions').innerHTML=panels.map(panel).join('')}
function renderFacts(facts){document.querySelector('#fact-count').textContent=`${facts.length} facts saved locally`;document.querySelector('#fact-list').innerHTML=facts.map(f=>`<article class="fact"><div><span class="fact-category">${esc(f.category)}</span><span class="fact-sensitivity">${esc(f.sensitivity)} sensitivity</span></div><p>${esc(f.fact)}</p><small>Safer version: ${esc(f.soft_fact)}</small></article>`).join('')}
async function runTest(agentId){const input=document.querySelector('#input-'+agentId),button=document.querySelector('#run-'+agentId),request=input.value.trim();if(!request)return;button.disabled=true;button.textContent='Running…';try{let response=await fetch('/api/query',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({agent_id:agentId,request})}),data=await response.json();if(!response.ok)throw Error(data.detail);tests[agentId]={...data,request};render()}catch(error){button.textContent=error.message}finally{if(document.body.contains(button)){button.disabled=false;button.textContent='Run test'}}}
async function load(){const [auditResponse,factResponse]=await Promise.all([fetch('/api/audit'),fetch('/api/facts')]);const d=await auditResponse.json();audit=d.decisions;render();renderFacts(await factResponse.json())};load();
</script></body></html>"""

PROTOCOL_DOCS = """
<section class="protocol-docs">
  <div class="eyebrow">IMPLEMENTATION NOTES</div>
  <h2>How agents call Need to Know</h2>
  <p>Each agent runs the same local FastMCP service, but with a fixed <code>N2K_AGENT_ID</code>. Identity comes from the connection configuration—not from a prompt an agent can change.</p>
  <div class="config"><b>Example configuration</b><pre>N2K_AGENT_ID=claude-health
uv --directory /Users/quentinfennessy/src/need2know-codex-fast-prototype run need2know-mcp</pre></div>
  <div class="protocol-grid">
    <article><h3>Tool input: <code>recall</code></h3><pre>{
  "request": "What restaurant accommodations do I need while traveling?",
  "max_memories": 8
}</pre><p>Need to Know uses that fixed identity and role, then retrieves only a short local candidate list.</p></article>
    <article><h3>One batched Jev request</h3><pre>{
  "model": "jev-latest",
  "state": {
    "agent_purpose": "plans travel",
    "agent_request": "...",
    "candidate_facts": ["relevant facts only"]
  },
  "questions": {
    "need_5": "Is this needed?",
    "expected_5": "Is this role expected to know it?",
    "disclosure_5": ["full", "soft", "withhold"]
  }
}</pre></article>
    <article><h3>Jev output → tool result</h3><pre>{
  "answers": {
    "need_5": { "noul": 0.89 },
    "expected_5": { "noul": 0.94 },
    "disclosure_5": { "choice": "soft" }
  }
}

→ { "memories": [{
  "disclosure": "soft",
  "memory": "Prioritize low-fiber food…"
}] }</pre></article>
  </div>
  <div class="rule"><b>Fail-closed release rule:</b> need ≥ 55%, expected access ≥ 65%, and Jev must choose <code>full</code> or <code>soft</code>. A timeout, malformed response, or any error returns no memories.</div>
</section>
<style>
.protocol-docs{margin-top:54px;padding:28px;background:#fff;border:1px solid #d8d3c9;border-radius:20px}
.protocol-docs h2{font:700 36px/1.1 Georgia;margin:5px 0}.protocol-docs>p{max-width:820px;color:#59665e;font-size:19px}.config{margin:22px 0;padding:16px;border-radius:12px;background:#edf4ef}.config b{display:block;margin-bottom:8px}.protocol-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.protocol-grid article{border:1px solid #e1ded6;border-radius:13px;padding:16px}.protocol-grid h3{margin:0 0 9px;font-size:18px}.protocol-grid p{font-size:15px;color:#59665e}.protocol-docs pre{margin:0;overflow:auto;background:#17221c;color:#e2eee5;border-radius:10px;padding:13px;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}.rule{margin-top:16px;padding:15px 17px;background:#fff0bd;color:#57420a;border-radius:12px;font-size:17px}@media(max-width:700px){.protocol-grid{grid-template-columns:1fr}}
</style>
"""


@app.get("/", response_class=HTMLResponse)
def demo() -> str:
    return TERMINAL_HTML.replace("</main><style>", f"{PROTOCOL_DOCS}</main><style>", 1)


class QueryBody(BaseModel):
    agent_id: str
    request: str


@app.get("/api/audit")
def audit(limit: int = 100) -> dict:
    return store.audit(min(limit, 500))


@app.get("/api/facts")
def facts() -> list[dict]:
    return store.list_facts()


@app.get("/api/proposals")
def proposals(status: str = "pending") -> list[dict]:
    if status not in {"pending", "accepted", "rejected"}:
        raise HTTPException(400, "status must be pending, accepted, or rejected")
    return store.list_memory_proposals(status)


@app.post("/api/query")
async def run_query(body: QueryBody) -> dict:
    try:
        return await query(settings, store, body.agent_id, body.request, client="web-demo")
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "judge_mode": settings.judge_mode, "embedder": store.embedder.name, "sqlite_vec": store.vec_enabled}
