import networkx as nx
from download_and_cut_nvdb_data import overlay_polygon_with_road_data
from graph_functions import create_adjacency_list, read_csv_to_dataframe, read_excel_to_dataframe, remove_connecting_nodes
from graph_functions import remove_roundabouts, get_area_polygon, create_color_map, calculate_centrality
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
from shapely import wkt

def create_objectid_dict(road_dataframe):
    objektid = {}
    for ind in road_dataframe.index:
        objektid.update({ind : str(road_dataframe["referanse"][ind])})
    return objektid

if __name__ == "__main__":
    Område = "Midtbyen"
    Kommunenummer = 5001
    polygon_area = get_area_polygon(Område, Kommunenummer)
    road_data = read_excel_to_dataframe(f"veg-test-{Kommunenummer}.xlsx")
    road_data = overlay_polygon_with_road_data(road_data, polygon_area, False, False)
  
    road_data = remove_roundabouts(road_data)
    nodes = create_adjacency_list(road_data)
    objektid = create_objectid_dict(road_data)
    G = nx.Graph(nodes)
    G = nx.relabel_nodes(G, objektid, copy=True)
    """for i in G.nodes():
        print(i)
        print(G.edges(i))"""

    G.remove_edges_from(nx.selfloop_edges(G))
    G = remove_connecting_nodes(G)
    G = calculate_centrality(G)
    color_map = create_color_map(G)
    nx.draw(G, pos=nx.kamada_kawai_layout(G), with_labels=True, font_weight='bold', node_color=color_map)
    plt.show()

