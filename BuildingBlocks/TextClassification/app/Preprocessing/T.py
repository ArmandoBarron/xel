import pandas as pd
from sys import argv
#nlp
import nltk
from nltk.corpus import stopwords
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
nltk.download('stopwords')
nltk.download('punkt')
stemmer = SnowballStemmer("english")
#preprocessing
from nltk.tokenize import word_tokenize
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
# build models
#dl
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense, Dropout, SpatialDropout1D
from tensorflow.keras.layers import Embedding
from keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import plot_model
#bayes
from sklearn.naive_bayes import GaussianNB
#for dumping
import pickle 
#evaluation
import sys

#plot
from matplotlib import pyplot as plt
 
"""# 1.Preprocessing"""
inputfile = argv[1] #path of the filename
outputpath=sys.argv[2] +"/"
label_column = argv[3] #name of the colum with the class 
text_column = argv[4] #name of the column with the text (e.g a tweet)
str_query  = argv[5] # query pandas "null"


tweet_df= pd.read_csv(inputfile, engine="python")
print(tweet_df[text_column])
#load stopwords
STOPWORDS = set(stopwords.words('english'))

#remove stopwords of 
tweet_df[text_column]= tweet_df[text_column].apply((lambda x: ' '.join([stemmer.stem(word) for word in x.split() if word not in STOPWORDS])))

#keep only certain columns
tweet_df = tweet_df[[label_column,text_column]]
tweet_df.head(10)

#filtter columns
#tweet_df.Sentiment.value_counts()
if text_column != "":
    tweet_df.query(str_query,inplace=True)

#delete stopwords and apply stemming

"""# 2.Preparation and data split"""

# convert label to numeric
labels_list = tweet_df[label_column].factorize() #y

#tokenization and data encoding (word embedding)
tweet = tweet_df[text_column].values
tokenizer = Tokenizer(num_words=8000)
tokenizer.fit_on_texts(tweet)
vocab_size = len(tokenizer.word_index) + 1
encoded_docs = tokenizer.texts_to_sequences(tweet)
padded_sequence = pad_sequences(encoded_docs, maxlen=250) #data

#print(tokenizer.word_index)
print(tweet[0])
print(encoded_docs[0])
print(padded_sequence[0])

#training and testing data
X_train, X_test, y_train, y_test = train_test_split(padded_sequence, labels_list[0], test_size = 0.2, random_state=42)


pickle.dump(X_train, open(outputpath+ "xtrain.pkl", "wb" ) )
pickle.dump(X_test, open( outputpath+ "xtest.pkl", "wb" ) )
pickle.dump(y_train, open(outputpath+  "ytrain.pkl", "wb" ) )
pickle.dump(y_test, open( outputpath+ "ytest.pkl", "wb" ) )