import streamlit as st
import pandas as pd
import networkx as nx

from route_optimization import build_graph, get_shortest_path
from delay_prediction import train_model, predict_delay

st.set_page_config(page_title="Train Route Optimizer", page_icon="🚆", layout="wide")

st.markdown("""
<style>
    .big-title { font-size: 2.2rem; font-weight: 800; color: #1b4332; text-align: center; margin-bottom: 0.2rem; }
    .subtitle  { text-align: center; color: #555; margin-bottom: 2rem; font-size: 1rem; }
    .card      { background: #f0fdf4; border-left: 5px solid #2d6a4f; border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0; color: #1b4332; }
    .card *    { color: #1b4332 !important; }
    .card-warn { background: #fffbeb; border-left: 5px solid #f59e0b; border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0; color: #7c4a00; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🚆 Smart Train Route Optimizer</div>', unsafe_allow_html=True)

@st.cache_resource
def load_everything():
    G     = build_graph()
    model = train_model()
    return G, model

G, model = load_everything()
stations = sorted(list(G.nodes()))

def format_time(minutes):
    minutes = int(minutes)
    if minutes < 60:
        return f"{minutes} min"
    h = minutes // 60
    m = minutes % 60
    if m == 0:
        return f"{h} hr"
    return f"{h} hr {m} min"

page = st.sidebar.radio("📌 Go to", ["🏠 Home", "🗺️ Find Route", "📊 Network Map"])


if page == "🏠 Home":
    col1, col2, col3 = st.columns(3)
    col1.metric("🚉 Stations", f"{G.number_of_nodes()}")
    col2.metric("🛤️ Routes",   f"{G.number_of_edges()}")
    col3.metric("🤖 ML Model", "Random Forest")

    st.markdown("---")
    st.subheader("How does this work?")
    st.markdown("""
    1. You select a source and destination station
    2. Dijkstra's Algorithm finds the best route through the railway graph
    3. Random Forest ML predicts how much delay to expect
    4. Final ETA = Travel Time + Predicted Delay
    """)
    st.info("👈 Use the sidebar to navigate to **Find Route** and try it out!")


elif page == "🗺️ Find Route":
    st.subheader("🗺️ Find the Best Train Route")

    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("🟢 From", stations, index=stations.index("New Delhi") if "New Delhi" in stations else 0)
    with col2:
        remaining   = [s for s in stations if s != source]
        destination = st.selectbox("🔴 To", remaining)

    optimize_by = st.radio("Optimize by:", ["📏 Shortest Distance (km)", "⏱️ Fastest Time (min)"], horizontal=True)
    weight = "distance" if "Distance" in optimize_by else "time"
    hour   = st.slider("🕐 Departure Hour", 0, 23, 10)

    if st.button("🔍 Find Optimal Route", type="primary", use_container_width=True):
        path, total = get_shortest_path(G, source, destination, weight)

        if path is None:
            st.error("❌ No route found between these stations.")
        else:
            st.markdown(f"""
            <div class="card">
                <h4>✅ Route Found!</h4>
                <p><b>Path:</b> {"  →  ".join(path)}</p>
                <p><b>Total {("Distance" if weight=="distance" else "Time")}:</b>
                   {total} {"km" if weight=="distance" else "minutes"}</p>
                <p><b>Stops:</b> {len(path) - 1}</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("📋 Journey Breakdown")
            rows = []
            total_time = 0
            total_dist = 0
            for i in range(len(path) - 1):
                edge = G[path[i]][path[i+1]]
                total_dist += edge["distance"]
                total_time += edge["time"]
                rows.append({
                    "Step": i + 1,
                    "From": path[i],
                    "To":   path[i+1],
                    "Distance (km)": edge["distance"],
                    "Time (min)":    edge["time"]
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.subheader("⏱️ Delay Prediction & Final ETA")
            delay     = predict_delay(model, len(path) - 1, total_dist, hour)
            final_eta = total_time + delay

            c1, c2, c3 = st.columns(3)
            c1.metric("🕐 Base Travel Time", format_time(total_time))
            c2.metric("⚠️ Predicted Delay",  format_time(delay))
            c3.metric("🎯 Final ETA",         format_time(final_eta))

            if delay < 10:
                status = "🟢 Train is likely ON TIME"
            elif delay < 30:
                status = "🟡 Expect a minor delay"
            else:
                status = "🔴 Expect a significant delay — plan accordingly"

            st.markdown(f'<div class="card-warn"><b>Status:</b> {status}</div>', unsafe_allow_html=True)


elif page == "📊 Network Map":
    st.subheader("🗺️ Indian Railway Network — Interactive Map")
    st.caption("Drag stations around • Hover to see details • Scroll to zoom")

    import math

    # Fixed positions based on rough geography of India
    GEO_POS = {
        "Amritsar":       (150, 80),
        "Chandigarh":     (220, 130),
        "New Delhi":      (280, 200),
        "Jaipur":         (210, 290),
        "Jodhpur":        (130, 340),
        "Agra":           (340, 260),
        "Lucknow":        (430, 240),
        "Gwalior":        (320, 310),
        "Varanasi":       (510, 270),
        "Patna":          (580, 250),
        "Bhopal":         (330, 390),
        "Ahmedabad":      (170, 410),
        "Surat":          (190, 490),
        "Mumbai":         (190, 570),
        "Pune":           (220, 620),
        "Nagpur":         (390, 460),
        "Kolkata":        (650, 320),
        "Bhubaneswar":    (650, 430),
        "Hyderabad":      (390, 560),
        "Visakhapatnam":  (580, 510),
        "Bangalore":      (370, 660),
        "Chennai":        (490, 660),
    }

    nodes_js = ""
    for station, (x, y) in GEO_POS.items():
        nodes_js += f"""
        nodes.push({{
            id: '{station}',
            label: '{station}',
            x: {x * 1.8},
            y: {y * 1.6},
            fixed: false,
            physics: false
        }});"""

    edges_js = ""
    for u, v, d in G.edges(data=True):
        edges_js += f"""
        edges.push({{
            from: '{u}',
            to: '{v}',
            label: '{d["distance"]}km',
            title: '{u} → {v}<br>{d["distance"]} km · {d["time"]} min'
        }});"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet">
        <style>
            body {{ margin: 0; background: #0a0f1e; }}
            #network {{
                width: 100%;
                height: 580px;
                background: radial-gradient(ellipse at center, #0d1b2a 0%, #0a0f1e 100%);
                border-radius: 12px;
                border: 1px solid #1e3a5f;
            }}
            #stats {{
                display: flex;
                gap: 1rem;
                padding: 0.8rem 1rem;
                background: #0d1b2a;
                border-radius: 0 0 12px 12px;
                border: 1px solid #1e3a5f;
                border-top: none;
            }}
            .stat {{
                color: #52b788;
                font-family: monospace;
                font-size: 0.85rem;
            }}
            .stat span {{ color: #ffffff; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div id="network"></div>
        <div id="stats">
            <div class="stat">🚉 Stations: <span>{G.number_of_nodes()}</span></div>
            <div class="stat">🛤️ Routes: <span>{G.number_of_edges()}</span></div>
            <div class="stat">💡 Tip: <span>Hover over a route to see distance & time</span></div>
        </div>
        <script>
            var nodes = [];
            var edges = [];
            {nodes_js}
            {edges_js}

            var container = document.getElementById('network');
            var data = {{
                nodes: new vis.DataSet(nodes),
                edges: new vis.DataSet(edges)
            }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    size: 14,
                    color: {{
                        background: '#52b788',
                        border: '#95d5b2',
                        highlight: {{ background: '#ffd166', border: '#ffa500' }}
                    }},
                    font: {{
                        color: '#ffffff',
                        size: 11,
                        face: 'monospace',
                        strokeWidth: 3,
                        strokeColor: '#0a0f1e'
                    }},
                    borderWidth: 2,
                    shadow: {{ enabled: true, color: '#52b78860', size: 10 }}
                }},
                edges: {{
                    color: {{ color: '#1e6091', highlight: '#ffd166', hover: '#90e0ef' }},
                    width: 1.5,
                    font: {{
                        color: '#90e0ef',
                        size: 9,
                        face: 'monospace',
                        strokeWidth: 2,
                        strokeColor: '#0a0f1e',
                        align: 'middle'
                    }},
                    smooth: {{ type: 'curvedCW', roundness: 0.1 }},
                    shadow: true
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    zoomView: true,
                    dragView: true
                }},
                physics: {{ enabled: false }}
            }};
            new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """

    st.components.v1.html(html, height=650, scrolling=False)



