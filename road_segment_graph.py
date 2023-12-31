import networkx as nx
from download_and_cut_nvdb_data import overlay_polygon_with_road_data
from graph_functions import create_adjacency_list, read_csv_to_dataframe, read_excel_to_dataframe, remove_connecting_nodes
from graph_functions import remove_roundabouts, get_area_polygon, create_color_map, calculate_centrality, basemap_plot
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

def color_nodes_without_color(road_dataframe, G):
    print("rrrr")
    while None in road_dataframe['color'].values.tolist():
        empty_df = road_dataframe.loc[road_dataframe['color'].isnull()]
        color_df = road_dataframe.loc[road_dataframe['color'].notnull()]
        print(empty_df.size, color_df.size)
        for ind in empty_df.index:
            #print(empty_df['referanse'][ind])
            edge_list = list(G[empty_df['referanse'][ind]].keys())
            print(len(edge_list))
            if edge_list:
                for node in edge_list:
                    if node in color_df['referanse'].values.tolist():
                        #print(node)
                        row_from = color_df.loc[color_df['referanse'] == node].index[0]
                        road_dataframe['color'][ind] = road_dataframe['color'][row_from]
                        break
            else:
                road_dataframe['color'][ind] = '#377eb8'
    color_map = []
    for node in G:
        color_map.append(road_dataframe['color'].loc[road_dataframe['referanse'] == node].tolist()[0])
    return road_dataframe, color_map

if __name__ == "__main__":
    colors = ['#377eb8', '#feb24c', '#e41a1c']
    Område = "Utleira"
    Kommunenummer = 5001
    polygon_area = get_area_polygon(Område, Kommunenummer)
    road_data = read_excel_to_dataframe(f"veg-test-{Kommunenummer}.xlsx")
    road_data = overlay_polygon_with_road_data(road_data, polygon_area, True, False)
  
    #road_data = remove_roundabouts(road_data)
    print(road_data)
    nodes = create_adjacency_list(road_data)
    objektid = create_objectid_dict(road_data)
    G = nx.DiGraph(nodes)
    G = nx.relabel_nodes(G, objektid, copy=True)
    """for i in G.nodes():
        print(i)
        print(G.edges(i))"""

    G.remove_edges_from(nx.selfloop_edges(G))
    G_conpact = remove_connecting_nodes(G.copy())
    G_conpact, bc = calculate_centrality(G_conpact)
    color_map, color_dict, labels = create_color_map(G_conpact, colors)
    road_data['color'] = road_data['referanse'].apply(lambda x: color_dict.get(x, None))
    road_data, color_map = color_nodes_without_color(road_data, G)
    basemap_plot(road_data, color_map, colors, bc, labels)
    """nx.draw(G, pos=nx.kamada_kawai_layout(G), with_labels=True, font_weight='bold', node_color=color_map)
    plt.show()"""


