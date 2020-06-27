import os,json
#Preprocesamiento
globalAction = 'ep'
preprocessingAction = 'INOS,INO,IN,I,ION,IO,OIN,OI,INS,IS,IONS,IOS,OINS,OIS'

#Work Params
imputationMethod = "mean"

#Columns to process
numericColumns = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'


iParams = {'T_numericColumns':numericColumns, 'T_imputationMethod':imputationMethod}
nParams = {'T_numericColumns':numericColumns}
oParams = {'T_numericColumns':numericColumns}
sParams = {}
preprocessingParams = {'IParams':iParams, 'NParams':nParams, 'OParams':oParams, 'SParams':sParams}
preprocessingParamString=json.dumps(preprocessingParams)

#os.system("python3 coordinator_middleware.py "+globalAction+" "+preprocessingAction+" '"+preprocessingParamString+"'")


#Deep Learning
globalAction= 'zd'
dlAction = 'CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR,CLR'

#CNN
columnsToConsider = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
trainSize = '80'
epochsNumber = '10'
classColumn = 'rh'
lossFunction = 'categorical_crossentropy'
evaluationMetric = 'accuracy'

cParams = {'T_columnsToConsider':columnsToConsider,
           'T_trainSize':trainSize,
           'T_classColumn':classColumn,
           'T_epochsNumber':epochsNumber,
           'T_lossFunction':lossFunction,
           'T_evaluationMetric':evaluationMetric}

#LSTM
columnsToConsider = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
trainSize = '80'
epochsNumber = '20'
classColumn = 'rh'
lossFunction = 'categorical_crossentropy'
evaluationMetric = 'accuracy'

lParams = {'T_columnsToConsider':columnsToConsider,
           'T_trainSize':trainSize,
           'T_classColumn':classColumn,
           'T_epochsNumber':epochsNumber,
           'T_lossFunction':lossFunction,
           'T_evaluationMetric':evaluationMetric}

#RNN
columnsToConsider = 'latitud,longitud,altitud,dir_rafaga,dir_viento,vel_rafaga,vel_viento,temperatura,humedad,presion_barometrica,precipitacion,radiacion_solar'
trainSize = '80'
epochsNumber = '10'
classColumn = 'rh'
lossFunction = 'categorical_crossentropy'
evaluationMetric = 'accuracy'

rParams = {'T_columnsToConsider':columnsToConsider,
           'T_trainSize':trainSize,
           'T_classColumn':classColumn,
           'T_epochsNumber':epochsNumber,
           'T_lossFunction':lossFunction,
           'T_evaluationMetric':evaluationMetric}


dlParams = {'CParams':cParams, 'LParams':lParams, 'RParams':rParams}

dlParamString=json.dumps(dlParams)
os.system("python3 coordinator_middleware.py "+globalAction+" "+dlAction+" '"+dlParamString+"'")

