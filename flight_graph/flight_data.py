import polars as pl
import networkx as nx
import matplotlib.pyplot as plt
import scipy
import random

df = pl.read_csv('routes.csv', null_values=['\\N'])

source_airports = df.select(pl.col(" source airport").alias("airport")).unique()
destination_airports = df.select(pl.col(" destination airport").alias("airport")).unique()

unique_airports = pl.concat([source_airports, destination_airports]).unique()


if unique_airports.height > 1000:
    selected_airports = random.sample(unique_airports['airport'].to_list(), 1000)

    df_filtered = df.filter(
        (df[" source airport"].is_in(selected_airports)) &
        (df[" destination airport"].is_in(selected_airports))
    )
else:
    df_filtered = df

print("Czy chcesz wyświetlić wykres? Wpisz y, jesli tak")
response = input('Wpisz odpowiedź: ')

edges = df_filtered.select([" source airport", " destination airport"]).to_numpy()

G = nx.DiGraph()
G.add_edges_from(edges)

for edge in edges:
    G.add_edge(edge[0], edge[1], capacity=1)

if response == 'y':

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, font_weight="bold", edge_color="gray")
    plt.title("Airports Network Graph")
    plt.show()

print("Czy chcesz obliczyć najkrótszą ścieżkę i spawdzić czy graf jest eulerowski? Wpisz y, jesli tak")
response = input('Wpisz odpowiedź: ')

if response == 'y':
    airports = list(G.nodes)
    print("Dostępne lotniska:")
    for airport in airports:
        print(airport)

    start = input("Podaj kod początkowego lotniska: ")
    end = input("Podaj kod końcowego lotniska: ")
    try:
        shortest_path = nx.shortest_path(G, source=start, target=end)
        print(f"Najkrótsza ścieżka między {start} a {end}: {shortest_path}")
    except nx.NetworkXNoPath:
        print(f"Brak dostępnej ścieżki między {start} a {end}.")
    except nx.NodeNotFound as e:
        print(f"Lotnisko {e} nie zostało znalezione w grafie.")

    if nx.is_eulerian(G):
        print("Graf jest eulerowski. Wyznaczanie ścieżki eulerowskiej...")
        euler_path = list(nx.eulerian_circuit(G))
        print("Ścieżka eulerowska:")
        for u, v in euler_path:
            print(f"{u} -> {v}")
    else:
        print("Graf nie jest eulerowski.")

        largest_scc = max(nx.strongly_connected_components(G), key=len)
        subgraph = G.subgraph(largest_scc)

        if nx.is_eulerian(subgraph):
            print("Największy spójny podgraf jest eulerowski. Wyznaczanie ścieżki eulerowskiej...")
            euler_path = list(nx.eulerian_circuit(subgraph))
            print("Ścieżka eulerowska w podgrafie:")
            for u, v in euler_path:
                print(f"{u} -> {v}")
        else:
            print("Żaden podgraf nie jest eulerowski.")

print("Czy chcesz obliczyć przepływ? Wpisz y, jesli tak")
response = input('Wpisz odpowiedź: ')

if response == 'y':

    airports = list(G.nodes)
    print("Dostępne lotniska:")
    for airport in airports:
        print(airport)

    source = input("Podaj kod początkowego lotniska: ")
    sink = input("Podaj kod końcowego lotniska: ")

    try:
        flow_value, flow_dict = nx.maximum_flow(G, source, sink)
        print(f"Maksymalny przepływ między {source} a {sink} wynosi: {flow_value}")
        print("Przepływy na poszczególnych krawędziach:")
        for u, flows in flow_dict.items():
            for v, flow in flows.items():
                print(f"Przepływ z {u} do {v}: {flow}")
    except nx.NetworkXError as e:
        print(f"Wystąpił błąd: {e}")
    except nx.NodeNotFound as e:
        print(f"Lotnisko {e} nie zostało znalezione w grafie.")