// ============================================================
//  FILE    : main.js
//  MEMBER  : Amit Pandey (Student ID: 240112243)
//  ROLE    : Frontend & User Interface Module
//  PURPOSE : Handles all page interactions and API calls
// ============================================================

let wt = 'distance', netLoaded = false, accLoaded = false;

// ── NAVIGATION ──────────────────────────────────────────────
function go(name, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('on'));
    document.querySelectorAll('.nb').forEach(b => b.classList.remove('on'));
    document.getElementById('p-' + name).classList.add('on');
    btn.classList.add('on');
    if (name === 'map' && !netLoaded) loadMap();
    if (name === 'acc' && !accLoaded) loadAcc();
}

function setWt(el, val) {
    document.querySelectorAll('.ropt').forEach(o => o.classList.remove('on'));
    el.classList.add('on'); wt = val;
}

function fmtH(h) {
    h = parseInt(h);
    return (h%12||12) + ':00 ' + (h>=12?'PM':'AM');
}

function upH(inp, disp) {
    document.getElementById(disp).textContent = fmtH(document.getElementById(inp).value);
}

function badge(s) {
    if (s==='ON TIME')     return '<span class="badge g">🟢 On Time</span>';
    if (s==='MINOR DELAY') return '<span class="badge y">🟡 Minor Delay</span>';
    return '<span class="badge r">🔴 Major Delay</span>';
}

async function api(url, body={}) {
    const opt = body.source ? {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)
    } : {};
    return (await fetch(url, opt)).json();
}

// ── FIND ROUTE ───────────────────────────────────────────────
async function findRoute() {
    const src = document.getElementById('fs').value;
    const dst = document.getElementById('fd').value;
    const hr  = document.getElementById('fh').value;
    const out = document.getElementById('fout');

    if (src===dst) { out.innerHTML='<div class="card" style="color:var(--red)">⚠️ Same source and destination.</div>'; return; }
    out.innerHTML = '<p class="loader">⏳ Finding route...</p>';

    const r = await api('/api/find_route', {source:src, destination:dst, weight:wt, hour:hr});
    if (r.error) { out.innerHTML=`<div class="card" style="color:var(--red)">❌ ${r.error}</div>`; return; }

    const pathHtml = r.path.split(' → ').map(s=>`<span>${s}</span>`).join(' → ');
    const tRows    = r.rows.map(x=>`<tr><td>${x.step}</td><td>${x.from}</td><td>${x.to}</td><td>${x.distance} km</td><td>${x.time} min</td></tr>`).join('');

    out.innerHTML = `
    <div class="card g">
        <div class="ctitle">✅ Route Found</div>
        <div class="path">${pathHtml}</div>
        <div class="slb">Journey Breakdown</div>
        <table><thead><tr><th>Step</th><th>From</th><th>To</th><th>Distance</th><th>Time</th></tr></thead><tbody>${tRows}</tbody></table>
        <div class="slb">ETA & Delay</div>
        <div class="metrics">
            <div class="met"><div class="mlbl">Base Time</div><div class="mval s">${r.total_time}</div></div>
            <div class="met"><div class="mlbl">Delay</div><div class="mval y s">${r.delay}</div></div>
            <div class="met"><div class="mlbl">Final ETA</div><div class="mval s">${r.final_eta}</div></div>
            <div class="met"><div class="mlbl">Arrives At</div><div class="mval s">${r.arrival}</div></div>
        </div>
        ${badge(r.status)}
        <div class="tip">💡 Best time to travel: <b>${r.best_hour}</b> — min delay of <b>${r.best_delay}</b></div>
    </div>`;
}

// ── ALTERNATE ROUTES ─────────────────────────────────────────
async function findAlt() {
    const src = document.getElementById('as').value;
    const dst = document.getElementById('ad').value;
    const hr  = document.getElementById('ah').value;
    const out = document.getElementById('aout');

    out.innerHTML = '<p class="loader">⏳ Finding alternate routes...</p>';
    const r = await api('/api/alternate_routes', {source:src, destination:dst, hour:hr});
    if (r.error) { out.innerHTML=`<div class="card" style="color:var(--red)">❌ ${r.error}</div>`; return; }

    out.innerHTML = r.routes.map((x,i) => `
    <div class="card ${i===0?'g':'b'}">
        <div class="rank ${i===0?'best':''}">${i===0?'🥇 Best Route':'🔵 Route '+(i+1)}</div>
        <div class="path">${x.path.split(' → ').map(s=>`<span>${s}</span>`).join(' → ')}</div>
        <div class="metrics">
            <div class="met"><div class="mlbl">Distance</div><div class="mval s">${x.distance} km</div></div>
            <div class="met"><div class="mlbl">Travel Time</div><div class="mval s">${x.travel_time}</div></div>
            <div class="met"><div class="mlbl">Delay</div><div class="mval y s">${x.delay}</div></div>
            <div class="met"><div class="mlbl">Arrives At</div><div class="mval s">${x.arrival}</div></div>
        </div>
        ${badge(x.status)}
    </div>`).join('');
}

