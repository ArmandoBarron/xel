#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for
import json
from Functions import *
import logging #logger

from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn import metrics
from sklearn import preprocessing
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt

import numpy as np
import time

app = Flask(__name__)
GRAPHS_PATH = "./static"
Log = logging.getLogger()


def apply_labels(data,labeled_data,idx):
    c = len(data.index)
    data["class"] = [*range(c)]

    for index,row in labeled_data.iterrows():
        data.loc[data[idx] == row[idx], 'class'] = row['class']
    
    return data

def apply_pca(df,variance = 0.90):
    pca = PCA(variance)
    df= scale(df)
    df_components=pca.fit_transform(df)
    numcols = len(df_components[0]) # columns

    principalDf = pd.DataFrame(data = df_components, columns = ["component %s" %(x) for x in range(numcols)])
    return principalDf


def NAN_format(df):
    df.replace('None', np.nan, inplace=True)
    df.replace('NA', np.nan, inplace=True)
    df.replace('Na', np.nan, inplace=True)
    df.replace('Null', np.nan, inplace=True)
    return df


def preproc(F_dataframe,columns,idx=None):
    F_dataframe = json2dataframe(F_dataframe) 
    #data filter 

    numeric_columns = columns
    if idx is not None:
        if columns!="all":
            columns = idx+","+columns

    if columns != "all":
        #F_dataframe = DF_Filter(F_dataframe,columns) #filtred only the columns
        F_dataframe[columns.split(",")] = NAN_format(DF_Filter(F_dataframe,columns)) #clean Na only selected columns
        numeric_columns= numeric_columns.split(",")
        F_dataframe[numeric_columns] = Numeric(F_dataframe[numeric_columns])
        F_dataframe[numeric_columns] = F_dataframe[numeric_columns].fillna(F_dataframe[numeric_columns].mean()) #fill nulls in numeric columns using mean
        
        if idx is not None:
            F_dataframe=F_dataframe.groupby(idx).mean().reset_index() #only the representative values
    else:
        F_dataframe = Numeric(NAN_format(F_dataframe))
        F_dataframe = F_dataframe.fillna(F_dataframe.mean())
        if idx is not None:
            F_dataframe=F_dataframe.groupby(idx).mean().reset_index() #only the representative values

    return F_dataframe

@app.route('/')
def prueba():
    return "Clustering Service"

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

@app.route('/clustering/kmeans', methods=['POST'])
def k_means(K=2, columns="all"):
    #get data
    message = request.get_json()
    data = message['data']
    if 'K' in message: K = int(message['K'])
    if 'columns' in message: columns = message['columns']
    if 'index' in message: idx = message['index'] #filter by index (mean)
    else: idx=None
    if 'pca' in message: pca_variance = message['pca'] #filter by index (mean)
    else: pca_variance=None

    Log.error("preprocessing data ...")
    F_dataframe = preproc(data,columns,idx=idx)
    Log.error("data is ready ...")

    columns = columns.split(",")
    extra = F_dataframe.drop(columns,axis=1) #all except extra columns
    F_dataframe = F_dataframe[columns] #all the selected columns

    if pca_variance != None:#apply pca
        F_dataframe = apply_pca(F_dataframe,variance=pca_variance)

    Log.error(F_dataframe.dtypes)
    #algorithm k means
    kmeans = KMeans(n_clusters=K, random_state=0).fit(F_dataframe)

    F_dataframe['class']=kmeans.labels_
    
    F_dataframe = pd.concat([extra, F_dataframe], axis=1)

    return json.dumps({"status": "OK" ,"path":None, "result": json.loads(F_dataframe.to_json(orient='records'))})


