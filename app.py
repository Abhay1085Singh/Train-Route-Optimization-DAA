import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from route_optimization import build_graph, get_shortest_path
from delay_prediction import train_model, predict_delay

st.set_page_config(page_title="Train Route Optimizer", page_icon="🚆", layout="wide")

st.markdown("""
<style>
    .big-title { font-size: 2.2rem; font-weight: 800; color: #1b4332; text-align: center; margin-bottom: 0.2rem; }
    .subtitle  { text-align: center; color: #555; margin-bottom: 2rem; font-size: 1rem; }
    .card      { background: #f0fdf4; border-left: 5px solid #2d6a4f; border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0; }
    .card-warn { background: #fffbeb; border-left: 5px solid #f59e0b; border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🚆 Smart Train Route Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Team: The Illuminators &nbsp;|&nbsp; DAA Project 2025-26 &nbsp;|&nbsp; Dijkstra\'s Algorithm + Random Forest ML</div>', unsafe_allow_html=True)

@st.cache_resource
def load_everything():
    G     = build_graph()
    model = train_model()
    return G, model

G, model = load_everything()
stations = sorted(list(G.nodes()))

page = st.sidebar.radio("📌 Go to", ["🏠 Home", "🗺️ Find Route", "📊 Network Map", "ℹ️ About"])


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
            c1.metric("🕐 Base Travel Time", f"{total_time} min")
            c2.metric("⚠️ Predicted Delay",  f"{delay} min")
            c3.metric("🎯 Final ETA",         f"{final_eta} min")

            if delay < 10:
                status = "🟢 Train is likely ON TIME"
            elif delay < 30:
                status = "🟡 Expect a minor delay"
            else:
                status = "🔴 Expect a significant delay — plan accordingly"

            st.markdown(f'<div class="card-warn"><b>Status:</b> {status}</div>', unsafe_allow_html=True)


elif page == "📊 Network Map":
    st.subheader("📊 Indian Railway Network Graph")

    fig, ax = plt.subplots(figsize=(14, 9))
    pos = nx.spring_layout(G, seed=42, k=2.5)

    nx.draw_networkx_nodes(G, pos, node_color="#2d6a4f", node_size=600, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=7, font_color="white", font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="#95d5b2", width=1.8, ax=ax)

    edge_labels = {(u, v): f"{d['distance']}km" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)

    ax.set_title("Railway Network — Stations & Routes", fontsize=15, fontweight="bold", pad=20)
    ax.axis("off")
    st.pyplot(fig)
    st.info(f"Total: **{G.number_of_nodes()} stations** and **{G.number_of_edges()} routes**")


elif page == "ℹ️ About":
    st.subheader("ℹ️ About This Project")
    st.markdown("""
    ### 🎯 Problem We Are Solving
    Existing railway apps only show static timetables. They don't find the smartest route or predict delays.
    Our system does both — using Dijkstra's Algorithm and Random Forest ML.

    ---
    ### 👨‍💻 Team — The Illuminators

    | Member | ID | Role |
    |--------|----|------|
    | Abhay Singh (Lead) | 240111781 | ML & Dataset |
    | Anuj Rawat | 24011939 | Route Optimization (DAA) |
    | Amit Pandey | 240112243 | Frontend & UI |
    | Diksha | 24012030 | Integration & Testing |

    ---
    ### 🧠 Algorithms Used

    **Dijkstra's Algorithm**
    - Finds shortest path in a weighted graph
    - Time Complexity: O((V + E) log V)
    - Stations = nodes, Routes = edges with distance/time weights

    **Random Forest Regression**
    - 100 decision trees working together
    - Predicts delay based on: stops, distance, hour, day, monsoon, holiday

    ---
    ### 🛠️ Tech Stack
    Python · NetworkX · Scikit-learn · Pandas · Streamlit · Matplotlib
    """)
