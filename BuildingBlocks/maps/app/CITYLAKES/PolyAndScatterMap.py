from unicodedata import name
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import json
import sys
import plotly.express as px
import plotly.graph_objects as go
import glob
import geojson

import os
"""
    applicacion para la geolocalizacion de datos en poligonos A NIVEL AGBR.

"""

ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

centers ={
    15:{"lat":19.3969, "lon": -99.2833},
    24:{"lat":22.15,"lon":-100.96}
}
def get_polygon_center(geojson_data):

    geometry = geojson_data['geometry']
    if geometry['type'] == 'Polygon':
        coordinates = geometry['coordinates'][0]  # Primer anillo exterior del polígono
        num_points = len(coordinates)
        total_lat, total_lon = 0, 0
        for lon, lat in coordinates:
            total_lat += lat
            total_lon += lon
        center_lat = total_lat / num_points
        center_lon = total_lon / num_points
        return center_lat, center_lon
    return None

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

def export_figures(fig,outputpath,imagefile_name,title):
    config = {'displaylogo': False,
        'editable': True,
        'showLink': True,
        'plotlyServerURL': "https://chart-studio.plotly.com",
        'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
    }
    fig.update_layout(title=title,
                    width=1000,
                    height=650,
                    hovermode='closest')

    fig.write_html("%s/%s.html" % (outputpath,imagefile_name),config=config)

def CreateGeocve(df):
    # Rellenar los valores de 'cve_ent' con ceros a la izquierda
    df[cve_ent] = df[cve_ent].astype(int).astype(str).str.zfill(2)
    df[cve_mun] = df[cve_mun].astype(int).astype(str).str.zfill(3)
    df["CVE_GEO"] = df[cve_ent]+df[cve_mun] 
    return df

def unify_geojson_files_in_folder(folder_path):
    combined_features = []

    # Obtener la lista de archivos GeoJSON en la carpeta
    geojson_files = glob.glob(os.path.join(folder_path, '*.json'))
    for file_path in geojson_files:
        with open(file_path, 'r') as file:
            data = geojson.load(file)
            if data['type'] == 'FeatureCollection':
                combined_features.extend(data['features'])
            elif data['type'] == 'Feature':
                combined_features.append(data)

    feature_collection = geojson.FeatureCollection(combined_features)
    return feature_collection


"""
python3 PolyAndScatterMap.py Guanajuato.csv output/ "ENT_CVE" "MUN_CVE" "MUN_CVE" "TASA" "ANIO_REGIS" "Cancer de mama" "CalidadAgua.csv" "LONGITUD" "LATITUD" "SEMAFORO" "SITIO"
"""
# python3 Map.py 01_base_integrada.csv out.jpg "cvegeo" "tot_casos" "15"   
inputpath = sys.argv[1]
outputpath = sys.argv[2]
cve_ent = sys.argv[3] #cve entidad
cve_mun = sys.argv[4]
string_label= sys.argv[5]
label_color = sys.argv[6]
temporal = sys.argv[7]
title = sys.argv[8]


## params for markers in map
inputpath_markers = sys.argv[9]
x_column = sys.argv[10] # 1 - 32 segun el estado de la republica
y_column = sys.argv[11]
label = sys.argv[12]
id_marker = sys.argv[13]

geocve_column = "CVE_GEO"

COLORES ={"Rojo":"#F25064","Verde":"#50F2BA","Amarillo":"#F2DC50"}
if not validate_att(string_label):
    string_label = cve_ent

print("leyendo geojson")

df = pd.read_csv(inputpath)

#geo = json.load(open("%s/mun/muni_2018.json" % (ACTUAL_PATH) ,"r"))
geo = unify_geojson_files_in_folder("%s/mun/" % (ACTUAL_PATH))
print("creando mapa")


df = CreateGeocve(df)

# filtro harcodeado
#causadef="C44"
#df = df[(df["SEXO"]=="Total")]
#df = df[(df["RANGO_EDAD"]=="Total")]
#df = df[(df["CAUSA_DEF"]==causadef)]
#df = df[(df["ANIO_REGIS"]==2020)]
#title = "Cancer de Piel"

