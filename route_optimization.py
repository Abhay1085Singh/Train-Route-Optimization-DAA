# ============================================================
#  MODULE  : Route Optimization
#  MEMBER  : Anuj Rawat (Student ID: 24011939)
#  ROLE    : Route Optimization — DAA Module
#  METHOD  : Dijkstra's Algorithm using NetworkX + Manual
# ============================================================

import networkx as nx
import heapq

ROUTES = [
    ("New Delhi","Agra",200,120),       ("New Delhi","Jaipur",280,270),
    ("New Delhi","Chandigarh",250,210), ("New Delhi","Lucknow",510,360),
    ("New Delhi","Amritsar",450,390),   ("Agra","Lucknow",336,240),
    ("Agra","Jaipur",240,200),          ("Agra","Gwalior",120,90),
    ("Gwalior","Bhopal",420,300),       ("Bhopal","Nagpur",350,270),
    ("Nagpur","Hyderabad",500,380),     ("Hyderabad","Bangalore",570,600),
    ("Bangalore","Chennai",360,330),    ("Chennai","Mumbai",1330,960),
    ("Mumbai","Pune",150,180),          ("Mumbai","Surat",265,195),
    ("Surat","Ahmedabad",265,195),      ("Ahmedabad","Jaipur",660,480),
    ("Jaipur","Jodhpur",330,270),       ("Lucknow","Varanasi",300,210),
    ("Varanasi","Patna",250,180),       ("Patna","Kolkata",500,480),
    ("Kolkata","Bhubaneswar",440,420),  ("Bhubaneswar","Visakhapatnam",440,420),
    ("Visakhapatnam","Chennai",800,660),("Chandigarh","Amritsar",230,180),
    ("Pune","Hyderabad",560,540),       ("Nagpur","Kolkata",1100,900),
]

def build_graph():
    G = nx.Graph()
    for s, d, dist, t in ROUTES:
        G.add_edge(s, d, distance=dist, time=t)
    return G

def get_shortest_path(G, src, dst, weight="distance"):
    try:
        return nx.dijkstra_path(G, src, dst, weight=weight), \
               nx.dijkstra_path_length(G, src, dst, weight=weight)
    except:
        return None, None

def dijkstra_manual(G, src, dst, weight="distance"):
    visited, cost, prev, pq = set(), {src:0}, {src:None}, [(0,src)]
    while pq:
        cc, cn = heapq.heappop(pq)
        if cn in visited: continue
        visited.add(cn)
        if cn == dst: break
        for nb in G.neighbors(cn):
            nc = cc + G[cn][nb][weight]
            if nc < cost.get(nb, float('inf')):
                cost[nb] = nc; prev[nb] = cn
                heapq.heappush(pq, (nc, nb))
    path, node = [], dst
    while node: path.append(node); node = prev.get(node)
    path.reverse()
    return (path, cost.get(dst)) if path and path[0]==src else (None, None)

def get_alternate_routes(G, src, dst, k=3):
    try:
        paths = list(nx.shortest_simple_paths(G, src, dst, weight="distance"))
        return [(p,
                 sum(G[p[i]][p[i+1]]["distance"] for i in range(len(p)-1)),
                 sum(G[p[i]][p[i+1]]["time"]     for i in range(len(p)-1)))
                for p in paths[:k]]
    except:
        return []
