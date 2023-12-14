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
import numpy as np
from area_road_graph import main

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
split1 = 70
split2 = 95
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
grid = matplotlib.gridspec.GridSpec(3,4, hspace=0.3, wspace=0.3)
left = fig.add_subplot(grid[:,:-2])
topright = fig.add_subplot(grid[:-2,2:])
middleright = fig.add_subplot(grid[1:-1,2:])
bottomright = fig.add_subplot(grid[2:,2:])

labels={'#377eb8':f"AADT: [{final[0][0]}, {final[0][-1]}]", '#feb24c':f"AADT: [{final[1][0]}, {final[1][-1]}]", '#e41a1c':f"AADT: [{final[2][0]}, {final[2][-1]}]"}
for i,dff in traffic_data.groupby('color'):
    dff.plot(ax=left, alpha=0.9, edgecolor='k', color=dff['color'].values.tolist(), linewidth=1, label=labels.get(i))
cx.add_basemap(left, crs=traffic_data.crs, source=cx.providers.CartoDB.Voyager)
left.legend(loc='upper left')

kwargs = dict(alpha=0.5)#, bins=100)
tr1 = traffic_data.loc[traffic_data["color"]==colors[0], 'ÅDT, total']
tr2 = traffic_data.loc[traffic_data["color"]==colors[1], 'ÅDT, total']
tr3 = traffic_data.loc[traffic_data["color"]==colors[2], 'ÅDT, total']
topright.hist([tr1,tr2,tr3], **kwargs, bins=100, color=colors, stacked=True)
#topright.set_title("Frequency of traffic levels")
topright.set(ylabel="Frequency", xlabel="AADT") #Annual average daily traffic
topright.set_yscale('log')
#topright.hist(traffic_data['ÅDT, total'].values.tolist(), bins=500)

traffic_data['geometry_length'] = traffic_data['geometry'].apply(lambda x: x.length)
tr1 = traffic_data.loc[traffic_data["color"]==colors[0], 'geometry_length']
tr2 = traffic_data.loc[traffic_data["color"]==colors[1], 'geometry_length']
tr3 = traffic_data.loc[traffic_data["color"]==colors[2], 'geometry_length']
middleright.hist([tr1,tr2,tr3], **kwargs, bins=100, color=colors, stacked=True)
#middleright.set_title("Frequency of length levels")
middleright.set(ylabel="Frequency", xlabel="Length [m]")
middleright.set_yscale('log')
#middleright.hist(traffic_data['geometry_length'].values.tolist(), bins=50)

bottomright.scatter(traffic_data['geometry_length'].values.tolist(), traffic_data['ÅDT, total'].values.tolist(), color=traffic_data['color'].values.tolist())
bottomright.set(ylabel="AADT", xlabel="Length [m]")
a,b = np.polyfit(traffic_data['geometry_length'].values.tolist(), traffic_data['ÅDT, total'].values.tolist(), 1)
bottomright.plot(traffic_data['geometry_length'].values.tolist(), a*traffic_data['geometry_length'].values+b, color='black')

plt.show()

cent = main()

comp = traffic_data.overlay(cent, how='intersection')

bc = sorted(comp['bc'].values.tolist())
final = [[],[],[]]
for i,v in enumerate(bc):
    if i/len(bc) * 100 < split1:
        final[0].append(v)
    elif i/len(bc) * 100 < split2:
        final[1].append(v)
    else:
        final[2].append(v)
comp['color_bc'] = comp["bc"].apply(lambda x: colors[0] if x in final[0] else colors[1] if x in final[1] else colors[2])
labels={'#377eb8':f"Centrality: [{format(final[0][0], '.4f')}, {format(final[0][-1], '.4f')}]", '#feb24c':f"Centrality: [{format(final[1][0], '.4f')}, {format(final[1][-1], '.4f')}]", '#e41a1c':f"Centrality: [{format(final[2][0], '.4f')}, {format(final[2][-1], '.4f')}]"}

f, ax = plt.subplots(1)
for i,dff in comp.groupby('color_bc'):
    dff.plot(ax=ax, alpha=0.9, edgecolor='k', color=dff['color_bc'].values.tolist(), linewidth=1, label=labels.get(i))
#ax = comp.plot(alpha=0.9, edgecolor='k', color=comp['color_bc'].values.tolist(), linewidth=1)
cx.add_basemap(ax=ax, crs=comp.crs, source=cx.providers.CartoDB.Voyager)
plt.legend(loc='upper left')
plt.show()


print(comp.columns.values.tolist())
comp['bcxtraffic'] = comp['bc'] * comp['ÅDT, total']
bcxtraffic = sorted(comp['bcxtraffic'].values.tolist())
final = [[],[],[]]
for i,v in enumerate(bcxtraffic):
    if i/len(bcxtraffic) * 100 < split1:
        final[0].append(v)
    elif i/len(bcxtraffic) * 100 < split2:
        final[1].append(v)
    else:
        final[2].append(v)
comp['fin_color'] = comp["bcxtraffic"].apply(lambda x: colors[0] if x in final[0] else colors[1] if x in final[1] else colors[2])


ax = comp.plot(alpha=0.9, edgecolor='k', color=comp['fin_color'].values.tolist(), linewidth=1)
cx.add_basemap(ax=ax, crs=comp.crs, source=cx.providers.CartoDB.Voyager)
plt.show()

plt.scatter(comp['bc'].values.tolist(), comp['ÅDT, total'].values.tolist(), color=comp['fin_color'].values.tolist())
plt.ylabel("AADT")
plt.xlabel("Betweenness centrality")
a,b = np.polyfit(comp['bc'].values.tolist(), comp['ÅDT, total'].values.tolist(), 1)
plt.plot(comp['bc'].values.tolist(), a*comp['bc'].values+b, color='black')
plt.show()

print(np.corrcoef(comp['bc'].values.tolist(), comp['ÅDT, total'].values.tolist())[0,1])
