# -*- coding: utf-8 -*-


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
import sys,json
from sklearn.cluster import AgglomerativeClustering

import os  # for os.path.basename
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import MDS
from scipy.cluster.hierarchy import ward, dendrogram
from sklearn import metrics

import logging #logger
LOGER = logging.getLogger()

params = sys.argv[1]
params = json.loads(params)

sil_score=False
cal_score=False
experiments = 1
num_clusters = 5
linkage ="ward" # complete. average, ward

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

if 'num_exp' in params:
    experiments = int(params['num_exp'])

if 'num_clusters' in params:
    num_clusters = int(params['num_clusters'])

if 'linkage' in params:
    linkage = params['linkage']

if 'sil_score' in params:
    sil_score = params['sil_score']

if 'cal_score' in params:
    cal_score = params['cal_score']

array_silhoutte_scores = []
array_calinski_harabasz_score = []

for exp in list(range(experiments)):
    """# PROCESS 5

    #HIERARCHICAL DOCUMENT CLUSTERING
    """

    MDS()
    # two components as we're plotting points in a two-dimensional plane
    # "precomputed" because we provide a distance matrix
    # we will also specify `random_state` so the plot is reproducible.
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

    dist = pickle.load( open(params['input_distance_filename'], "rb" ) ) 
    #titles = pickle.load( open(params['titles_filename'], "rb" ) )

    frame = pd.read_csv(params['input_frame_filename']) 
    titles = frame[params['identifier_column']].tolist()

    linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances

    fig, ax = plt.subplots(figsize=(15, 20)) # set size
    ax = dendrogram(linkage_matrix, orientation="right", labels=titles)

    plt.tick_params(\
        axis= 'x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')

    plt.tight_layout() #show plot with tight layout

    #uncomment below to save figure
    plt.savefig(params['output_folder']+"tree.jpg", dpi=200) #save figure as ward_clusters

    plt.close()


    agg_tree = AgglomerativeClustering(linkage =linkage, n_clusters=num_clusters)
    as_comp = agg_tree.fit_predict(dist)
    labels_tree = agg_tree.labels_

    if sil_score: # silhouette_score
        silhouette_score = metrics.silhouette_score(dist, labels_tree)
        print("Silhouette_score: %.3f" % silhouette_score)
        array_silhoutte_scores.append(silhouette_score)
    if cal_score: # calinski_harabaz_score
        calinski_harabasz_score = metrics.calinski_harabaz_score(dist, labels_tree)
        print("calinski_harabasz_score: %.3f" % calinski_harabasz_score)
        array_calinski_harabasz_score.append(calinski_harabasz_score)
    LOGER.error("ITERATION %s" % exp)


pickle.dump(array_silhoutte_scores, open( params['output_folder'] + "silhouette.pkl", "wb" ) )
pickle.dump(array_calinski_harabasz_score, open( params['output_folder'] + "calinski.pkl", "wb" ) )



















'''




"""#Latent Dirichlet Allocation"""

#text = pickle.load( open( "06-text.pkl", "rb" ) )
synopses = pickle.load( open(params['texts_filename'], "rb" ) )

#strip any proper names from a text...unfortunately right now this is yanking the first word from a sentence too.
import string
def strip_proppers(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent) if word.islower()]
    return "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokens]).strip()

#strip any proper nouns (NNP) or plural proper nouns (NNPS) from a text
from nltk.tag import pos_tag

def strip_proppers_POS(text):
    tagged = pos_tag(text.split()) #use NLTK's part of speech tagger
    non_propernouns = [word for word,pos in tagged if pos != 'NNP' and pos != 'NNPS']
    return non_propernouns

# Commented out IPython magic to ensure Python compatibility.
#Latent Dirichlet Allocation implementation with Gensim

from gensim import corpora, models, similarities 

#remove proper names
preprocess = [strip_proppers(doc) for doc in synopses]

# %time tokenized_text = [tokenize_and_stem(text) for text in preprocess]
tokenized_text = [tokenize_and_stem(text) for text in preprocess]

# %time texts = [[word for word in text if word not in stopwords] for text in tokenized_text]
texts = [[word for word in text if word not in stopwords] for text in tokenized_text]

#print(len([word for word in texts[0] if word not in stopwords]))
print(len(texts[0]))

dictionary = corpora.Dictionary(texts)

dictionary.filter_extremes(no_below=1, no_above=0.8)

corpus = [dictionary.doc2bow(text) for text in texts]

len(corpus)

# Commented out IPython magic to ensure Python compatibility.
# %time lda = models.LdaModel(corpus, num_topics=5, id2word=dictionary, update_every=5, chunksize=10000, passes=100)
lda = models.LdaModel(corpus, num_topics=params['lda_topics'], id2word=dictionary, update_every=params['update_cycle'], chunksize=params['chunk_size'], passes=params['passes'])

print(lda[corpus[0]])

topics = lda.print_topics(5, num_words=20)

topics_matrix = lda.show_topics(formatted=False, num_words=20)

topics_matrix = np.array(topics_matrix)

topics_matrix.shape

print(topics_matrix)
topic_words = topics_matrix[::,1]

for i in topic_words:
    print([str(word) for word in i])
    print()

'''









