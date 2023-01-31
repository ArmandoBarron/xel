from unicodedata import name
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import json
import sys
import plotly.express as px
import plotly.graph_objects as go
from pandas.api.types import is_numeric_dtype

import os
"""
    applicacion para la geolocalizacion de datos en poligonos A NIVEL AGBR.

"""

ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

centers ={
    15:{"lat":19.3969, "lon": -99.2833},
    24:{"lat":22.15,"lon":-100.96}
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

def export_figures(fig,outputpath,imagefile_name,title):
    config = {'displaylogo': False,
        'editable': True,
        'showLink': True,
        'plotlyServerURL': "https://chart-studio.plotly.com",
        'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
    }
    fig.update_layout(title=title,
                    width=1500,
                    height=1000,
                    hovermode='closest')

    fig.write_html("%s/%s.html" % (outputpath,imagefile_name),config=config)


def minmax_norm(df_input):
    return (df_input - df_input.min()) / ( df_input.max() - df_input.min())

# python3 Map.py 01_base_integrada.csv out.jpg "cvegeo" "tot_casos" "15"   
inputpath = sys.argv[1]
outputpath = sys.argv[2]
geocve_column = sys.argv[3] #cve del estado
string_label= sys.argv[4]
label_color = sys.argv[5]
title = sys.argv[6]


## params for markers in map
inputpath_markers = sys.argv[7]
x_column = sys.argv[8] # 1 - 32 segun el estado de la republica
y_column = sys.argv[9]
label = sys.argv[10]
id_marker = sys.argv[11]
size_marker = sys.argv[12]


if not validate_att(string_label):
    string_label = geocve_column


print("leyendo geojson")

geo = json.load(open("%s/GEOJSON_ESTADOS/estados.json" % (ACTUAL_PATH) ,"r"))
df = pd.read_csv(inputpath)

print("creando mapa")

zoom = 5

# countries you want
df[geocve_column] = df[geocve_column].astype("int")
wanted = df[geocve_column].unique()
print(len(wanted))

# new list of geo_json but only ones with ['properties']['ADMIN'] in countries
filtered = [g for g in geo['features'] if int(g['properties']['CODIGO']) in wanted]
geo['features'] = filtered
print(len(filtered))

fig = px.choropleth_mapbox(df, geojson=geo, locations=geocve_column, 
                        featureidkey="properties.CODIGO",
                        color_continuous_scale="Viridis",
                        hover_name=string_label,
                        zoom=zoom,
                        mapbox_style="carto-positron",
                        center={"lat":22.3969, "lon": -101.2833},
                        color=label_color,
                        opacity=0.5)


if validate_att(inputpath_markers):
    df_markers = pd.read_csv(inputpath_markers)

    if not validate_att(size_marker):
        size = 7
        size_label = 7
        size_marker = "Size"
    else:
        size = minmax_norm(df_markers[size_marker])*40 # este indice altera el tamaño maximo y minimo de los marcadores
        size_label = df_markers[size_marker]


    df_markers['cat_id'] = df_markers[label].astype('category')

    df_markers['cat_id']= df_markers['cat_id'].cat.codes
    list_colores=list(df_markers['cat_id'])

    ##verificar si la variable de color 
    if is_numeric_dtype(df_markers[label]):
        list_colors = df_markers[label]
    else:
        list_colors =  pd.Categorical(df_markers[label]).codes

    #print(list_colors)
    df_markers['color'] = list_colors
    #print(df_markers['color'].unique())

    fig.add_trace(go.Scattermapbox(lon=list(df_markers[x_column]),
                        lat=list(df_markers[y_column]),
                        mode='markers+text',
                        marker=dict(color=list_colors,colorscale="YlOrRd",size=size),
                        textposition='top right',
                        textfont=dict(size=18, color='black'),
                        
                        text=['ID: ' +str(df_markers[id_marker][i]) + '<br> Value: ' + str(df_markers[label][i]) + '<br> '+ size_marker +': ' + str(size_label[i]) for i in range(df_markers.shape[0])]
                        ))

    fig.update_layout(legend=dict(x=0.03))

    #fig.add_trace(go.Densitymapbox(lon=list(df_markers[x_column]),
    #                    lat=list(df_markers[y_column]),
    #                    opacity=.3,
    #                    radius = 25.5
    #                    ))


export_figures(fig,outputpath,"mapa",title)

