import os,json,gzip
import requests as api #for APIs request
import pandas as pd
from base64 import b64decode
from zipfile import ZipFile, ZIP_DEFLATED
from base64 import b64encode,b64decode

"""

#Deep Learning
dlAction = 'C'

#CNN
columnsToConsider = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
trainSize = '80'
epochsNumber = '10'
classColumn = 'rh'
lossFunction = 'categorical_crossentropy'
evaluationMetric = 'accuracy'

cParams = {'columns':columnsToConsider,
           'trainSize':trainSize,
           'classColumn':classColumn,
           'epoch':epochsNumber,
           'lossFunction':lossFunction,
           'metric':evaluationMetric}

#LSTM
columnsToConsider = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
trainSize = '80'
epochsNumber = '20'
classColumn = 'rh'
lossFunction = 'categorical_crossentropy'
evaluationMetric = 'accuracy'

lParams = {'columns':columnsToConsider,
           'trainSize':trainSize,
           'classColumn':classColumn,
           'epoch':epochsNumber,
           'lossFunction':lossFunction,
           'metric':evaluationMetric}

#RNN
columnsToConsider = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
trainSize = '80'
epochsNumber = '10'
classColumn = 'rh'
lossFunction = 'categorical_crossentropy'
evaluationMetric = 'accuracy'

rParams = {'columns':columnsToConsider,
           'trainSize':trainSize,
           'classColumn':classColumn,
           'epoch':epochsNumber,
           'lossFunction':lossFunction,
           'metric':evaluationMetric}


dlParams = {'C_params':cParams, 'L_params':lParams, 'R_params':rParams}

"""

"""
#Preprocesamiento
dlAction = ['INOS']

#Work Params
imputationMethod = "mean"

#Columns to process
numericColumns = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'


iParams = {'columns':numericColumns, 'method':imputationMethod}
nParams = {'columns':numericColumns}
oParams = {'columns':numericColumns}
sParams = {}
preprocessingParams = {'I':iParams, 'N':nParams, 'O':oParams, 'S':sParams}


#read data
data = pd.read_csv("content.csv")
data = data.to_json(orient='records')

ToSend = {'data':data,'actions':dlAction,'params':preprocessingParams}

ToSend=json.dumps(ToSend)

url = 'http://localhost:25000/execute/preprocessing'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
result = api.post(url, data=ToSend,headers=headers)
RES = result.json()
print(RES)


"""
"""
###### TPS SERVICES #####
# dependiendo de los parametros se llama a un servicio diferente
params ={"service":"cleaningtools","columns":"all","ReplaceWithNa":['None',-99,-99.0,'NaN','nan'],"NaReaplace":"mean"} #calling the cleaning service
params = {"service":"clustering","k":3,"alghoritm":"kmeans","variables":"presion_barometrica"} #calling the clustering service
params ={"service":"ANOVA","variables":"vel_viento,temperatura,humedad,presion_barometrica","method":"kendall"} #calling ANOVA service
params ={"service":"transform", "process":"group","group":['estacion'],"variable":["temperatura","humedad"],"group_by":"median" } #service to transform data (group in this case)
#params ={"service":"graphics","kind":"hist","variables":['temperatura','humedad'],"alpha":.25,"bins":20 } #calling graphic service

#there is also a jacard and a validate clustering service, but i need labeled data for test it.


#read data
data = pd.read_csv("content.csv")
data = data.to_json(orient='records')

ToSend = {'data':data,'params':params} #no actions, so it will taken the default application A

ToSend=json.dumps(ToSend)

url = 'http://localhost:25000/execute/TS'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
result = api.post(url, data=ToSend,headers=headers)
RES = json.loads(result.json())
print(RES)


#el resultado de el servicio de grafica se puede escribir en disco, pero hay que decodificar los datos
#siempre es un archivo png
#with open("grafica.png","wb") as file:
#        file.write(b64decode(RES['data'].encode('utf-8')))
"""

    
"""

 #### executing a DAG

#textpreprocessingAction = 'T'
textprocessingAction = 'R'
#imputationMethod = "mean"
#numericColumns = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
#numericColumns = 'radiacion_solar'


#iParams = {'columns':numericColumns, 'method':imputationMethod,"SAVE_DATA":False}
#nParams = {'columns':numericColumns,"SAVE_DATA":False}
#oParams = {'columns':numericColumns,"SAVE_DATA":False}
#sParams = {}
sParams = {'lang':'english', 'column_to_process':'synopsis',"SAVE_DATA":False}

tParams = {'column_to_process':'synopsis', 'lang':'english', 'max_df':0.8,'max_features':200000,'min_df':0.2, 'idf':True, 'min_window_size':1,'max_window_size':3,"SAVE_DATA":False}


lParams = {'lang':'english', 'column_to_process':'synopsis',"SAVE_DATA":False}

kParams = {'representation_filename':'01-tfidf_matrix.pkl',
          'num_clusters':5,
          'input_frame_filename':'synopses.csv',"SAVE_DATA":False}

hParams = {'input_distance_filename':'05-dist.pkl',
          'input_frame_filename':'synopses.csv',
          'identifier_column':'title',
          "SAVE_DATA":False
          }

rParams = {'clustered_dataframe_filename':'04-frame.csv',
          'cluster_column_name':'cluster',
          'identifier_column':'title',
          'input_distance_filename':'05-dist.pkl',
          "SAVE_DATA":False}

textpreprocessingParams = {'T':tParams, "SAVE_DATA":False}
textprocessingParams = {'R':rParams, "SAVE_DATA":False}

'''
DAG  = [{
    "id":"s1",
    "service":"preprocessing",
    "actions":preprocessingAction,
    "childrens":[
        {"id":"s2","service":"TS","childrens":[],"params":{"service":"ANOVA","variables":"vel_viento,temperatura,humedad,presion_barometrica","method":"kendall","SAVE_DATA":False}},
        {"id":"s3","service":"TS","childrens":[],"params":{"service":"clustering","k":3,"alghoritm":"kmeans","variables":"presion_barometrica","SAVE_DATA":False}}
        ],
    "params":preprocessingParams
    }]

'''
DAG  = [{
    "id":"s1",
    "service":"text_processing",
    "actions":textprocessingAction,
    "params":textprocessingParams
    }]

DAG = json.dumps(DAG)


#read data
#data = pd.read_csv("synopses.csv")
#print(data)
#data = json.loads(data.to_json(orient='records'))
#print(data)

with ZipFile("data.zip", 'w') as zipObj:
    zipObj.write("05-dist.pkl", "05-dist.pkl")
    zipObj.write('04-frame.csv', '04-frame.csv')


with open("data.zip","rb") as file:
    data = b64encode(file.read()).decode()
    file.close()


ToSend = {'data':json.dumps({'data':data,'type':'zip'}),'DAG':DAG} #no actions, so it will taken the default application A


ToSend=json.dumps(ToSend)
"""