@app.route('/clustering/herarhical', methods=['POST'])
def herarh(K=2, columns="all", method = "single"):
    #get data
    message = request.get_json()
    if 'K' in message: K = int(message['K'])
    if 'method' in message: method = message['method']
    if 'columns' in message: columns = message['columns']
    if 'index' in message: idx = message['index'] #filter by index (mean)
    else: idx=None
    if 'pca' in message: pca_variance = message['pca'] #filter by index (mean)
    else: pca_variance=None

    Log.error("preprocessing data ...")
    F_dataframe = preproc(message['data'],columns,idx=idx) #BASIC PREPROCESSING
    Log.error("data is ready ...")

    columns = columns.split(",")
    extra = F_dataframe.drop(columns,axis=1) #all except extra columns
    F_dataframe = F_dataframe[columns] #all the selected columns

    if pca_variance != None:#apply pca
        F_dataframe = apply_pca(F_dataframe,variance=pca_variance)
    #algorithm herarhical
    ward = AgglomerativeClustering(n_clusters=K, linkage=method).fit(F_dataframe)
    F_dataframe['class']=ward.labels_

    F_dataframe = pd.concat([extra, F_dataframe], axis=1)

    return json.dumps({"status": "OK" ,"path":None, "result": json.loads(F_dataframe.to_json(orient='records'))})


@app.route('/clustering/silhouette', methods=['POST'])
def silhouette():
    #get data
    message = request.get_json()
    data = message['data']
    if 'columns' in message: columns = message['columns']
    if 'index' in message: idx = message['index'] #filter by index (mean)
    else: idx=None
    if 'pca' in message: pca_variance = message['pca'] #filter by index (mean)
    else: pca_variance=None

    F_dataframe = preproc(data,columns,idx=idx) #BASIC PREPROCESSING

    km_results = []
    her_results = []

    labels_results = []
    maxK = 2

    columns = columns.split(",")
    extra = F_dataframe.drop(columns,axis=1) #all except extra columns
    F_dataframe = F_dataframe[columns] #all the selected columns

    if pca_variance != None:#apply pca
        F_dataframe = apply_pca(F_dataframe,variance=pca_variance)

    for k in range(2,15):
        try:
            #KMEANS
            kmeans = KMeans( n_clusters=k )
            kmeans.fit(F_dataframe)
            pl_kmeans = kmeans.labels_
            #HER
            ward = AgglomerativeClustering(n_clusters=k, linkage='single').fit(F_dataframe)
            pl_her = ward.labels_

            kmeans_sil = metrics.silhouette_score(F_dataframe, pl_kmeans , metric='euclidean')
            her_sil = metrics.silhouette_score(F_dataframe, pl_her , metric='euclidean')

        except ValueError as v:
            break
        #print( "Silhouette Score (K-Means, %d clusters) (her, %d clusters) =" % (k,k), kmeans_sil, her_sil)


        km_results.append( kmeans_sil )
        her_results.append(her_sil)
        labels_results.append([pl_kmeans,pl_her])

        maxK = maxK+1


    #maximum result
    M_km = km_results.index(max(km_results))
    M_hr = her_results.index(max(her_results))

    winner = [max(km_results),max(her_results)]
    winner = winner.index(max(winner))
    
    if winner == 0: #km wins
        w_lab =  labels_results[M_km][winner]
        win = "BEST: KMEANS - %s Clusters " % (int(M_km)+2)
        winner_algh = "kmeans"
    if winner == 1: #hr wins
        w_lab =  labels_results[M_km][winner]
        win = "BEST: HIERARCHICAL  %s Clusters" %(int(M_hr)+2)
        winner_algh = "herarhical"


# PLOT ---------------
    picture_name= time.strftime("%c")
    picture_name = hash(str(picture_name)+str(k)+str(winner))
    fig, ax = plt.subplots()
    plt.title(win)
    ax.plot( [i for i in range(2,maxK)], km_results )
    ax.plot( [i for i in range(2,maxK)], her_results )
    
    ax.set_xlabel('Number of Clusters (k)')
    ax.set_ylabel('Silhouette Score')
    plt.xticks([i for i in range(2,maxK)])
    #plt.show()
    PATH = "%s/%s.png" %(GRAPHS_PATH,picture_name)
    plt.savefig(PATH)
    plt.close()
#---------------------

    F_dataframe['class']=w_lab

    F_dataframe = pd.concat([extra, F_dataframe], axis=1)

    return json.dumps({"status": "OK" ,"path":PATH[1:], "winner":winner_algh ,"result": json.loads(F_dataframe.to_json(orient='records'))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True) 