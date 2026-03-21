import networkx as nx

ROUTES = [
    ("New Delhi",    "Agra",            200,  120),
    ("New Delhi",    "Jaipur",          280,  270),
    ("New Delhi",    "Chandigarh",      250,  210),
    ("New Delhi",    "Lucknow",         510,  360),
    ("New Delhi",    "Amritsar",        450,  390),
    ("Agra",         "Lucknow",         336,  240),
    ("Agra",         "Jaipur",          240,  200),
    ("Agra",         "Gwalior",         120,   90),
    ("Gwalior",      "Bhopal",          420,  300),
    ("Bhopal",       "Nagpur",          350,  270),
    ("Nagpur",       "Hyderabad",       500,  380),
    ("Hyderabad",    "Bangalore",       570,  600),
    ("Bangalore",    "Chennai",         360,  330),
    ("Chennai",      "Mumbai",         1330,  960),
    ("Mumbai",       "Pune",            150,  180),
    ("Mumbai",       "Surat",           265,  195),
    ("Surat",        "Ahmedabad",       265,  195),
    ("Ahmedabad",    "Jaipur",          660,  480),
    ("Jaipur",       "Jodhpur",         330,  270),
    ("Lucknow",      "Varanasi",        300,  210),
    ("Varanasi",     "Patna",           250,  180),
    ("Patna",        "Kolkata",         500,  480),
    ("Kolkata",      "Bhubaneswar",     440,  420),
    ("Bhubaneswar",  "Visakhapatnam",   440,  420),
    ("Visakhapatnam","Chennai",         800,  660),
    ("Chandigarh",   "Amritsar",        230,  180),
    ("Pune",         "Hyderabad",       560,  540),
    ("Nagpur",       "Kolkata",        1100,  900),
]


def build_graph():
    G = nx.Graph()
    for source, destination, distance, time in ROUTES:
        G.add_edge(source, destination, distance=distance, time=time)
    return G


def get_shortest_path(G, source, destination, weight="distance"):
    try:
        path  = nx.dijkstra_path(G, source, destination, weight=weight)
        total = nx.dijkstra_path_length(G, source, destination, weight=weight)
        return path, total
    except:
        return None, None
