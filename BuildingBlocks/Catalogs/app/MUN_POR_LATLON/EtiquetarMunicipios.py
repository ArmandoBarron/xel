import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon,Point
import pandas as pd
import sys
import os
"""
    applicacion para la geolocalizacion de datos en poligonos A NIVEL AGBR.

"""

ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

centers ={
    15:{"lat":19.3969, "lon": -99.2833}
}

def validate_att(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="" or att =="-":
        return False
    else:
        return True

def validate_bool(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="0":
        return False
    else:
        return True




# python3 Map.py 01_base_integrada.csv out.jpg "cvegeo" "tot_casos" "15"   
inputpath = sys.argv[1]
outputpath = sys.argv[2]
lat_column = sys.argv[3]
lon_column= sys.argv[4]

df = pd.read_csv(inputpath)

# convertir shapes a geojson
geo_df = gpd.read_file(ACTUAL_PATH+"Municipios/municipios_mx_feb2018.shp")

print()
df["CVE_MUN"]=""
df["CVE_ENT"]=""

for index,row in df.iterrows():
    p = Point(row[lon_column], row[lat_column])
    mun = geo_df[geo_df.geometry.contains(p)]
    df.loc[index,'CVE_MUN'] = mun['CVE_MUN'].iloc[0]
    df.loc[index,'CVE_ENT'] = mun['CVE_ENT'].iloc[0]
    df.loc[index,'NOMGEO'] = mun['NOMGEO'].iloc[0]

df.to_csv(outputpath,index=False)
