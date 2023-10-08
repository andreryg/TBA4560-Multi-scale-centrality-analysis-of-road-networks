import nvdbapiv3
import pandas as pd
import geopandas as gpd
from shapely import wkt

def gather_road_data(kommunenummer):
    v = nvdbapiv3.nvdbVegnett()
    v.filter( { 'kommune' : int(kommunenummer) } )
    #v.info()
    veg = pd.DataFrame(v.to_records())
    v.refresh()

    #print(veg.head(5))    
    #veg.to_excel("veg-test.xlsx")
    #return veg

    veg['geometry'] = veg['geometri'].apply( wkt.loads )
    veg.to_excel(f"veg-test-{kommunenummer}.xlsx")
    vegGDF = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )

    return vegGDF

def overlay_polygon_with_road_data(road_dataframe, polygon, kommunalveg=False, privatveg=False):
    typeveg_mask = ((road_dataframe['typeVeg'] == 'Gågate') | (road_dataframe['typeVeg'] == 'Gang- og sykkelveg') | (road_dataframe['typeVeg'] == 'Sykkelveg') | (road_dataframe['typeVeg'] == 'Fortau') | (road_dataframe['typeVeg'] == 'Gangfelt') | (road_dataframe['typeVeg'] == 'Trapp'))
    road_dataframe = road_dataframe[~typeveg_mask]

    detaljnivå_mask = ((road_dataframe['detaljnivå'] == 'Kjørebane') | (road_dataframe['detaljnivå'] == 'Kjørefelt'))
    road_dataframe = road_dataframe[~detaljnivå_mask]
    
    kategori_mask = (road_dataframe['vegkategori'] == 'S')
    road_dataframe = road_dataframe[~kategori_mask]

    if not kommunalveg:
        kategori_mask = (road_dataframe['vegkategori'] == 'K')
        road_dataframe = road_dataframe[~kategori_mask]

    if not privatveg:
        kategori_mask = (road_dataframe['vegkategori'] == 'P')
        road_dataframe = road_dataframe[~kategori_mask]

    #print(road_dataframe["geometry"])
    road_dataframe['intersect'] = road_dataframe['geometry'].apply(lambda x: wkt.loads(x).intersects(polygon))
    road_dataframe = road_dataframe.loc[road_dataframe['intersect'] == True]
    #test = wkt.loads(road_dataframe["geometry"].values.tolist()).intersects(polygon)
    #road_dataframe.to_excel("dddd.xlsx")

    return road_dataframe

if __name__ == "__main__":
    gather_road_data(5001)