#ref harcodeadas
#df_ref = pd.read_csv("Mortalidad_Tasas_soloestatales.csv")
#
#df_ref_estatales = df_ref[(df_ref["ENT_CVE"]!="Total")]
#df_ref_estatales = df_ref_estatales[(df_ref_estatales["CAUSA_DEF"]==causadef)]
#df_ref_estatales['REF_ESTATAL'] = df_ref_estatales["TASA_AJUSTADA"]
#df_ref_estatales[cve_ent] = df_ref_estatales[cve_ent].astype(int).astype(str).str.zfill(2)
#
#df_ref_nacional = df_ref[(df_ref["ENT_CVE"]=="Total")]
#df_ref_nacional = df_ref_nacional[(df_ref_nacional["CAUSA_DEF"]==causadef)]
#df_ref_nacional['REF_NACIONAL'] = df_ref_nacional["TASA_AJUSTADA"]



#df = pd.merge(df, df_ref_estatales[['CAUSA_DEF','ANIO_REGIS','ENT_CVE','REF_ESTATAL']], on=['CAUSA_DEF','ANIO_REGIS','ENT_CVE'])
#df = pd.merge(df, df_ref_nacional[['CAUSA_DEF','ANIO_REGIS','REF_NACIONAL']], on=['CAUSA_DEF','ANIO_REGIS'])


# countries you want
wanted = df[geocve_column].unique()
print(len(wanted))
print(len(geo['features']))
# new list of geo_json but only ones with ['properties']['ADMIN'] in countries
filtered = [g for g in geo['features'] if g['properties']['CVEGEO'] in wanted]
geo['features'] = filtered
print(len(filtered))

range_color = [df[label_color].min(),df[label_color].max()]

lat,lon= get_polygon_center(geo['features'][1])
cent ={"lat":lat, "lon": lon}
#cent = centers[15]
zoom = 7


fig = px.choropleth_mapbox(df, geojson=geo, locations=geocve_column, 
                        featureidkey="properties.CVEGEO",
                        color_continuous_scale="Sunset",
                        hover_name=string_label,
                        zoom=zoom,
                        center = cent,
                        mapbox_style="stamen-terrain",
                        color=label_color,
                        animation_frame=temporal,
                        range_color=range_color,
                        #hover_data=["REF_ESTATAL","REF_NACIONAL"],
                        opacity=0.7)

fig.update_traces(marker_line_width=0)

if validate_att(inputpath_markers):
    df_markers = pd.read_csv(inputpath_markers)
    # filtro harcodeado
    #df_markers = df_markers[(df_markers["ESTADO"]=="GUANAJUATO")]

    df_markers['cat_id'] = df_markers[label].astype('category')

    df_markers['cat_id']= df_markers['cat_id'].cat.codes
    list_colores=list(df_markers['cat_id'])

    
    for namedf,group_df in df_markers.groupby([label]):
        print(group_df.shape)

        # Hardcodeado
        lista_textos = ['ID: ' +str(group_df[id_marker].iloc[i]) + '<br> Pollutants: ' + str(group_df["CONTAMINANTES"].iloc[i]) for i in range(group_df.shape[0])]
        parametros = dict(lon=list(group_df[x_column]),
                            lat=list(group_df[y_column]),
                            mode='markers',
                            marker=dict(size=8),
                            textposition='top right',
                            textfont=dict(size=16, color='black'),
                            hovertext=lista_textos,
                            name=namedf,
                            hoverinfo="all",
                            #visible ="legendonly"
                            )
        try:
            color=COLORES[namedf]
            parametros['marker']['color'] = color
        except Exception:
            pass

        fig.add_trace(go.Scattermapbox(parametros))


    fig.update_layout(legend=dict(x=0.03, title=label))

    #fig.add_trace(go.Densitymapbox(lon=list(df_markers[x_column]),
    #                    lat=list(df_markers[y_column]),
    #                    opacity=.3,
    #                    radius = 25.5
    #                    ))


export_figures(fig,outputpath,"mapa",title)

