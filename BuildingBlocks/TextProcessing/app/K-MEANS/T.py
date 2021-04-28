# -*- coding: utf-8 -*-

from __future__ import print_function
from sklearn.cluster import KMeans
from sklearn import metrics
import numpy as np
import pandas as pd
#import nltk
#nltk.download('stopwords')
#nltk.download('punkt')
import re
import os
import pickle
import codecs
from sklearn import feature_extraction
#!pip install mpld3
import mpld3
import json,sys

import logging #logger
LOGER = logging.getLogger()

params = sys.argv[1]
params = json.loads(params)

sil_score=False
cal_score=False
experiments = 1

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

if 'num_exp' in params:
    experiments = int(params['num_exp'])

if 'sil_score' in params:
    sil_score = params['sil_score']

if 'cal_score' in params:
    cal_score = params['cal_score']

array_silhoutte_scores = []
array_calinski_harabasz_score = []

for exp in list(range(experiments)):
    """# PROCESS 3

    #K-means clustering

    Now onto the fun part. Using the tf-idf matrix, you can run a slew of clustering algorithms to better understand the hidden structure within the synopses. I first chose [k-means](http://en.wikipedia.org/wiki/K-means_clustering). K-means initializes with a pre-determined number of clusters (I chose 5). Each observation is assigned to a cluster (cluster assignment) so as to minimize the within cluster sum of squares. Next, the mean of the clustered observations is calculated and used as the new cluster centroid. Then, observations are reassigned to clusters and  centroids recalculated in an iterative process until the algorithm reaches convergence.

    I found it took several runs for the algorithm to converge a global optimum as k-means is susceptible to reaching local optima.
    """

    # Commented out IPython magic to ensure Python compatibility.

    km = KMeans(n_clusters=params['num_clusters'])

    tfidf_matrix = pickle.load(open(params['representation_filename'], "rb" ))

    # %time km.fit(tfidf_matrix)
    km.fit(tfidf_matrix)

    clusters = km.labels_.tolist()

    #from sklearn.externals import joblib
    import joblib

    joblib.dump(km,  params['model_output'])


    frame = pd.read_csv(params['input_frame_filename'])
    ranks = [i for i in range(frame.shape[0])]
    frame.index = clusters  # can be a list, a Series, an array or a scalar   
    frame.insert(loc=0, column='rank', value=ranks)
    frame.insert(loc=2, column='cluster', value=clusters)
    #frame.drop('synopsis', axis=1, inplace=True)
    frame['cluster'].value_counts()
    grouped = frame['rank'].groupby(frame['cluster'])
    grouped.mean()


    #This is purely to help export tables to html and to correct for my 0 start rank (so that Godfather is 1, not 0)
    frame['Rank'] = frame['rank'] + 1
    #frame['Title'] = frame['title']

    print(frame.head())


    #pickle.dump(frame, open(params['output_frame_filename'], "wb" ))
    if experiments == 1:
        file_output = params['frame_output']
    else:
        file_output = params['output_folder']+ "frame_"+str(exp)+".csv"
    frame.to_csv(file_output, index=False)


    #
    # Calculate Validation Scores
    #

    if sil_score: # silhouette_score
        silhouette_score = metrics.silhouette_score(tfidf_matrix, km.labels_, metric='cosine')
        print("Silhouette_score: %.3f" % silhouette_score)
        array_silhoutte_scores.append(silhouette_score)
    if cal_score: # calinski_harabaz_score
        calinski_harabasz_score = metrics.calinski_harabaz_score(tfidf_matrix.toarray(), km.labels_)
        print("calinski_harabasz_score: %.3f" % calinski_harabasz_score)
        array_calinski_harabasz_score.append(calinski_harabasz_score)
    
    LOGER.error("ITERATION %s" % exp)

pickle.dump(array_silhoutte_scores, open( params['output_folder'] + "silhouette.pkl", "wb" ) )
pickle.dump(array_calinski_harabasz_score, open( params['output_folder'] + "calinski.pkl", "wb" ) )