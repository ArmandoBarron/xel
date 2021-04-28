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
from keras.optimizers import SGD

import sys



# PARAMETERS #
inputpath="./"
outputpath="./"
ep_list= "10" #epochs
bsize_list= "128" #batch_size

#parameters from script
if len(sys.argv)>1:
    inputpath=sys.argv[1] +"/"
    outputpath=sys.argv[2] +"/"
    ep_list = sys.argv[3]
    bsize_list = sys.argv[4]


ep_list = ep_list.split(",") 
bsize_list = bsize_list.split(",")


#load preprocessed data

X_train = pickle.load( open(inputpath+"xtrain.pkl", "rb" ) )
X_test =pickle.load( open(inputpath+ "xtest.pkl", "rb" ) ) 
y_train=pickle.load( open(inputpath+ "ytrain.pkl", "rb" ) )
y_test=pickle.load( open(inputpath+ "ytest.pkl", "rb" ) )

vocab_size = 68921

## iterate for all  the configurations

for ep in ep_list:
  for bsize in bsize_list:
    ep = int(ep)
    bsize = int(bsize)

    """# 3. Deep learning"""
    opt = SGD(lr=0.01)

    #defining DL architecture
    embedding_vector_length = 64 #embedding dimension
    model = Sequential(name="covidModel_v1") 
    model.add(Embedding(vocab_size, embedding_vector_length, input_length=250) )
    model.add(SpatialDropout1D(0.25))
    model.add(LSTM(50, dropout=0.5, recurrent_dropout=0.5))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid')) 
    model.compile(loss='binary_crossentropy',optimizer="adam", metrics=['accuracy'])  

    print(model.summary())

    plot_model(model, to_file=outputpath+'model.png')

    print(str(ep))
    print("batch size: "+str(bsize))

    filepath="DLModelEp"+str(ep)+"BS"+str(bsize)+".hdf5"

    checkpoint = ModelCheckpoint(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    """Training DL model"""


    history = model.fit(X_train, 
                        y_train, 
                        epochs=ep, 
                        batch_size=bsize,
                        validation_data=(X_test, y_test),callbacks=callbacks_list)

    #obtaining accuracy from test dataset
    test_loss, test_acc= model.evaluate(X_test,y_test)

    #get prediction vector
    predictions = model.predict(X_test)

    y_predDL = [0] * len(predictions)
    i=0
    for x in predictions:
      if x[0]>0.5:
        y_predDL[i]=1
      else: 
        y_predDL[i]=0
      i=i+1


    #confusion matrix
    matrix = confusion_matrix(y_test, y_predDL)
    matrix

    #get metrics
    precisionDL, recallDL, f1DL, supportDL =precision_recall_fscore_support(y_test,y_predDL,average='weighted')
    nnMSE=mean_squared_error(y_test, y_predDL)
    nnRMSE = mean_squared_error(y_test, y_predDL,squared=False)
    nnMAE = mean_absolute_error(y_test, y_predDL)
    nnr= pearsonr(y_predDL,y_test)
    nnRMSE


    f = open(outputpath +"RESULT_LSTM_ep-%s_bsize-%s.txt" %(str(ep),str(bsize)),"a")

    f.write("\n\nRESULTS OF EVALUATING LSTM Epocs"+str(ep)+"Batch Size"+str(bsize)+"\n")
    f.write("\nMSE:"+repr(nnMSE))
    f.write("\nRMSE:"+repr(nnRMSE))
    f.write("\nMAE:"+repr(nnMAE))
    f.write("\nPearson:"+repr(nnr))
    f.write("\nAccuracy:"+repr(test_acc))
    f.write("\nprecision:"+repr(precisionDL))
    f.write("\nrecall:"+repr(recallDL))
    f.write("\nf1:"+repr(f1DL))
    f.write("\nSupport:"+repr(supportDL))
    f.write("\n\nConfusion matrix:\n")
    f.write(repr(matrix))

    f.close()