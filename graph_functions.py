import pandas as pd
from shapely import wkt
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.gridspec
import contextily as cx
from collections import Counter

def create_adjacency_list(road_dataframe):
    """
    Takes a dataframe of road segments and returns a dictionary of adjacency list graph representation.
    """
    adjacency_list = {}

    for ind in road_dataframe.index:
        #Try directed graph by checking the lanes and then instead of the line under only check if 
        if road_dataframe['feltoversikt'][ind] == "1":
            adj_noder = road_dataframe.loc[((road_dataframe['startnode'] == road_dataframe['sluttnode'][ind]) & (road_dataframe['feltoversikt'] != "2") | (road_dataframe['sluttnode'] == road_dataframe['sluttnode'][ind]) & (road_dataframe['feltoversikt'] != "1"))]
        elif road_dataframe['feltoversikt'][ind] == "2":
            adj_noder = road_dataframe.loc[((road_dataframe['startnode'] == road_dataframe['startnode'][ind]) & (road_dataframe['feltoversikt'] != "2") | (road_dataframe['sluttnode'] == road_dataframe['startnode'][ind]) & (road_dataframe['feltoversikt'] != "1"))]
        else:
            adj_noder = road_dataframe.loc[((road_dataframe['startnode'] == road_dataframe['startnode'][ind]) & (road_dataframe['feltoversikt'] != "1") | (road_dataframe['sluttnode'] == road_dataframe['startnode'][ind]) & (road_dataframe['feltoversikt'] != "1") | (road_dataframe['startnode'] == road_dataframe['sluttnode'][ind]) & (road_dataframe['feltoversikt'] != "2") | (road_dataframe['sluttnode'] == road_dataframe['sluttnode'][ind]) & (road_dataframe['feltoversikt'] != "2"))]
        node_list = adj_noder.index.tolist()
        try:
            node_list.remove(ind)
        except:
            pass

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

def create_color_map(G, colors):
    color_map = []
    color_dict = {}
    for node in G:
        if G.nodes[node]["cent_betweenness"] < 0.1:
            color_map.append(colors[0])
            color_dict.update({node : colors[0]})
        elif G.nodes[node]["cent_betweenness"] < 0.2:
            color_map.append(colors[1])
            color_dict.update({node : colors[1]})
        elif G.nodes[node]["cent_betweenness"] < 0.3:
            color_map.append(colors[2])
            color_dict.update({node : colors[2]})
        elif G.nodes[node]["cent_betweenness"] < 0.4:
            color_map.append(colors[3])
            color_dict.update({node : colors[3]})
        elif G.nodes[node]["cent_betweenness"] < 0.5:
            color_map.append(colors[4])
            color_dict.update({node : colors[4]})
        elif G.nodes[node]["cent_betweenness"] < 0.7:
            color_map.append(colors[5])
            color_dict.update({node : colors[5]})
        else:
            color_map.append(colors[6])
            color_dict.update({node : colors[6]})
    return color_map, color_dict

def calculate_centrality(G):
    bc = nx.betweenness_centrality(G)
    nx.set_node_attributes(G, bc, "cent_betweenness")
    return G

def basemap_plot(road_dataframe, color_map, colors):
    fig = plt.figure()
    grid = matplotlib.gridspec.GridSpec(3,4, hspace=0.2, wspace=0.2)
    left = fig.add_subplot(grid[:,:-2])
    topright = fig.add_subplot(grid[:-2,2:])
    middleright = fig.add_subplot(grid[1:-1,2:])
    bottomright = fig.add_subplot(grid[2:,2:])
    
    try:
        road_dataframe['geometry'] = road_dataframe['geometry'].apply(lambda x: wkt.loads(x))
    except:
        pass
    gdf = gpd.GeoDataFrame(road_dataframe, geometry='geometry', crs=5973)
    gdf.plot(ax=left, alpha=0.5, edgecolor='k', color=color_map, linewidth=3)
    #cx.add_basemap(left, crs=gdf.crs)#, source=cx.providers.CartoDB.Positron)#, source=cx.providers.Stamen.Toner)

    centrality_plot_data = Counter(color_map)
    print(road_dataframe.shape, len(color_map))
    try:
        centrality_plot_data["0-0.1"] = centrality_plot_data[colors[0]]
        centrality_plot_data["0.1-0.2"] = centrality_plot_data[colors[1]]
        centrality_plot_data["0.2-0.3"] = centrality_plot_data[colors[2]]
        centrality_plot_data["0.3-0.4"] = centrality_plot_data[colors[3]]
        centrality_plot_data["0.4-0.5"] = centrality_plot_data[colors[4]]
        centrality_plot_data["0.5-0.6"] = centrality_plot_data[colors[5]]
        centrality_plot_data["0.6-0.7"] = centrality_plot_data[colors[6]]
        centrality_plot_data["0.7-1"] = centrality_plot_data[colors[7]]
    except:
        pass
    try:
        for i in colors:
            del centrality_plot_data[i]
    except:
        pass
    print(centrality_plot_data)
    topright.bar(centrality_plot_data.keys(), centrality_plot_data.values())

    road_dataframe['geometry_length'] = road_dataframe['geometry'].apply(lambda x: x.length)
    print(max(road_dataframe['geometry_length'].values.tolist()))
    ranges = [(0,10), (10,20), (20,30), (30,40), (40,50), (50,60), (60,70), (80,2000)]
    length_range_data = {r: 0 for r in ranges}
    for length in road_dataframe['geometry_length'].values:
        for r in ranges:
            if r[0] <= length < r[1]:
                length_range_data[r] += 1
    #print(length_range_data)
    middleright.bar({str(key)[1:-1]: value for key,value in length_range_data.items()}.keys(), length_range_data.values())

    scatter_betweenness_data = []
    for i in color_map:
        if i == colors[0]:
            scatter_betweenness_data.append(0.1)
        elif i == colors[1]:
            scatter_betweenness_data.append(0.2)
        elif i == colors[2]:
            scatter_betweenness_data.append(0.3)
        elif i == colors[3]:
            scatter_betweenness_data.append(0.4)
        elif i == colors[4]:
            scatter_betweenness_data.append(0.5)
        elif i == colors[5]:
            scatter_betweenness_data.append(0.6)
        elif i == colors[6]:
            scatter_betweenness_data.append(0.7)
        else:
            scatter_betweenness_data.append(0.8)
    bottomright.scatter(road_dataframe['geometry_length'].values.tolist(), scatter_betweenness_data)
    plt.show()
