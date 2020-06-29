import os,json
import requests as api #for APIs request
import pandas as pd
from base64 import b64decode

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


 #### executing a DAG

preprocessingAction = 'INO'
imputationMethod = "mean"
numericColumns = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'


iParams = {'columns':numericColumns, 'method':imputationMethod}
nParams = {'columns':numericColumns}
oParams = {'columns':numericColumns}
sParams = {}
preprocessingParams = {'I':iParams, 'N':nParams, 'O':oParams, 'S':sParams}


DAG  = [{
    "id":"s1",
    "service":"preprocessing",
    "actions":preprocessingAction,
    "childrens":[
        {"id":"s2","service":"TS","childrens":[],"params":{"service":"ANOVA","variables":"vel_viento,temperatura,humedad,presion_barometrica","method":"kendall"}},
        {"id":"s3","service":"TS","childrens":[],"params":{"service":"clustering","k":3,"alghoritm":"kmeans","variables":"presion_barometrica"}}
        ],
    "params":preprocessingParams
    },
]


#read data
data = pd.read_csv("content.csv")
data = data.to_json(orient='records')

ToSend = {'data':data,'DAG':DAG} #no actions, so it will taken the default application A

ToSend=json.dumps(ToSend)

url = 'http://localhost:25000/executeDAG'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
result = api.post(url, data=ToSend,headers=headers)
RES = result.json()


RN = RES['RN'] #get RN to monitoring

Notask = 3
while True:
    if Notask <=0: break
    url = 'http://localhost:25000/monitor/%s' % (RN)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = api.post(url,headers=headers)
    RES = result.json()
    if RES['status'] == "OK":
        print(RES['data'])
        print("DATA FOUNDED")
        print(RES['task'])
        Notask-=1
    else:
        print("nothing yet")

