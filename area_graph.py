from shapely import LineString, wkt, intersection
from road_segment_graph import read_csv_to_dataframe
from graph_functions import read_excel_to_dataframe, calculate_centrality, create_color_map
from download_and_cut_nvdb_data import gather_road_data, overlay_polygon_with_road_data
import networkx as nx
import matplotlib.pyplot as plt
import nvdbapiv3
import pandas as pd
import geopandas as gpd
import contextily as cx

Trondheim = ["Nardo", "Elgeseter/Øya", "Åsveien", "Byåsen", "Singsaker", "Hallset", "Rosenborg", "Lademoen", "Lade", "Ila", "Midtbyen", "Blussuvoll", "Strindheim", "Eberg", "Charlottenlund", "Brundalen", "Åsvang", "Hoeggen", "Utleira", "Nidarvoll", "Sjetne", "Tonstad", "Breidablikk", "Romolslia", "Uglam", "Flatåsen", "Kolstad", "Stabbursmoen", "Åsheim"]
TrondheimNr = "5001"

def find_connecting_areas(list_of_polygons):
    """
    Finds potential connected areas based on the coordinates of the areas. 
    """
    potential_connected_areas = []
    for i,v in enumerate(list_of_polygons):
        for j,w in enumerate(list_of_polygons):
            if i != j:
                if intersection(v, w):
                    potential_connected_areas.append(sorted([i,j]))
    return [list(t) for t in set(tuple(element) for element in potential_connected_areas)]

def unique_roads(road_dataframe, list_of_area_names, areas):
    """
    Takes a list of area names and returns a 2d list of unique road_ids in the same order as input list. 
    """
    print(len(list_of_area_names) == len(areas))
    ids = []
    for i,name in enumerate(list_of_area_names):
        print(name)
        dataframe = overlay_polygon_with_road_data(road_dataframe, areas[i], False, False)
        id_list = dataframe['referanse'].values.tolist()
        id_list = [a.split("-")[0] for a in id_list]
        ids.append(list(set(id_list)))
    return ids

def common_member(a,b):
    """
    https://www.geeksforgeeks.org/python-check-two-lists-least-one-element-common/
    """
    a_set = set(a)
    b_set = set(b)
    if a_set & b_set:
        #print(a_set & b_set)
        return True
    else:
        return False

def common_road_segments(ids_list, potential_connected_areas):
    connected_areas = potential_connected_areas.copy()
    for id_pair in potential_connected_areas:
        if not common_member(ids_list[id_pair[0]], ids_list[id_pair[1]]):
            connected_areas.remove(id_pair)
    return connected_areas

def create_graph(connected_areas, list_of_area_names):
    G = nx.Graph()
    G.add_nodes_from(list_of_area_names)
    for i in connected_areas:
        G.add_edge(list_of_area_names[i[0]],list_of_area_names[i[1]])
    return G

def basemap_area_plot(areas, list_of_area_names, color_map):
    print(color_map)
    df = pd.DataFrame({'Name': list_of_area_names, 'geometry': areas})
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=5973)
    ax = gdf.plot(alpha=0.5, edgecolor='k', color=color_map)
    cx.add_basemap(ax, crs=gdf.crs)#, source=cx.providers.Stamen.TonerLite, zoom=10)
    plt.show()

stemmekretser = read_csv_to_dataframe("stemmekrets_csv.csv")
areas = list(stemmekretser.loc[stemmekretser["Stemmekretsnavn"].isin(Trondheim)].loc[stemmekretser["Kommunenummer"] == TrondheimNr]["posList"])
Trondheim = list(stemmekretser.loc[stemmekretser["Stemmekretsnavn"].isin(Trondheim)].loc[stemmekretser["Kommunenummer"] == TrondheimNr]["Stemmekretsnavn"])
print([len(i) for i in areas])
print(Trondheim)
polygon_areas = []
for area in areas:
    a = str(area).replace(" ", ",").split(",")
    a = [(x + " " + y) for x,y in zip(a[0::2], a[1::2])]
    a = ','.join(a)
    polygon_areas.append(wkt.loads("POLYGON(("+a+"))"))
veg = read_excel_to_dataframe("veg-test-5001.xlsx")

#vegGDF = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )
#overlay_polygon_with_road_data(veg, polygon_areas[0])

potential_connected_areas = find_connecting_areas(polygon_areas)
print(potential_connected_areas)
ids_list = unique_roads(veg, Trondheim, polygon_areas)
connected_areas = common_road_segments(ids_list, potential_connected_areas)
G = create_graph(connected_areas, Trondheim)
G = calculate_centrality(G)
color_map = create_color_map(G)
basemap_area_plot(polygon_areas, Trondheim, color_map)
nx.draw(G, pos=nx.kamada_kawai_layout(G), with_labels=True, font_weight='bold', node_color=color_map)
plt.show()
