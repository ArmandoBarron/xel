from netCDF4 import Dataset
import numpy as np
import pandas as pd
import json
import glob
import logging #logger
import os

#CONFIGPATH= "/home/robot/Escritorio/Projects/TESIS/TEST/"
#SCHEMAPATH= "/home/robot/Escritorio/Projects/TESIS/TEST/"
CONFIGPATH= os.getenv('CONFIGPATH') 
SCHEMAPATH= os.getenv('SCHEMAPATH')


Log = logging.getLogger()

#----------------INICIO DEL PROGRAMA------------------------

#----------------INICIO DEL PROGRAMA------------------------

dataset = Dataset('wrfout_d01_2019-11-22_12:00:00') #se abre el archivo
Variables = []
print(dataset.variables.keys())

#print(dataset.dimensions.keys())
DIM = dict()
print(dataset.variables['SST'][0,3,0])
for d in dataset.dimensions:
    DIM[d] = dataset.dimensions[d].size
    #for v_d in range(0:DIM[d]):# all values in the dim

print(dataset.variables['SST'][0,0:1,range(0,5)])

for v in dataset.variables:
    variable = dataset.variables[v]
    v_dim = variable.dimensions
        


    
    
    #print(i,dataset.variables[i].shape)
    #print(i, dataset.variables[i].dimensions)


    #d = np.array(nc.variables['precip'], dtype=type(nc.variables))
    #print(d[:,23.75,91.25])

exit(1)
#OBTENER LOS DATOS DE CADA VARIABLE
lat = dataset.variables["lat"][:]
lon = dataset.variables["lon"][:]
nc_time = dataset.variables["time"][:]
t_unit = dataset.variables["time"].units
HNORAIN= dataset.variables["HOURNORAIN"][:] #time-during_an_hour_with_no_precipitation
Temp_MAX=dataset.variables["T2MMAX"][:]
Temp_MIN=dataset.variables["T2MMIN"][:]
Temp_MEAN=dataset.variables["T2MMEAN"][:]
Prec_MAX =dataset.variables["TPRECMAX"][:] # total_precipitation
#obtener indices de lat y lon
idx_lat=np.nonzero(lat)[0]
idx_lon=np.nonzero(lon)[0]
idx_time=np.nonzero(nc_time)[0]
#print idx_lon, idx_lat
#PrintVariables()
if not os.path.exists("./volumen/Parsing"):
        os.makedirs("./volumen/Parsing")

        for t in idx_time: #por cada valor de tiempo
                for i in idx_lat: #por cada valor de latitud
                        for j in idx_lon: #por cada valor de longitud
                                values =[]
                                values.append(nc_time[t]) #tiempo
                                values.append(lat[i]) #latitud
                                values.append(lon[j]) #longitud
                                values.append(HNORAIN[t,i,j])
                                values.append(Temp_MAX[t,i,j])
                                values.append(Temp_MIN[t,i,j])
                                values.append(Temp_MEAN[t,i,j])
                                values.append(Prec_MAX[t,i,j])
                                writer.writerow(values)  #escribir linea
