import pandas as pd

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
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from scipy.stats.stats import pearsonr

#plot
from matplotlib import pyplot as plt
import sys

# PARAMETERS #
inputpath="./"
outputpath="./"


#parameters from script
if len(sys.argv)>1:
    inputpath=sys.argv[1] +"/"
    outputpath=sys.argv[2]



#load preprocessed data

X_train = pickle.load( open(inputpath+"xtrain.pkl", "rb" ) )
X_test =pickle.load( open(inputpath+ "xtest.pkl", "rb" ) ) 
y_train=pickle.load( open(inputpath+ "ytrain.pkl", "rb" ) )
y_test=pickle.load( open(inputpath+ "ytest.pkl", "rb" ) )




model_naive = GaussianNB()
model_naive.fit(X_train, y_train) #entrenamiento

#y_probNaive = model_naive.predict_proba(X_test)[:,1] # This will give you positive class prediction probabilities  
#y_predNaive = np.where(y_probNaive > 0.5, 1, 0) # This will threshold the probabilities to give class predictions.
#model_naive.score(X_test, y_predNaive)


y_predNaive = model_naive.fit(X_train, y_train).predict(X_test)

matrixNaive = confusion_matrix(y_test, y_predNaive)
#matrixNaive


#naiveAccuracy = accuracy_score(y_test,y_predNaive)
naiveMSE=mean_squared_error(y_test, y_predNaive)
naiveRMSE = mean_squared_error(y_test, y_predNaive,squared=False)
naiveMAE = mean_absolute_error(y_test, y_predNaive)
naiver= pearsonr(y_predNaive,y_test)

precisionNaive, recallNaive, f1Naive, supportNaive =precision_recall_fscore_support(y_test,y_predNaive,average='weighted')

scoresNaive = cross_val_score(model_naive, X_train, y_train, cv=10, scoring='accuracy')

naiveAccuracy = scoresNaive.mean()


f = open(outputpath +"RESULT_NB.txt","a")
f.write("RESULTS OF EVALUATING Naive Bayes\n")
f.write("\nMSE:"+repr(naiveMSE))
f.write("\nRMSE:"+repr(naiveRMSE))
f.write("\nMAE:"+repr(naiveMAE))
f.write("\nPearson:"+repr(naiver))
f.write("\nAccuracy:"+repr(naiveAccuracy))
f.write("\nprecision:"+repr(precisionNaive))
f.write("\nrecall:"+repr(recallNaive))
f.write("\nf1:"+repr(f1Naive))
f.write("\nSupport:"+repr(supportNaive))
f.write("\n\nConfusion matrix:\n")
f.write(repr(matrixNaive))

f.close()

# save the model to disk
filename = '%sNaiveBayes.pkl' %(outputpath)
pickle.dump(model_naive, open(filename, 'wb'))
 