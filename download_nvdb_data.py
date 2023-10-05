import nvdbapiv3
import pandas as pd
#import geopandas as gpd
#from shapely import wkt
#import matplotlib.pyplot as plt

def gather_road_data(linestring, kommunalveg=False, privatveg=False):
    v = nvdbapiv3.nvdbVegnett()
    v.filter( { 'kommune' : 5001 } )
    a = str(linestring)[2:-2].replace(" ", ",").split(",")
    b = [(x + " " + y) for x,y in zip(a[0::2], a[1::2])]
    v.filter( {'polygon': str(b)[1:-1].replace("'", "")} )
    #v.info()
    veg = pd.DataFrame(v.to_records())
    v.refresh()

    #print(veg.head(5))
    typeveg_mask = ((veg['typeVeg'] == 'Gågate') | (veg['typeVeg'] == 'Gang- og sykkelveg') | (veg['typeVeg'] == 'Sykkelveg') | (veg['typeVeg'] == 'Fortau') | (veg['typeVeg'] == 'Gangfelt'))
    veg = veg[~typeveg_mask]

    detaljnivå_mask = ((veg['detaljnivå'] == 'Kjørebane') | (veg['detaljnivå'] == 'Kjørefelt'))
    veg = veg[~detaljnivå_mask]
    
    kategori_mask = (veg['vegkategori'] == 'S')
    veg = veg[~kategori_mask]
    
    if not kommunalveg:
        kategori_mask = (veg['vegkategori'] == 'K')
        veg = veg[~kategori_mask]
    
    if not privatveg:
        kategori_mask = (veg['vegkategori'] == 'P')
        veg = veg[~kategori_mask]
    
    #veg.to_excel("veg-test.xlsx")
    return veg

    #veg['geometry'] = veg['geometri'].apply( wkt.loads )
    #vegGDF = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )
    #vegGDF.plot()
    #plt.show()

#gather_road_data()