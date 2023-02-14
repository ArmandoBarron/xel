#import geopandas as gpd
import plotly.express as px
import json
import os
import pandas as pd
import sys

def validate_att(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="" or att =="-":
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
                    width=2000,
                    height=1200,
                    hovermode='closest')

    fig.write_html("{}/{}.html".format(outputpath,imagefile_name.replace('>','_')),config=config)
    
"""
Applicacion para generar mapas de shapes de los estados de mexico, por colores y temporal

** e.g. python3 plotMapState.py cancer_piel_100k_estados.csv ./out/ 'ent_regis' 'nombre entidad' HEATMAP 'tasa_100k' '' 'Poblacion total,count' 'titulo de ejemplo'


python3 plotMapState.py defunciones_all_5anios.csv ./out/ 'ENT_OCURR' 'ENT_OCURR' 'HEATMAP' 'TASA_AJUSTADA' 'ANIO_REGIS' 'CONTEO,TASA_CRUDA,TASA_AJUSTADA,codigo,Descripcion' 'Defunciones'
"""
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

INPUTPATH = sys.argv[1]
OUTPUTPATH = sys.argv[2]
GEOCVE_COLUMN = sys.argv[3] #cve del estado
STRING_LABEL= sys.argv[4] #label used to identify the point
KIND_MAP = sys.argv[5] #HEATMAP or CLASS 
LABEL_COLOR = sys.argv[6] # class column
TEMPORAL_COL = sys.argv[7]

ADDITIONAL_COL =sys.argv[8] # "col1,col2,col3 = []"
TITLE = sys.argv[9]


if not validate_att(STRING_LABEL):
    STRING_LABEL = geocve_column
if not validate_att(TEMPORAL_COL):
    TEMPORAL_COL = None

if not validate_att(ADDITIONAL_COL):
    ADDITIONAL_COL = []
else:
    ADDITIONAL_COL = ADDITIONAL_COL.split(",")

print("leyendo geojson")
geo = json.load(open("%s/GEOJSON_ESTADOS/estados.json" % (ACTUAL_PATH) ,"r"))
df = pd.read_csv(INPUTPATH)
#df["shortname"] = df["codigo"] + "_"+ df["Descripcion"].str.split().str[:3].str.join(sep=" ")
#df.to_csv("defunciones_short.csv", index=False)
#exit()

#df = df[df["CAUSA_DEF"]=="C16"]
print("creando mapa")

zoom = 4

# countries you want
df[GEOCVE_COLUMN] = df[GEOCVE_COLUMN].astype("int")
wanted = df[GEOCVE_COLUMN].unique()
print(len(wanted))

# new list of geo_json but only ones with ['properties']['ADMIN'] in countries
filtered = [g for g in geo['features'] if int(g['properties']['CODIGO']) in wanted]
geo['features'] = filtered
print(len(filtered))


cols = [TEMPORAL_COL,GEOCVE_COLUMN,STRING_LABEL] + ADDITIONAL_COL
# to remove None values in list
cols = [i for i in cols if i is not None]
# remove those that already exist
#cols.remove(GEOCVE_COLUMN)
if LABEL_COLOR in cols: cols.remove(LABEL_COLOR)
cols = [*set(cols)]

print(cols)

if KIND_MAP == "HEATMAP":
    df_general = df.groupby(cols)[LABEL_COLOR].median().reset_index()
elif KIND_MAP == "CLASS":
    df_general = df.groupby(cols)[LABEL_COLOR].mode().reset_index()
else:
    df_general = df

if TEMPORAL_COL is not None:
    df_general= df_general.sort_values(by=[TEMPORAL_COL])

fig = px.choropleth_mapbox(df_general, geojson=geo, locations=GEOCVE_COLUMN, 
                            featureidkey="properties.CODIGO",
                            color_continuous_scale="Viridis",
                            hover_name=STRING_LABEL,
                            zoom=zoom,
                            mapbox_style="carto-positron",
                            center={"lat":22.3969, "lon": -101.2833},
                            color=LABEL_COLOR,
                            hover_data =cols,
                            animation_frame=TEMPORAL_COL,
                            animation_group=GEOCVE_COLUMN,
                            opacity=0.5)

export_figures(fig,OUTPUTPATH,"States",TITLE)
