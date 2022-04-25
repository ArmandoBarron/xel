import sys
import os
import time
import pandas as pd
import json

def validate_bool(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="0":
        return False
    else:
        return True
# app para elminar columnas, renombrarlas y otras que se me puedan llegar a ocurrir

data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path

if_delete = validate_bool(sys.argv[3])
if_rename = validate_bool(sys.argv[4])

variables = sys.argv[5].split(",") #variables list para eliminar
rename_dict = json.loads(sys.argv[6])


DF_data = pd.read_csv(data_path)


# =============== DELETE ===================
if if_delete:
        DF_data.drop(variables, axis=1, inplace=True)
# =============== RENAME ===================
if if_rename:
        DF_data.rename(rename_dict, axis = "columns", inplace = True)

DF_data.to_csv(output_path,index=False)



#print(DF_data)


