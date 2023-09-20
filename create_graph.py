import networkx as nx
from download_nvdb_data import gather_road_data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_adjacency_list(road_dataframe):
    """
    Takes a dataframe of road segments and returns a dictionary of adjacency list graph representation.
    """
    adjacency_list = {}

    for ind in road_dataframe.index:

        adj_noder = road_dataframe.loc[((road_dataframe['startnode'] == road_dataframe['startnode'][ind]) | (road_dataframe['sluttnode'] == road_dataframe['startnode'][ind]) | (road_dataframe['startnode'] == road_dataframe['sluttnode'][ind]) | (road_dataframe['sluttnode'] == road_dataframe['sluttnode'][ind]))]
        node_list = adj_noder.index.tolist()
        node_list.remove(ind)

        adjacency_list.update({ind : node_list})

        """if ind == 5:
            break"""

    return adjacency_list

def remove_connecting_nodes(G, threshold=2):
    """
    Removes nodes in a graph G which only has two edges.
    Also removes isolated nodes. 
    """
    for node in list(G.nodes()):
        if G.degree(node) == threshold:
            edges = list(G.edges(node))
            G.add_edge(edges[0][1], edges[1][1])
            G.remove_node(node)
        elif G.degree(node) == 0:
            G.remove_node(node)
    return G

road_data = gather_road_data()
nodes = create_adjacency_list(road_data)
G = nx.Graph(nodes)
"""for i in G.nodes():
    print(i)
    print(G.edges(i))"""

G = remove_connecting_nodes(G)
bc = nx.betweenness_centrality(G)
nx.set_node_attributes(G, bc, "cent_betweenness")
color_map = []
for node in G:
    if G.nodes[node]["cent_betweenness"] < 0.2:
        color_map.append('blue')
    elif G.nodes[node]["cent_betweenness"] < 0.5:
        color_map.append('yellow')
    else:
        color_map.append('red')

nx.draw(G, pos=nx.kamada_kawai_layout(G), with_labels=True, font_weight='bold', node_color=color_map)
plt.show()