// ── MODEL ACCURACY ────────────────────────────────────────────
async function loadAcc() {
    const r = await api('/api/model_accuracy');
    accLoaded = true;
    const bars = r.importance.map(x=>`
    <div class="brow">
        <div class="blbl">${x.factor}</div>
        <div class="btrk"><div class="bfil" style="width:${x.value*2.5}%"></div></div>
        <div class="bval">${x.value}%</div>
    </div>`).join('');

    document.getElementById('accout').innerHTML = `
    <div class="stats">
        <div class="stat"><div class="slbl">MAE</div><div class="sval">${r.mae}<span style="font-size:1rem;color:var(--muted)"> min</span></div></div>
        <div class="stat"><div class="slbl">R² Score</div><div class="sval">${r.r2}</div></div>
        <div class="stat"><div class="slbl">Decision Trees</div><div class="sval">${r.trees}</div></div>
    </div>
    <div class="card">
        <div class="ctitle">What Causes Delays the Most?</div>
        <p style="color:var(--muted);font-size:.79rem;margin-bottom:.9rem">Feature Importance — higher % = more impact on prediction</p>
        ${bars}
    </div>
    <div class="card" style="font-size:.83rem;color:var(--muted);line-height:1.9">
        <b style="color:var(--text)">How to read:</b><br>
        • <b style="color:var(--text)">MAE ${r.mae} min</b> — predictions are off by ${r.mae} minutes on average<br>
        • <b style="color:var(--text)">R² ${r.r2}</b> — model explains ${Math.round(r.r2*100)}% of delay patterns<br>
        • Closer R² is to 1.0 the better the model
    </div>`;
}

// ── NETWORK MAP ───────────────────────────────────────────────
async function loadMap() {
    const r = await api('/api/network');
    netLoaded = true;

    const GEO = {
        "Amritsar":[150,80],"Chandigarh":[220,130],"New Delhi":[280,200],
        "Jaipur":[210,290],"Jodhpur":[130,340],"Agra":[340,260],
        "Lucknow":[430,240],"Gwalior":[320,310],"Varanasi":[510,270],
        "Patna":[580,250],"Bhopal":[330,390],"Ahmedabad":[170,410],
        "Surat":[190,490],"Mumbai":[190,570],"Pune":[220,620],
        "Nagpur":[390,460],"Kolkata":[650,320],"Bhubaneswar":[650,430],
        "Hyderabad":[390,560],"Visakhapatnam":[580,510],
        "Bangalore":[370,660],"Chennai":[490,660]
    };

    const nodes = new vis.DataSet(r.nodes.map(n=>({
        id:n.id, label:n.label,
        x:(GEO[n.id]?.[0]??300)*1.8, y:(GEO[n.id]?.[1]??300)*1.6,
        fixed:false, physics:false
    })));

    const edges = new vis.DataSet(r.edges.map(e=>({
        from:e.from, to:e.to,
        label:e.distance+'km',
        title:`${e.from} → ${e.to} | ${e.distance} km · ${e.time} min`
    })));

    new vis.Network(document.getElementById('map'), {nodes,edges}, {
        nodes:{shape:'dot',size:14,
            color:{background:'#22c55e',border:'#86efac',highlight:{background:'#eab308',border:'#ffa500'}},
            font:{color:'#fff',size:11,face:'monospace',strokeWidth:3,strokeColor:'#050810'},
            borderWidth:2, shadow:{enabled:true,color:'#22c55e60',size:10}},
        edges:{color:{color:'#1e3a5f',highlight:'#eab308',hover:'#60a5fa'},width:1.5,
            font:{color:'#60a5fa',size:9,face:'monospace',strokeWidth:2,strokeColor:'#050810',align:'middle'},
            smooth:{type:'curvedCW',roundness:0.1},shadow:true},
        interaction:{hover:true,tooltipDelay:100,zoomView:true,dragView:true},
        physics:{enabled:false}
    });
}
