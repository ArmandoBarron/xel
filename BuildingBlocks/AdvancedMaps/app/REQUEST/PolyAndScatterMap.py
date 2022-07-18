from unicodedata import name
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import json
import sys
import plotly.express as px
import plotly.graph_objects as go

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




# python3 Map.py 01_base_integrada.csv out.jpg "cvegeo" "tot_casos" "15"   
inputpath = sys.argv[1]
outputpath = sys.argv[2]
geocve_column = sys.argv[3]
string_label= sys.argv[4]
label_color = sys.argv[5]
area = sys.argv[6] # 1 - 32 segun el estado de la republica
title = sys.argv[7]


## params for markers in map
inputpath_markers = sys.argv[8]
x_column = sys.argv[9] # 1 - 32 segun el estado de la republica
y_column = sys.argv[10]
label = sys.argv[11]
id_marker = sys.argv[12]



if not validate_att(string_label):
    string_label = geocve_column

# convertir shapes a geojson
#geo_df = gpd.read_file("Shapes/15a.shp")
#geo_df = geo_df.to_crs(epsg=4326)
#print(geo_df)
#geo_df.to_file("Shapes/15a.json", driver="GeoJSON")
#exit()

#df = px.data.gapminder()
#fig = px.choropleth(df, locations="iso_alpha",
#                    color="lifeExp", # lifeExp is a column of gapminder
#                    hover_name="country", # column to add to hover information
#                    color_continuous_scale=px.colors.sequential.Plasma,
#                    animation_frame='year')
#fig2 = px.scatter_geo(df, locations="iso_alpha",
#                    size="lifeExp", # lifeExp is a column of gapminder
#                    hover_name="country", # column to add to hover information
#                    color_continuous_scale=px.colors.sequential.Plasma,
#                    animation_frame='year')
#fig.add_trace(fig2.data[0])
#for i, frame in enumerate(fig.frames):
#    fig.frames[i].data += (fig2.frames[i].data[0],)
#fig.show()

print("leyendo geojson")

geo = json.load(open("%s/GEOJSONS/%sa.json" % (ACTUAL_PATH,area) ,"r"))
df = pd.read_csv(inputpath)

print("creando mapa")
#center of the map
try:
    cent = centers[int(area)]
    zoom = 9 
except Exception as e:
    cent = centers[15]
    zoom = 3

# countries you want
wanted = df[geocve_column].unique()
print(len(wanted))
print(len(geo['features']))

# new list of geo_json but only ones with ['properties']['ADMIN'] in countries
filtered = [g for g in geo['features'] if g['properties']['CVEGEO'] in wanted]
geo['features'] = filtered
print(len(filtered))

fig = px.choropleth_mapbox(df, geojson=geo, locations=geocve_column, 
                        featureidkey="properties.CVEGEO",
                        color_continuous_scale="Viridis",
                        hover_name=string_label,
                        zoom=zoom,
                        center = cent,
                        mapbox_style="carto-positron",
                        color=label_color,
                        opacity=0.5)


if validate_att(inputpath_markers):
    df_markers = pd.read_csv(inputpath_markers)
    df_markers['cat_id'] = df_markers[label].astype('category')

    df_markers['cat_id']= df_markers['cat_id'].cat.codes
    list_colores=list(df_markers['cat_id'])

    
    for namedf,group_df in df_markers.groupby([label]):
        fig.add_trace(go.Scattermapbox(lon=list(group_df[x_column]),
                            lat=list(group_df[y_column]),
                            mode='markers',
                            marker=dict(size=7),
                            textposition='top right',
                            textfont=dict(size=16, color='black'),
                            hovertext=group_df[id_marker],
                            name=namedf,
                            #text=['ID: ' +str(group_df[id_marker][i]) + '<br> Group: ' + str(group_df[label][i]) for i in range(group_df.shape[0])]
                            ))

    fig.update_layout(legend=dict(x=0.03))

    #fig.add_trace(go.Densitymapbox(lon=list(df_markers[x_column]),
    #                    lat=list(df_markers[y_column]),
    #                    opacity=.3,
    #                    radius = 25.5
    #                    ))


export_figures(fig,outputpath,"ScatterAndPolygonMap",title)

