# ============================================================
#  MODULE  : Backend / Integration
#  MEMBER  : Diksha (Student ID: 24012030)
#  ROLE    : Integration, Testing & Documentation
#  METHOD  : Flask REST API — connects all modules
# ============================================================

import os
from flask import Flask, render_template, request, jsonify

# Dynamically calculate absolute directory handles
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)
G     = build_graph()
model = train_model()

# ── HELPERS ──────────────────────────────────────────────────

def fmt(m):
    m = int(m)
    return f"{m} min" if m < 60 else (f"{m//60} hr" if m%60==0 else f"{m//60} hr {m%60} min")

def arrival(hour, mins):
    t = datetime.now().replace(hour=hour, minute=0, second=0) + timedelta(minutes=int(mins))
    return t.strftime("%I:%M %p")

def status(d):
    return "ON TIME" if d < 10 else ("MINOR DELAY" if d < 30 else "MAJOR DELAY")

def best_hour(stops, dist):
    delays = {h: predict_delay(model, stops, dist, h) for h in range(24)}
    bh = min(delays, key=delays.get)
    return datetime.now().replace(hour=bh, minute=0).strftime("%I:%M %p"), round(delays[bh],1)

# ── PAGE ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", stations=sorted(G.nodes()),
                           total_stations=G.number_of_nodes(),
                           total_routes=G.number_of_edges())

# ── API ──────────────────────────────────────────────────────

@app.route("/api/find_route", methods=["POST"])
def find_route():
    d    = request.json
    path, total = get_shortest_path(G, d["source"], d["destination"], d["weight"])
    if not path: return jsonify({"error": "No route found"})

    rows, dist, time = [], 0, 0
    for i in range(len(path)-1):
        e = G[path[i]][path[i+1]]
        dist += e["distance"]; time += e["time"]
        rows.append({"step":i+1,"from":path[i],"to":path[i+1],
                     "distance":e["distance"],"time":e["time"]})

    hour    = int(d["hour"])
    delay   = predict_delay(model, len(path)-1, dist, hour)
    eta     = time + delay
    bh, bd  = best_hour(len(path)-1, dist)

    return jsonify({"path":" → ".join(path),"stops":len(path)-1,"rows":rows,
                    "total_dist":dist,"total_time":fmt(time),"delay":fmt(delay),
                    "final_eta":fmt(eta),"arrival":arrival(hour,eta),
                    "status":status(delay),"best_hour":bh,"best_delay":fmt(bd)})


@app.route("/api/alternate_routes", methods=["POST"])
def alternate_routes():
    d      = request.json
    routes = get_alternate_routes(G, d["source"], d["destination"])
    if not routes: return jsonify({"error": "No routes found"})
    hour   = int(d["hour"])
    result = []
    for i,(path,dist,time) in enumerate(routes):
        delay = predict_delay(model, len(path)-1, dist, hour)
        eta   = time + delay
        result.append({"rank":i+1,"path":" → ".join(path),"distance":dist,
                       "travel_time":fmt(time),"delay":fmt(delay),
                       "final_eta":fmt(eta),"arrival":arrival(hour,eta),
                       "status":status(delay)})
    return jsonify({"routes": result})


@app.route("/api/model_accuracy")
def model_accuracy():
    mae, r2 = get_model_metrics(model)
    labels  = {"stops":"Number of Stops","distance":"Distance (km)",
               "hour":"Departure Hour","day":"Day of Week",
               "is_monsoon":"Monsoon Season","is_holiday":"Holiday"}
    imp = sorted([{"factor":labels[k],"value":round(v*100,1)}
                  for k,v in get_feature_importance(model).items()],
                 key=lambda x: x["value"], reverse=True)
    return jsonify({"mae":mae,"r2":r2,"trees":100,"importance":imp})


@app.route("/api/network")
def network():
    return jsonify({
        "nodes": [{"id":n,"label":n} for n in G.nodes()],
        "edges": [{"from":u,"to":v,"distance":d["distance"],"time":d["time"]}
                  for u,v,d in G.edges(data=True)]
    })

if __name__ == "__main__":
    app.run(debug=True)
