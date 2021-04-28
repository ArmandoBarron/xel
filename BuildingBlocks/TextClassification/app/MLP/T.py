import pandas as pd
#nlp

# build models
#dl
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense, Dropout, SpatialDropout1D
from tensorflow.keras.layers import Embedding
from keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import plot_model
#bayes
from sklearn.naive_bayes import GaussianNB
#svc
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

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
from sklearn.metrics import classification_report
import json

import sys

# PARAMETERS #
inputpath="./"
outputpath="./"
ep_list= "10" #epochs
bsize_list= "128" #batch_size
network = '[{"units":250,"input_dim":250, "activation":"relu"},{"units":250,"kernel_initializer":"uniform", "activation":"relu"},{"units":1,"activation":"sigmoid"}]'

#parameters from script
if len(sys.argv)>1:
    inputpath=sys.argv[1] +"/"
    outputpath=sys.argv[2]
    ep_list = sys.argv[3]
    bsize_list = sys.argv[4]
    network = sys.argv[5]

print(network )
ep_list = ep_list.split(",") 
bsize_list = bsize_list.split(",")
network = json.loads(network) #list of dicts
#load preprocessed data

X_train = pickle.load( open(inputpath+"xtrain.pkl", "rb" ) )
X_test =pickle.load( open(inputpath+ "xtest.pkl", "rb" ) ) 
y_train=pickle.load( open(inputpath+ "ytrain.pkl", "rb" ) )
y_test=pickle.load( open(inputpath+ "ytest.pkl", "rb" ) )


"""Training MLP model"""


modelMLP = Sequential(name="covidMLP_v1")
for nw in network:
  modelMLP.add(Dense(**nw))
#modelMLP.add(Dense(250, kernel_initializer = 'uniform', activation='relu'))
#modelMLP.add(Dense(1, activation='sigmoid'))

for ep in ep_list:
  for bsize in bsize_list:
    ep = int(ep)
    bsize = int(bsize)
      # Compile model
    modelMLP.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


    history = modelMLP.fit(X_train, 
                        y_train, 
                        epochs=ep, 
                        batch_size=bsize,
                        validation_data=(X_test, y_test),verbose=True)



    #obtaining accuracy from test dataset
    test_lossMLP, test_accMLP= modelMLP.evaluate(X_test,y_test)


    predictionsMLP = modelMLP.predict(X_test)


    y_predMLP = [0] * len(predictionsMLP)
    i=0
    for x in predictionsMLP:
      if x[0]>0.5:
        y_predMLP[i]=1
      else: 
        y_predMLP[i]=0
      i=i+1

    mlpMSE=mean_squared_error(y_test, y_predMLP)
    mlpRMSE = mean_squared_error(y_test, y_predMLP,squared=False)
    mlpMAE = mean_absolute_error(y_test, y_predMLP)
    mlpr= pearsonr(y_predMLP,y_test)

    precisionMLP, recallMLP, f1MLP, supportMLP =precision_recall_fscore_support(y_test,y_predMLP,average='weighted')

    matrixMLP=confusion_matrix(y_test, y_predMLP)


    f = open(outputpath,"a")

    f.write("RESULTS OF EVALUATING MLP\n")
    f.write("\nMSE:"+repr(mlpMSE))
    f.write("\nRMSE:"+repr(mlpRMSE))
    f.write("\nMAE:"+repr(mlpMAE))
    f.write("\nPearson:"+repr(mlpr))
    f.write("\nAccuracy:"+repr(test_accMLP))
    f.write("\nprecision:"+repr(precisionMLP))
    f.write("\nrecall:"+repr(recallMLP))
    f.write("\nf1:"+repr(f1MLP))
    f.write("\nSupport:"+repr(supportMLP))
    f.write("\n\nConfusion matrix:\n")
    f.write(repr(matrixMLP))

    f.close()