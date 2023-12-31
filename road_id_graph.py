from graph_functions import calculate_centrality, create_color_map, get_area_polygon, basemap_plot
from graph_functions import read_csv_to_dataframe, read_excel_to_dataframe, remove_connecting_nodes, remove_roundabouts
from download_and_cut_nvdb_data import overlay_polygon_with_road_data
import networkx as nx
import matplotlib.pyplot as plt
from shapely.ops import linemerge
from shapely import wkt
import geopandas as gpd
import contextily as cx

def create_objectid_dict(road_dataframe):
    objektid = {}
    for ind in road_dataframe.index:
        objektid.update({ind : str(road_dataframe["referanse"][ind])})
    return objektid

def create_adjacency_list(road_dataframe):
    """
    Takes a dataframe of road segments and returns a dictionary of adjacency list graph representation.
    """
    adjacency_list = {}

    for ind in road_dataframe.index:
        adjacents = []
        for node in road_dataframe['noder'][ind]:
            adj_noder = road_dataframe.loc[road_dataframe['noder'].apply(lambda x: node in x)]
            adjacents += adj_noder['referanse'].values.tolist()
        adjacents = list(set(adjacents))
        try:
            adjacents.remove(road_dataframe['referanse'][ind])
        except:
            pass

        adjacency_list.update({road_dataframe['referanse'][ind] : adjacents})

    return adjacency_list

def id_grouping(road_dataframe):
    agg_functions = {
        'startnode': ', '.join,
        'sluttnode': ', '.join,
        'geometry': '- '.join,
        'vegkategori': max#lambda x: x.value_counts().index[0]
    }
    #print(road_dataframe.columns.values)

    group = {}
    road_dataframe['referanse'] = road_dataframe['referanse'].apply(lambda x: x.split('-')[0])
    #road_dataframe['startnode'] = road_dataframe['startnode'].apply(lambda x: x.split('-')[0])
    #road_dataframe['sluttnode'] = road_dataframe['sluttnode'].apply(lambda x: x.split('-')[0])
    print(road_dataframe.columns.values.tolist())
    road_dataframe = road_dataframe[['referanse', 'startnode', 'sluttnode', 'vegkategori', 'geometry']].groupby('referanse').agg(agg_functions).reset_index()
    road_dataframe['geometry'] = road_dataframe['geometry'].apply(lambda x: linemerge([wkt.loads(y) for y in x.split('- ')]))
    road_dataframe['noder'] = road_dataframe['startnode'] + ', ' + road_dataframe['sluttnode']
    road_dataframe['noder'] = road_dataframe['noder'].apply(lambda x: list(set(x.split(', '))))
    print(road_dataframe.columns.values)

    return road_dataframe

def main():
    colors = ['#377eb8', '#feb24c', '#e41a1c']
    Område = "Midtbyen"
    Kommunenummer = 5001
    polygon_area = get_area_polygon(Område, Kommunenummer)
    road_data = read_excel_to_dataframe(f"veg-test-{Kommunenummer}.xlsx")
    road_data = overlay_polygon_with_road_data(road_data, polygon_area, True, False)
  
    road_data = id_grouping(road_data)
    #create_adjacency_list(road_data)
    #road_data = remove_roundabouts(road_data)
    nodes = create_adjacency_list(road_data)
    objektid = create_objectid_dict(road_data)
    G = nx.Graph(nodes)
    G = nx.relabel_nodes(G, objektid, copy=True)
    

    #G.remove_edges_from(nx.selfloop_edges(G))
    #G = remove_connecting_nodes(G)
    G, bc = calculate_centrality(G)
    color_map, color_dict, labels = create_color_map(G, colors)
    gdf = basemap_plot(road_data, color_map, colors, bc, labels)
    print(road_data.columns.values)
    """nx.draw(G, pos=nx.kamada_kawai_layout(G), with_labels=True, font_weight='bold', node_color=color_map)
    plt.show()"""
    return gdf

main()