textClassificationAction = 'S'
pParams = {'labelColumn':'Sentiment',
           'contentColumn':'OriginalTweet',
           'objective':"Sentiment=='Positive'",
           "SAVE_DATA":False}

dParams = {'epoch':'1',
           'batch_size':'128',
           "SAVE_DATA":False}

nParams ={"SAVE_DATA":False}

sParams ={"SAVE_DATA":False}

mParams = {'epoch':'5',
           'batch_size':'32',
           "SAVE_DATA":False}

textClassificationParams = {'S':sParams, "SAVE_DATA":False}


DAG  = [{
    "id":"s1",
    "service":"text_classification",
    "actions":textClassificationAction,
    "params":textClassificationParams
    }]
DAG = json.dumps(DAG)

#data = pd.read_csv("CoronaNLP.csv",encoding="ISO-8859-1")
#print(data)
#data = json.loads(data.to_json(orient='records'))

with ZipFile("input/TextClassification/DL/data.zip", 'w') as zipObj:
    zipObj.write('input/TextClassification/DL/xtest.pkl','xtest.pkl')
    zipObj.write('input/TextClassification/DL/xtrain.pkl','xtrain.pkl')
    zipObj.write('input/TextClassification/DL/ytest.pkl', 'ytest.pkl')
    zipObj.write('input/TextClassification/DL/ytrain.pkl','ytrain.pkl')


with open("input/TextClassification/DL/data.zip","rb") as file:
    data = b64encode(file.read()).decode()
    file.close()
    

ToSend = {'data':json.dumps({'data':data,'type':'zip'}),'DAG':DAG} #no actions, so it will taken the default application A

ToSend=json.dumps(ToSend)

url = 'http://localhost:25000/executeDAG'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
result = api.post(url, data=ToSend,headers=headers)
print(result)

RES = result.json()
print(RES)
 
RN = RES['RN'] #get RN to monitoring

Notask = 1
while True:
    if Notask <=0: break
    url = 'http://localhost:25000/monitor/%s' % (RN)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = api.post(url,headers=headers)
    RES = result.json()
    print(RES)
    if RES['status'] == "OK":
        #print(RES['data'])
        print("DATA FOUNDED")
        print(RES['task'])
        Notask-=1
    else:
        print("nothing yet")





