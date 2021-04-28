# -*- coding: utf-8 -*-
import logging #logger
LOGER = logging.getLogger()

import numpy as np
import pandas as pd
import nltk
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

params = sys.argv[1]
params = json.loads(params)

cv_score = False
umass_score = False
cuci_score = False
cnpmi_score = False
num_topics = 5
num_words = 20

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

if 'num_exp' in params:
    experiments = int(params['num_exp'])
if 'num_clusters' in params:
    num_topics = int(params['num_clusters'])
if 'num_words' in params:
    num_words = int(params['num_words'])

if 'cv_score' in params:
    cv_score = params['cv_score']
if 'umass_score' in params:
    umass_score = params['umass_score']
if 'cuci_score' in params:
    cuci_score = params['cuci_score']
if 'cnpmi_score' in params:
    cnpmi_score = params['cnpmi_score']

array_coherence_lda_cv = []
array_coherence_lda_umass = []
array_coherence_lda_cuci = []
array_coherence_lda_cnpmi = []

# load nltk's SnowballStemmer as variabled 'stemmer'
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer(params['lang'])
"""Below I define two functions:

<ul>
<li> *tokenize_and_stem*: tokenizes (splits the synopsis into a list of its respective words (or tokens) and also stems each token <li> *tokenize_only*: tokenizes the synopsis only
</ul>

I use both these functions to create a dictionary which becomes important in case I want to use stems for an algorithm, but later convert stems back to their full words for presentation purposes. Guess what, I do want to do that!
"""

# here I define a tokenizer and stemmer which returns the set of stems in the text that it is passed

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens


"""#Latent Dirichlet Allocation"""

stopwords = nltk.corpus.stopwords.words(params['lang'])
#text = pickle.load( open( "06-text.pkl", "rb" ) )
#synopses = pickle.load( open(params['texts_filename'], "rb" ) )
frame = pd.read_csv(params['inputfile'])
synopses = frame[params['column_to_process']].tolist()

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
for exp in list(range(experiments)):
    # Commented out IPython magic to ensure Python compatibility.
    # %time lda = models.LdaModel(corpus, num_topics=5, id2word=dictionary, update_every=5, chunksize=10000, passes=100)
    lda = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, update_every=5, chunksize=10000, passes=100)

    print(lda[corpus[0]])

    topics = lda.print_topics(num_topics, num_words=num_words)

    topics_matrix = lda.show_topics(formatted=False, num_words=num_words)

    topics_matrix = np.array(topics_matrix)


    print(topics_matrix)
    topic_words = topics_matrix[::,1]


    topics_list = []
    for i in topic_words:
        topics = []
        for word in i:
            string = word[0] + " - " + str(word[1])
            topics.append(string)
        topics_list.append(topics)
        #print([str(word) for word in i])
        #print()

    dict_frame = {}
    list_topics_names = []
    for topic_id in list(range(num_topics)):
        topic_name = 'topic_%s' % topic_id 
        list_topics_names.append(topic_name)
        dict_frame[topic_name]= topics_list[topic_id]


    frame = pd.DataFrame(dict_frame, columns = list_topics_names)
    print(frame.head())

    frame.to_csv(params['output_folder']+"frame_"+str(exp)+".csv", index=False)

    #############################################################################
    ###  VALIDATION COMPUTING THE COHERENCE SCORE ###############################
    #############################################################################

    ############### MODIFICAR AQUI PROCESSES = MAX NUM THREADS INTO THE HARDWARE
    from gensim.models import CoherenceModel

    # Compute Coherence Score
    if cv_score:
        coherence_model_lda = CoherenceModel(model=lda, texts=texts, dictionary=dictionary, coherence='c_v', processes= 4)
        coherence_lda = coherence_model_lda.get_coherence()
        print('Coherence Score (normalized pointwise mutual information and the cosine similarity): ', coherence_lda)
        array_coherence_lda_cv.append(coherence_lda)
    ###########
    if umass_score:
        coherence_model_lda = CoherenceModel(model=lda, texts=texts, dictionary=dictionary, coherence='u_mass', processes=4)
        coherence_lda = coherence_model_lda.get_coherence()
        print('Coherence Score (document cooccurrence counts, a one-preceding segmentation and a logarithmic conditional probability): ', coherence_lda)
        array_coherence_lda_umass.append(coherence_lda)
    ###########
    if cuci_score:
        coherence_model_lda = CoherenceModel(model=lda, texts=texts, dictionary=dictionary, coherence='c_uci', processes=4)
        coherence_lda = coherence_model_lda.get_coherence()
        print('Coherence Score (pointwise mutual information): ', coherence_lda)
        array_coherence_lda_cuci.append(coherence_lda)
    ###########
    if cnpmi_score:
        coherence_model_lda = CoherenceModel(model=lda, texts=texts, dictionary=dictionary, coherence='c_npmi', processes=4)
        coherence_lda = coherence_model_lda.get_coherence()
        print('Coherence Score (normalized pointwise mutual information): ', coherence_lda)
        array_coherence_lda_cnpmi.append(coherence_lda)
    LOGER.error("ITERATION %s" % exp)


pickle.dump(array_coherence_lda_cv, open( params['output_folder']+ "cv.pkl", "wb" ) )
pickle.dump(array_coherence_lda_umass, open( params['output_folder']+ "umass.pkl", "wb" ) )
pickle.dump(array_coherence_lda_cuci, open( params['output_folder']+ "cuci.pkl", "wb" ) )
pickle.dump(array_coherence_lda_cnpmi, open( params['output_folder']+ "cnpmi.pkl", "wb" ) )


