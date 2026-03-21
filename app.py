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
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

    .about-hero {
        background: linear-gradient(135deg, #0f2027, #1b4332, #203a43);
        border-radius: 16px;
        padding: 3rem 2.5rem;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .about-hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        color: #ffffff;
        margin: 0 0 0.5rem 0;
        letter-spacing: -1px;
    }
    .about-hero p {
        font-family: 'DM Sans', sans-serif;
        color: #95d5b2;
        font-size: 1.05rem;
        font-weight: 300;
        margin: 0;
    }
    .section-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #2d6a4f;
        margin-bottom: 1rem;
    }
    .mission-box {
        background: #f8fffe;
        border: 1px solid #d8f3dc;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2.5rem;
        font-family: 'DM Sans', sans-serif;
        font-size: 1.05rem;
        color: #1b4332;
        line-height: 1.8;
        font-weight: 300;
    }
    .team-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.2rem;
        margin-bottom: 2.5rem;
    }
    .team-card {
        background: white;
        border: 1px solid #e8f5e9;
        border-radius: 12px;
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 2px 12px rgba(45,106,79,0.07);
        transition: transform 0.2s;
    }
    .team-avatar {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1b4332, #52b788);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }
    .team-name {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        color: #1b4332;
        margin: 0 0 0.2rem 0;
    }
    .team-role {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.78rem;
        color: #888;
        margin: 0 0 0.2rem 0;
        font-weight: 300;
    }
    .team-id {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        color: #2d6a4f;
        margin: 0;
        font-weight: 500;
    }
    .stack-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
    }
    .stack-pill {
        background: #1b4332;
        color: #95d5b2;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        letter-spacing: 0.5px;
    }
    .divider {
        border: none;
        border-top: 1px solid #e8f5e9;
        margin: 2rem 0;
    }
    </style>

    <div class="about-hero">
        <h1>The Illuminators</h1>
        <p>Smart Train Route Optimization &amp; Delay Prediction System &nbsp;·&nbsp; DAA Project 2025–26</p>
    </div>

    <div class="section-label">Our Mission</div>
    <div class="mission-box">
        Railway passengers deserve more than static timetables. We built a smart system that finds
        the <strong>fastest route</strong> between any two stations and predicts <strong>how late your train might be</strong>
        — so you can plan your journey with confidence, not guesswork.
    </div>

    <hr class="divider">

    <div class="section-label">The Team</div>
    <div class="team-grid">
        <div class="team-card">
            <div class="team-avatar">👨‍💻</div>
            <div>
                <p class="team-name">Abhay Singh</p>
                <p class="team-role">Team Lead · ML & Dataset</p>
                <p class="team-id">ID: 240111781</p>
            </div>
        </div>
        <div class="team-card">
            <div class="team-avatar">🗺️</div>
            <div>
                <p class="team-name">Anuj Rawat</p>
                <p class="team-role">Route Optimization</p>
                <p class="team-id">ID: 24011939</p>
            </div>
        </div>
        <div class="team-card">
            <div class="team-avatar">🎨</div>
            <div>
                <p class="team-name">Amit Pandey</p>
                <p class="team-role">Frontend & UI</p>
                <p class="team-id">ID: 240112243</p>
            </div>
        </div>
        <div class="team-card">
            <div class="team-avatar">🔗</div>
            <div>
                <p class="team-name">Diksha</p>
                <p class="team-role">Integration & Testing</p>
                <p class="team-id">ID: 24012030</p>
            </div>
        </div>
    </div>

    <hr class="divider">

    <div class="section-label">Built With</div>
    <div class="stack-row">
        <span class="stack-pill">Python</span>
        <span class="stack-pill">Streamlit</span>
        <span class="stack-pill">NetworkX</span>
        <span class="stack-pill">Scikit-learn</span>
        <span class="stack-pill">Pandas</span>
        <span class="stack-pill">Matplotlib</span>
    </div>
    """, unsafe_allow_html=True)