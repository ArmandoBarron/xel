import sys
import os
import time
import pandas as pd
"""
python3 App.py Alcaldias_contaminantes_Anual_geo_limpio_86-22.csv out.csv 'Clave,Alcaldia,Entidad,year,nombre' 'CO,NO,NO2,NOX,O3,PM10,PM25,PMCO,SO2' 'contamiantes'
"""


def validate_bool(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="0":
        return False
    else:
        return True
# app para elminar columnas, renombrarlas y otras que se me puedan llegar a ocurrir

data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path

group_by= sys.argv[3].split(",") #group_by
variables = sys.argv[4].split(",") #variables list
column_name = sys.argv[5] #new column name

DF_data = pd.read_csv(data_path)

DF_data = pd.melt(DF_data, 
            id_vars=group_by, 
            value_vars=variables, # list of days of the week
            var_name=column_name, 
            value_name='%s_value'% column_name)


DF_data.to_csv(output_path,index=False)



#print(DF_data)


