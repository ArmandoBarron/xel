from logging import exception
from unicodedata import name
import pandas as pd
import json
import sys
import plotly.express as px
import plotly.graph_objects as go

import os


ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"


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

## params for markers in map
inputpath_markers = sys.argv[1]
outputpath = sys.argv[2]

x_column = sys.argv[3] # 1 - 32 segun el estado de la republica
y_column = sys.argv[4]
radius = int(sys.argv[5])
title = sys.argv[6]



df_markers = pd.read_csv(inputpath_markers)

params = dict(lat=y_column, lon=x_column,zoom=7,radius=radius,mapbox_style = "carto-positron")

fig = px.density_mapbox(df_markers, **params)

export_figures(fig,outputpath,"DensityMap",title)
