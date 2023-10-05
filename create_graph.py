import networkx as nx
from download_nvdb_data import gather_road_data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools

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

def create_objektid_dict(road_dataframe):
    objektid = {}
    for ind in road_dataframe.index:
        objektid.update({ind : str(road_dataframe["referanse"][ind])})
    return objektid

def remove_connecting_nodes(G, threshold=2):
    """
    Removes nodes in a graph G which only has two edges.
    Also removes isolated nodes. 
    """
    for node in list(G.nodes()):
        try:
            if G.degree(node) == threshold:
                edges = list(G.edges(node))
                G.add_edge(edges[0][1], edges[1][1])
                G.remove_node(node)
            elif G.degree(node) == 0:
                G.remove_node(node)
        except:
            pass
    return G

def remove_roundabouts(dataframe):
    """
    Removes roundabouts by artificially connecting all arms of the roundabout to eachother. 
    As a result it should work like a normal intersection. 
    """
    updated_dataframe = dataframe[dataframe["typeVeg"] != "Rundkjøring"]
    roundabouts = dataframe[dataframe["typeVeg"] == "Rundkjøring"]
    temp = roundabouts[["gate", "startnode", "sluttnode"]]
    print(temp.columns)
    temp["gate"] = temp["gate"].astype(str)
    unique_groups = temp["gate"].unique()
    g = temp.groupby(["gate"])
    for group in unique_groups:
        roundabout = g.get_group(group)
        print(roundabout)
        nodes = set(list(roundabout["startnode"]) + list(roundabout["sluttnode"]))
        relevant_nodes = []
        for node in nodes:
            if node in set(updated_dataframe["startnode"]) or node in set(updated_dataframe["sluttnode"]):
                relevant_nodes.append(node)
        print(relevant_nodes)
        for node in relevant_nodes:
            updated_dataframe = updated_dataframe.replace(node, relevant_nodes[0])
    return updated_dataframe

def read_csv_to_dataframe(file):
    """
    Reads and returns a csv file as a dataframe. 
    """
    return pd.read_csv(file)

if __name__ == "__main__":
    stemmekretser = read_csv_to_dataframe("stemmekrets_csv.csv")
    area = list(stemmekretser.loc[stemmekretser['Stemmekretsnavn'] == 'Eberg'].loc[stemmekretser['Kommunenummer'] == "5001"]['posList'])
    print(len(area[0]))
    road_data = gather_road_data(area, False, False)
    road_data = remove_roundabouts(road_data)
    nodes = create_adjacency_list(road_data)
    objektid = create_objektid_dict(road_data)
    G = nx.Graph(nodes)
    G = nx.relabel_nodes(G, objektid, copy=True)
    """for i in G.nodes():
        print(i)
        print(G.edges(i))"""

    G.remove_edges_from(nx.selfloop_edges(G))
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

