import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import json
import sys
import plotly.express as px
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

def export_figures(fig,outputpath,imagefile_name,title):
    config = {'displaylogo': False,
        'editable': True,
        'showLink': True,
        'plotlyServerURL': "https://chart-studio.plotly.com",
        'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
    }
    fig.update_layout(title=title,
                    width=1800,
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


export_figures(fig,outputpath,"mapa",title)

"""

app = Flask(__name__)

#root service
@app.route('/')
def prueba():
    return {"status":"OK","message":"shapes"}



@app.route('/CreateJSONS')
def createjsons():
    df = gpd.read_file("Shapes/15mun_wgs84.shp")
    df['centroid']=''
    def coord_lister(row):
        if isinstance(row.geometry, MultiPolygon):
            list_of_polys = []
            for poly in row.geometry:
                list_points= []
                for p in poly.exterior.coords:
                    list_points.append({"lat":p[0],"lng":p[1]})
                list_of_polys.append(list_points)
            row.centroid = {"lat":row.geometry.centroid.x,"lng":row.geometry.centroid.y}
            
            row.geometry = list_of_polys
        else:
            list_points= []
            for p in row.geometry.exterior.coords:
                list_points.append({"lat":p[0],"lng":p[1]})
            row.centroid = {"lat":row.geometry.centroid.x,"lng":row.geometry.centroid.y}
            row.geometry = list_points
        return row

    coordinates = df.apply(coord_lister,axis=1)
    coordinates[['cvegeo','nomgeo','geometry']].to_json("catalogs/polygon_15mun.json",orient="columns")
    coordinates[['cvegeo','nomgeo','centroid']].to_json("catalogs/centroid_15mun.json",orient="columns")

    return {"status":"OK","message":"shapes"}

    
@app.route('/getPolygon',methods=['POST'])
def get_agbs():
    params = request.get_json(force=True)
    print(params['states'])

    return json.load(open("catalogs/15mun.json", "r") )

if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=5555,debug=True)
"""