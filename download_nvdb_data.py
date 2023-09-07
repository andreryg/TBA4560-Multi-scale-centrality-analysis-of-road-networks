import nvdbapiv3
import pandas as pd
#import geopandas as gpd
#from shapely import wkt
#import matplotlib.pyplot as plt

def gather_road_data():
    v = nvdbapiv3.nvdbVegnett()
    v.filter( { 'kommune' : 5001 } )
    v.filter( {'kartutsnitt': '269834.722,7041016.566,271133.21,7042310.3'} )
    veg = pd.DataFrame(v.to_records())

    print(veg.head(5))
    typeveg_mask = ((veg['typeVeg'] == 'Gågate') | (veg['typeVeg'] == 'Gang- og sykkelveg') | (veg['typeVeg'] == 'Sykkelveg') | (veg['typeVeg'] == 'Fortau') | (veg['typeVeg'] == 'Gangfelt'))
    veg = veg[~typeveg_mask]

    detaljnivå_mask = ((veg['detaljnivå'] == 'Kjørebane') | (veg['detaljnivå'] == 'Kjørefelt'))
    veg = veg[~detaljnivå_mask]
    
    #veg.to_excel("veg-test.xlsx")
    return veg

    #veg['geometry'] = veg['geometri'].apply( wkt.loads )
    #vegGDF = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )
    #vegGDF.plot()
    #plt.show()

#gather_road_data()