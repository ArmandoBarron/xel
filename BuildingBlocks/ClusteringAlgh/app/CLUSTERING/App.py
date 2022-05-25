from gettext import npgettext
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import AgglomerativeClustering

import pandas as pd
import json
import sys
import time
import tempfile
import logging
import numpy as np

def sort_labels(centroids,labels):
    idx = np.argsort(centroids)
    lut = np.zeros_like(idx)
    lut[idx] = np.arange(k)
    print(labels)
    print(lut[labels])
    return lut[labels]

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
    arr_labels['default'] = sort_labels(kmeans.cluster_centers_.sum(axis=1),k_labels)
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
    arr_labels['default'] = sort_labels(modelo_gmm.means_.sum(axis=1),k_labels)

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

LOG = logging.getLogger()

inicio = time.time()
# recibir K

input_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path

k= int(sys.argv[3])
algh= sys.argv[4]
columns= sys.argv[5].split(",")
clustering_params= sys.argv[6]

LOG.error(clustering_params)
clustering_params= json.loads(clustering_params)

print(clustering_params['dbscan'])
#read data frame 
DF_data = pd.read_csv(input_path)
clean_DF_data = DF_data[columns].dropna(how="any")
len_DF_data= len(DF_data)

# KMEANS
if (algh=="kmeans"):
        arr_labels = K_means(k,clean_DF_data,columns)
elif (algh=="gm"):
        arr_labels = MixtureModel(k,clean_DF_data,columns)
elif (algh=="dbscan"):
        arr_labels = DB_scan(clustering_params['dbscan'],clean_DF_data,columns)
elif (algh=="agglomerative"):
        arr_labels = agglomerative(clustering_params['agglomerative'],k,clean_DF_data,columns)


cluster_labels= pd.DataFrame(["-"] * len_DF_data) ##array de labels vacios
arr_labels = list(arr_labels['default'])
cluster_labels.loc[DF_data[columns].notna().all(axis=1),0] = arr_labels # rellenar array de labels vacios con labels de grupos
name = "class"

DF_data[name]=cluster_labels[0].values.tolist()
print(DF_data)

DF_data.to_csv(output_path,index=False)

fin = time.time()
