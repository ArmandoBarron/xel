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
svc_parameters = '{"gamma":"auto"}'


#parameters from script
if len(sys.argv)>1:
    inputpath=sys.argv[1] +"/"
    outputpath=sys.argv[2]
    svc_parameters = sys.argv[3]

print(svc_parameters)
new_svc_parameters = json.loads(svc_parameters)
#load preprocessed data

X_train = pickle.load( open(inputpath+"xtrain.pkl", "rb" ) )
X_test =pickle.load( open(inputpath+ "xtest.pkl", "rb" ) ) 
y_train=pickle.load( open(inputpath+ "ytrain.pkl", "rb" ) )
y_test=pickle.load( open(inputpath+ "ytest.pkl", "rb" ) )



clf = make_pipeline(StandardScaler(), SVC(**new_svc_parameters),verbose=True )


clf.fit(X_train, y_train)
y_predSVC = clf.predict(X_test)

#metrics
svcMSE=mean_squared_error(y_test, y_predSVC)
svcRMSE = mean_squared_error(y_test, y_predSVC,squared=False)
svcMAE = mean_absolute_error(y_test, y_predSVC)
svcr= pearsonr(y_predSVC,y_test)

precisionSVC, recallSVC, f1SVC, supportSVC =precision_recall_fscore_support(y_test,y_predSVC,average='weighted')

matrixSVC=confusion_matrix(y_test, y_predSVC)

#accuracy and loss
accuracySVC = accuracy_score(y_test, y_predSVC)

f = open(outputpath +"RESULT_SVC.txt","a")
f.write("RESULTS OF EVALUATING Support Vector Machines\n")
f.write("\nMSE:"+repr(svcMSE))
f.write("\nRMSE:"+repr(svcRMSE))
f.write("\nMAE:"+repr(svcMAE))
f.write("\nPearson:"+repr(svcr))
f.write("\nAccuracy:"+repr(accuracySVC))
f.write("\nprecision:"+repr(precisionSVC))
f.write("\nrecall:"+repr(recallSVC))
f.write("\nf1:"+repr(f1SVC))
f.write("\nSupport:"+repr(supportSVC))
f.write("\n\nConfusion matrix:\n")
f.write(repr(matrixSVC))
f.close()

# save the model to disk
filename = '%sSVC_model.pkl' %(outputpath)
pickle.dump(clf, open(filename, 'wb'))
 