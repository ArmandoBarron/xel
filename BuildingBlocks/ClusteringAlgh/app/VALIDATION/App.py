from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
from sklearn.metrics import calinski_harabasz_score, silhouette_score, davies_bouldin_score
from sklearn.cluster import AgglomerativeClustering
import plotly.express as px

import pandas as pd
import json
import sys
import time
import tempfile
import logging

def validate_bool(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="0":
        return False
    else:
        return True

def DB_scan(dbscan_params,data,col):
    arr_labels={}
    dataToProcess = data[col]
    clustering = DBSCAN(**dbscan_params).fit(dataToProcess)
    arr_labels['default']=clustering.labels_
    return arr_labels


def K_means(k,data,col):
    arr_labels={}
    dataToProcess = data[col]
    kmeans = KMeans(n_clusters=k).fit(dataToProcess)
    k_labels = kmeans.predict(dataToProcess)
    arr_labels['default']=k_labels
    return arr_labels


def MixtureModel(k,data,col):
    arr_labels={}
    dataToProcess = data[col]
    modelo_gmm = GaussianMixture(
                n_components    = k,
                covariance_type = 'full',
                random_state    = 123)
    modelo_gmm.fit(dataToProcess)
    k_labels = modelo_gmm.predict(dataToProcess)
    arr_labels['default']=k_labels
    return arr_labels


def agglomerative(agg_params,K,data,col):
    arr_labels={}
    cacheFile = tempfile.TemporaryDirectory()# FILE TO SAVE DATA


    for lk in agg_params['linkage']:
        ward = AgglomerativeClustering(n_clusters=K, linkage=lk,memory=cacheFile.name).fit(data[col]) #linkage
        arr_labels[lk]=ward.labels_

    cacheFile.cleanup()
    return arr_labels

    
def read_CSV(name):
    return pd.read_csv("./data/"+name+".csv")

def export_figures(fig,outputpath,imagefile_name,config):
    fig.update_layout(title="Validation scores",
                    dragmode='select',
                    width=1000,
                    height=1000,
                    hovermode='closest')

    fig.write_image("%s/%s.png" % (outputpath,imagefile_name))
    fig.write_image("%s/%s.svg" % (outputpath,imagefile_name))
    fig.write_html("%s/%s.html" % (outputpath,imagefile_name),config=config)


LOG = logging.getLogger()

inicio = time.time()
# recibir K

input_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path

k= int(sys.argv[3])
algh= sys.argv[4]
columns= sys.argv[5].split(",")
clustering_params= sys.argv[6]
sample_size= int(sys.argv[7])
if_sil_score= validate_bool(sys.argv[8])
if_cal_score= validate_bool(sys.argv[9])
if_dav_score = validate_bool(sys.argv[10])

array_k_value = []
array_scores = []
array_scores_label = []

LOG.error(clustering_params)
clustering_params= json.loads(clustering_params)

#read data frame 
DF_data = pd.read_csv(input_path)
clean_DF_data = DF_data[columns].dropna(how="any")
len_DF_data= len(DF_data)

for i in range(2,k+1):
    # KMEANS
    if (algh=="kmeans"):
            arr_labels = K_means(i,clean_DF_data,columns)
    elif (algh=="gm"):
            arr_labels = MixtureModel(i,clean_DF_data,columns)
    elif (algh=="agglomerative"):
            arr_labels = agglomerative(clustering_params['agglomerative'],i,clean_DF_data,columns)

    if if_sil_score: # silhouette_score
        #print("calculating sil score")
        score_silhouette = silhouette_score(clean_DF_data, arr_labels['default'], metric='euclidean',sample_size=sample_size)
        #print("Silhouette_score: %.3f" % score_silhouette)
        array_scores.append(score_silhouette)
        array_scores_label.append("silhoutte")
        array_k_value.append(i)

    if if_cal_score: # calinski_harabaz
        #print("calculating calinski score")
        score_calinski = calinski_harabasz_score(clean_DF_data, arr_labels['default'])
        #print("calinski_harabasz_score: %.3f" % score_calinski)
        array_scores.append(score_calinski)
        array_scores_label.append("calinski_harabasz")
        array_k_value.append(i)

    if if_dav_score: # calinski_harabaz
        #print("calculating davies_bouldin score")
        score_bouldin = davies_bouldin_score(clean_DF_data, arr_labels['default'])
        #print("davies_bouldin_score: %.3f" % score_bouldin)
        array_scores.append(score_bouldin)
        array_scores_label.append("davies_bouldin")
        array_k_value.append(i)

    cluster_labels= pd.DataFrame(["-"] * len_DF_data) ##array de labels vacios
    arr_labels = list(arr_labels['default'])
    cluster_labels.loc[DF_data[columns].notna().all(axis=1),0] = arr_labels # rellenar array de labels vacios con labels de grupos
    name = "class_K-%s" % i
    DF_data[name]=cluster_labels[0].values.tolist()


def plot_line_scores(df):
    # exportar resultados
    v = df['validation_index'].iloc[0]
    imagefile_name = "scores_plot_"+v

    params_plot = dict(x='k', y="score", line_shape="linear", render_mode="svg", markers=True)
    fig = px.line(df, **params_plot)
    config = {'displaylogo': False,
            'editable': True,
            'showLink': True,
            'plotlyServerURL': "https://chart-studio.plotly.com",
            'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
    }
    export_figures(fig,output_path,imagefile_name,config)


## diseñar grafica de scores
if if_cal_score or if_sil_score:
    data = {'k': array_k_value, 'score': array_scores, 'validation_index':array_scores_label}  
    df = pd.DataFrame(data)

    print("ploting...")
    df.groupby("validation_index").apply(plot_line_scores)

    df.to_csv(output_path+"scores.csv",index=False)


print("saving results...")

DF_data.to_csv(output_path+"labels.csv",index=False)

fin = time.time()
