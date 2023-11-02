from road_segment_graph import read_csv_to_dataframe
from graph_functions import read_excel_to_dataframe, calculate_centrality, create_color_map
from download_and_cut_nvdb_data import gather_road_data, overlay_polygon_with_road_data
from road_id_graph import id_grouping, create_adjacency_list, create_objectid_dict, basemap_plot
from shapely import LineString, wkt, intersection
from shapely.ops import unary_union
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx

Trondheim = ["Nardo", "Elgeseter/Øya", "Åsveien", "Byåsen", "Singsaker", "Hallset", "Rosenborg", "Lademoen", "Lade", "Ila", "Midtbyen", "Blussuvoll", "Strindheim", "Eberg", "Charlottenlund", "Brundalen", "Åsvang", "Hoeggen", "Utleira", "Nidarvoll", "Sjetne", "Tonstad", "Breidablikk", "Romolslia", "Uglam", "Flatåsen", "Kolstad", "Stabbursmoen", "Åsheim"]
TrondheimNr = "5001"
colors = ['#ffd7cb', '#ffccbc', '#ffbda9', '#ff9d81', '#ff6c4d', '#ff3b24', '#ff0a0a']

stemmekretser = read_csv_to_dataframe("stemmekrets_csv.csv")
areas = list(stemmekretser.loc[stemmekretser["Stemmekretsnavn"].isin(Trondheim)].loc[stemmekretser["Kommunenummer"] == TrondheimNr]["posList"])
Trondheim = list(stemmekretser.loc[stemmekretser["Stemmekretsnavn"].isin(Trondheim)].loc[stemmekretser["Kommunenummer"] == TrondheimNr]["Stemmekretsnavn"])
"""print([len(i) for i in areas])
print(Trondheim)"""
polygon_areas = []
for area in areas:
    a = str(area).replace(" ", ",").split(",")
    a = [(x + " " + y) for x,y in zip(a[0::2], a[1::2])]
    a = ','.join(a)
    polygon_areas.append(wkt.loads("POLYGON(("+a+"))"))

#print(polygon_areas)
merged_area = unary_union(polygon_areas)

road_data = read_excel_to_dataframe(f"veg-test-{TrondheimNr}.xlsx")
road_data = overlay_polygon_with_road_data(road_data, merged_area, False, False)
  
road_data = id_grouping(road_data)
nodes = create_adjacency_list(road_data)
objektid = create_objectid_dict(road_data)
G = nx.Graph(nodes)
G = nx.relabel_nodes(G, objektid, copy=True)


#G.remove_edges_from(nx.selfloop_edges(G))
#G = remove_connecting_nodes(G)
G = calculate_centrality(G)
color_map, color_dict = create_color_map(G, colors)
basemap_plot(road_data, color_map, colors)
print(road_data.columns.values)