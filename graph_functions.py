import pandas as pd
from shapely import wkt
import networkx as nx

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

def read_excel_to_dataframe(file):
    """
    Reads and returns a excel file as a dataframe. 
    """
    return pd.read_excel(file)

def get_area_polygon(area_name, kommunenummer):
    stemmekretser = read_csv_to_dataframe("stemmekrets_csv.csv")
    areas = list(stemmekretser.loc[stemmekretser['Stemmekretsnavn'] == area_name].loc[stemmekretser['Kommunenummer'] == str(kommunenummer)]['posList'])
    polygon_areas = []
    for area in areas:
        a = str(area).replace(" ", ",").split(",")
        a = [(x + " " + y) for x,y in zip(a[0::2], a[1::2])]
        a = ','.join(a)
        polygon_areas.append(wkt.loads("POLYGON(("+a+"))"))
    return polygon_areas[0]

def create_color_map(G):
    color_map = []
    for node in G:
        if G.nodes[node]["cent_betweenness"] < 0.1:
            color_map.append('#ffd7cb')
        elif G.nodes[node]["cent_betweenness"] < 0.2:
            color_map.append('#ffccbc')
        elif G.nodes[node]["cent_betweenness"] < 0.3:
            color_map.append('#ffbda9')
        elif G.nodes[node]["cent_betweenness"] < 0.4:
            color_map.append('#ff9d81')
        elif G.nodes[node]["cent_betweenness"] < 0.5:
            color_map.append('#ff6c4d')
        elif G.nodes[node]["cent_betweenness"] < 0.7:
            color_map.append('#ff3b24')
        else:
            color_map.append('#ff0a0a')
    return color_map

def calculate_centrality(G):
    bc = nx.betweenness_centrality(G)
    nx.set_node_attributes(G, bc, "cent_betweenness")
    return G