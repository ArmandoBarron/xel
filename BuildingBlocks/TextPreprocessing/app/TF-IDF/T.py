# -*- coding: utf-8 -*-


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
import sys
import json

params = sys.argv[1]
params = json.loads(params)
print(params)

"""# PROCESS 2

##Tf-idf and document similarity

<img src='http://www.jiem.org/index.php/jiem/article/viewFile/293/252/2402' align='right' style="margin-left:10px">

Here, I define term frequency-inverse document frequency (tf-idf) vectorizer parameters and then convert the *synopses* list into a tf-idf matrix. 

To get a Tf-idf matrix, first count word occurrences by document. This is transformed into a document-term matrix (dtm). This is also just called a term frequency matrix. An example of a dtm is here at right.

Then apply the term frequency-inverse document frequency weighting: words that occur frequently within a document but not frequently within the corpus receive a higher weighting as these words are assumed to contain more meaning in relation to the document.

A couple things to note about the parameters I define below:

<ul>
<li> max_df: this is the maximum frequency within the documents a given feature can have to be used in the tfi-idf matrix. If the term is in greater than 80% of the documents it probably cares little meanining (in the context of film synopses)
<li> min_idf: this could be an integer (e.g. 5) and the term would have to be in at least 5 of the documents to be considered. Here I pass 0.2; the term must be in at least 20% of the document. I found that if I allowed a lower min_df I ended up basing clustering on names--for example "Michael" or "Tom" are names found in several of the movies and the synopses use these names frequently, but the names carry no real meaning.
<li> ngram_range: this just means I'll look at unigrams, bigrams and trigrams. See [n-grams](http://en.wikipedia.org/wiki/N-gram)
</ul>
"""

# Commented out IPython magic to ensure Python compatibility.
#texts = pickle.load(open(params['input_filename'], "rb" ))
df = pd.read_csv(params['inputfile'])
texts = df[params['column_to_process']].tolist()


# load nltk's SnowballStemmer as variabled 'stemmer'
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer(params['lang'])
print(">>>>>>>>>> STEAMER LOADED <<<<<<<<<<<<<")
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


from sklearn.feature_extraction.text import TfidfVectorizer
print(">>>>>>>>>> TFIDF PROCESS <<<<<<<<<<<<<")

tfidf_vectorizer = TfidfVectorizer(max_df=params['max_df'], max_features=params['max_features'], min_df=params['min_df'], stop_words=params['lang'], use_idf=params['idf'], tokenizer=tokenize_and_stem, ngram_range=(params['min_window_size'],params['max_window_size']))

#%time tfidf_matrix = tfidf_vectorizer.fit_transform(synopses)
tfidf_matrix = tfidf_vectorizer.fit_transform(texts)


print(tfidf_matrix.shape)

terms = tfidf_vectorizer.get_feature_names()


from sklearn.metrics.pairwise import cosine_similarity
dist = 1 - cosine_similarity(tfidf_matrix)

#serialization
pickle.dump(tfidf_matrix, open(params['matrix_outputfile'], "wb" ))

pickle.dump(dist, open(params['dist_outputfile'], "wb" ))
print(">>>>>>>>>> PROCESS FINISHED <<<<<<<<<<<<<")

#pickle.dump(terms, open(params['terms_outputfile'], "wb" ))