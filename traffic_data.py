from graph_functions import read_excel_to_dataframe
from road_segment_graph import read_csv_to_dataframe
from download_traffic_data import overlay_polygon_with_traffic
from shapely import LineString, wkt
from shapely.ops import unary_union
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.gridspec
import contextily as cx
import math

Trondheim = ["Nardo", "Elgeseter/Øya", "Åsveien", "Byåsen", "Singsaker", "Hallset", "Rosenborg", "Lademoen", "Lade", "Ila", "Midtbyen", "Blussuvoll", "Strindheim", "Eberg", "Charlottenlund", "Brundalen", "Åsvang", "Hoeggen", "Utleira", "Nidarvoll", "Sjetne", "Tonstad", "Breidablikk", "Romolslia", "Uglam", "Flatåsen", "Kolstad", "Stabbursmoen", "Åsheim"]
TrondheimNr = "5001"
colors = ['#377eb8', '#feb24c', '#e41a1c']

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

traffic_data = read_excel_to_dataframe("traffic-5001.xlsx")
traffic_data = overlay_polygon_with_traffic(traffic_data, merged_area, True, False)
try:
        traffic_data['geometry'] = traffic_data['geometry'].apply(lambda x: wkt.loads(x))
except:
    pass
traffic_data = gpd.GeoDataFrame(traffic_data, geometry='geometry', crs=5973)

color_map = []
n = math.ceil(len(traffic_data['ÅDT, total'].values.tolist())/3)
ådt = sorted(traffic_data["ÅDT, total"].values.tolist())
split1 = 60
split2 = 90
final = [[],[],[]]
for i,v in enumerate(ådt):
    if i/len(ådt) * 100 < split1:
        final[0].append(v)
    elif i/len(ådt) * 100 < split2:
        final[1].append(v)
    else:
        final[2].append(v)
print(len(final[0]), len(final[1]), len(final[2]))
traffic_data['color'] = traffic_data["ÅDT, total"].apply(lambda x: colors[0] if x in final[0] else colors[1] if x in final[1] else colors[2])

fig = plt.figure()
grid = matplotlib.gridspec.GridSpec(3,4, hspace=0.2, wspace=0.2)
left = fig.add_subplot(grid[:,:-2])
topright = fig.add_subplot(grid[:-2,2:])
middleright = fig.add_subplot(grid[1:-1,2:])
bottomright = fig.add_subplot(grid[2:,2:])
traffic_data.plot(ax=left, alpha=0.9, edgecolor='k', color=traffic_data['color'].values.tolist(), linewidth=1)
cx.add_basemap(left, crs=traffic_data.crs, source=cx.providers.CartoDB.Voyager)

kwargs = dict(alpha=0.5)#, bins=100)
tr1 = traffic_data.loc[traffic_data["color"]==colors[0], 'ÅDT, total']
tr2 = traffic_data.loc[traffic_data["color"]==colors[1], 'ÅDT, total']
tr3 = traffic_data.loc[traffic_data["color"]==colors[2], 'ÅDT, total']
topright.hist([tr1,tr2,tr3], **kwargs, bins=100, color=colors, stacked=True, density=True)
topright.set_title("Frequency of traffic levels")
topright.set(ylabel="Frequency", xlabel="AADT, total") #Annual average daily traffic
topright.set_yscale('log')
#topright.hist(traffic_data['ÅDT, total'].values.tolist(), bins=500)

traffic_data['geometry_length'] = traffic_data['geometry'].apply(lambda x: x.length)
tr1 = traffic_data.loc[traffic_data["color"]==colors[0], 'geometry_length']
tr2 = traffic_data.loc[traffic_data["color"]==colors[1], 'geometry_length']
tr3 = traffic_data.loc[traffic_data["color"]==colors[2], 'geometry_length']
middleright.hist([tr1,tr2,tr3], **kwargs, bins=100, color=colors, stacked=True, density=True)
middleright.set_title("Frequency of length levels")
middleright.set(ylabel="Frequency", xlabel="Length")
middleright.set_yscale('log')
#middleright.hist(traffic_data['geometry_length'].values.tolist(), bins=50)

bottomright.scatter(traffic_data['geometry_length'].values.tolist(), traffic_data['ÅDT, total'].values.tolist(), color=traffic_data['color'].values.tolist())

plt.show()
