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
label = sys.argv[5]
id_marker = sys.argv[6]
size_point = sys.argv[7]
title = sys.argv[8]
groupby_columns = sys.argv[9]



df_markers = pd.read_csv(inputpath_markers)


#$df_markers['cat_id'] = df_markers[label].astype('category')
#$df_markers['cat_id']= df_markers['cat_id'].cat.codes
#$list_colores=list(df_markers['cat_id'])



def CreateMap(df,anim_group=None):

    gb_c = ""
    params = dict(lat=y_column, lon=x_column,hover_name=id_marker,color=label,zoom=7,range_color=range_colors,color_continuous_scale=px.colors.sequential.Bluered,mapbox_style = "carto-positron")

    if not validate_att(size_point):
        pass
    else:
        params['size'] = size_point

    try:

        if anim_group is not None:
            params['animation_frame']=anim_group
            df = df.sort_values(anim_group, ascending=True)

        fig = px.scatter_mapbox(df,**params)

        fig.update_layout(legend=dict(x=0.03))
        export_figures(fig,outputpath,"ScatterMap_%s" %(gb_c) ,title)
    except Exception as e:
        print(e)

range_colors = [df_markers[label].min(),df_markers[label].max()]
print(range_colors)
if groupby_columns =='' or groupby_columns == '-':
    CreateMap(df_markers)
else:
    CreateMap(df_markers,anim_group=groupby_columns)
    #df_markers.groupby(groupby_columns).apply(CreateMap)