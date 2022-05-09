import pandas as pd
import folium
import os
import imageio
import branca
import branca.colormap as cm
import numpy as np 

import sys
import logging #logger
LOGER = logging.getLogger()

INPUT_DATA = sys.argv[1] #"tm_labeled.csv"
OUTPUT_PATH = sys.argv[2] #"./results/"
MapType= int(sys.argv[3]) #1 # 1=heatmap, 2= clustermap
LAT_COLUMN = sys.argv[4] #"lat"
LON_COLUMN = sys.argv[5] #"lon"
GROUPBY_COLUMN= sys.argv[6] #"anio_regis"
VARIABLE = sys.argv[7].split(",") #"Tras. ment. & Uso sust._Hombre_Sexo,Otra causa_Mujer_Sexo".split(",")
CLASS_COLUMN = sys.argv[8] #"class"
NORMALIZE =int(sys.argv[9]) #"0 1

#HARCODEADO
LABEL = "nombre municipio"


COLORS = [
    'red',
    'blue',
    'gray',
    'darkred',
    'lightred',
    'orange',
    'beige',
    'green',
    'darkgreen',
    'lightgreen',
    'darkblue',
    'lightblue',
    'purple',
    'darkpurple',
    'pink',
    'cadetblue',
    'lightgray',
    'black'
]
def normalize(df):
    result = df.copy()
    max_value = df.max()
    min_value = df.min()
    result = (df - min_value) / (max_value - min_value)

    return result


def plot_maps(df):

    if GROUPBY_COLUMN != "":
        gb_c = df[GROUPBY_COLUMN].iloc[0]
    else:
        gb_c = "all"

    locations = df[[LAT_COLUMN, LON_COLUMN]]

    for v in VARIABLE:
        out_path = "%s%s/" %(OUTPUT_PATH,v)
        try:    
            os.mkdir(out_path)
        except FileExistsError:
            pass


        locat= [df[LAT_COLUMN].median(), df[LON_COLUMN].median()]

        map_layer = folium.Map(location=locat, zoom_start=6, control_scale=True)

        if MapType == 1: #normal map
            if NORMALIZE==1:
                df[v] = normalize(df[v])
                q1 = 0
                q2 = .25
                q3 = .5
                q4 = .75
                q5 = 1
            else:
                q1 = df[v].quantile(0)
                q2 = df[v].quantile(0.25)
                q3 = df[v].quantile(0.5)
                q4 = df[v].quantile(0.75)
                q5 = df[v].quantile(1)


            colormap = cm.LinearColormap(colors=['green', 'lightgreen', 'yellow', 'orange','red'],
                            index=[q1,q2,q3,q4,q5], vmin=q1, vmax=q5,
                             caption='%s for %s' %(v,gb_c))

            map_layer.add_child(colormap)

            for index, location_info in df.iterrows():
                if np.isnan(location_info[v]):
                    location_info[v] = 0 #se remplaza por 0

                color = colormap(location_info[v])
                html = "<p>%s</p><br> <p>%s</p>" % (location_info[LABEL],location_info[v])
                iframe = folium.IFrame(html,width=100,height=100)
                popup = folium.Popup(iframe,max_width=100)
                folium.CircleMarker(location=[location_info[LAT_COLUMN],location_info[LON_COLUMN]],
                                     radius=3,
                                     fill=True,
                                     color=color,
                                     popup=popup,
                                     fill_color=color).add_to(map_layer)

        elif MapType == 2: #with class column
            df_grouped = df.groupby(CLASS_COLUMN)

            for group_name, df_group in df_grouped: # iterate over each group
                for index, location_info in df_group.iterrows():
                    class_label = location_info[CLASS_COLUMN]
                    if class_label == "-":
                        pass
                    else:
                        class_label = int(class_label)
                        folium.Marker([location_info[LAT_COLUMN], location_info[LON_COLUMN]],icon=folium.Icon(color=COLORS[class_label])).add_to(map_layer)



        #save image
        image_path = '%s%s.html'%(out_path,gb_c)
        map_layer.save(image_path)
        LOGER.error(image_path)



gdf = pd.read_csv(INPUT_DATA) #read csv


if GROUPBY_COLUMN !="":
    gdf.groupby(GROUPBY_COLUMN).apply(plot_maps)
    #create gif
    print("creating gifs")
    for v in VARIABLE:
        out_path = "%s%s/" %(OUTPUT_PATH,v)
        #create_gif(out_path,v)
else:
    plot_maps(gdf)

