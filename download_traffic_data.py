import nvdbapiv3
import pandas as pd
from shapely import wkt

def gather_traffic_data(kommunenummer):
    t = nvdbapiv3.nvdbFagdata(540)
    t.filter( { 'kommune' : int(kommunenummer) } )
    #v.info()
    traffic = pd.DataFrame(t.to_records())
    t.refresh()

    #print(veg.head(5))    
    #veg.to_excel("veg-test.xlsx")
    #return veg

    traffic['geometry'] = traffic['geometri'].apply( wkt.loads )
    traffic.to_excel(f"traffic-{kommunenummer}.xlsx")
    #vegGDF = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )

    return True

def overlay_polygon_with_traffic(traffic_dataframe, polygon, kommunalveg=False, privatveg=False):    
    kategori_mask = (traffic_dataframe['vegkategori'] == 'S')
    traffic_dataframe = traffic_dataframe[~kategori_mask]

    if not kommunalveg:
        kategori_mask = (traffic_dataframe['vegkategori'] == 'K')
        traffic_dataframe = traffic_dataframe[~kategori_mask]

    if not privatveg:
        kategori_mask = (traffic_dataframe['vegkategori'] == 'P')
        traffic_dataframe = traffic_dataframe[~kategori_mask]

    #print(traffic_dataframe["geometry"])
    traffic_dataframe['intersect'] = traffic_dataframe['geometry'].apply(lambda x: wkt.loads(x).intersects(polygon))
    traffic_dataframe = traffic_dataframe.loc[traffic_dataframe['intersect'] == True]
    #test = wkt.loads(traffic_dataframe["geometry"].values.tolist()).intersects(polygon)
    #traffic_dataframe.to_excel("dddd.xlsx")

    return traffic_dataframe

if __name__ == "__main__":
    gather_traffic_data(5001)