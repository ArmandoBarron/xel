import sys
import os
import time
import pandas as pd
import json
import re
import numpy as np
from math import *

"""
python3 App.py cancer_infantil_00_14.csv output.csv "x=19;print(19)" ""

"""
import logging #logger
logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()

def FormatCommand(command):

        while True:
                start = command.find("{") + 1
                if start==0: #given that -1 + 1 = 0
                        break
                end = command.find("}", start)
                if start>end:
                        return None
                parameter_found = command[start:end]

                ########## REPLACE PARAMS FOUND #############
                command = command.replace("{%s}" % (parameter_found),"@DF_data['%s']" % parameter_found)
        return command

def fillna_if_not_exists(df, column_name):
    if column_name not in df.columns:
        df[column_name] = None
    return df

def add_column_from_string(df, string):
    # Extraer las expresiones separadas por ';'
    expressions = string.split(';')
    
    for expression in expressions:
        # Extraer la condición y la expresión de cada expresión
        matches = re.findall(r'if\s+(.*?)\s*:\s*(.*)', expression)
        
        if matches:
            condition, expression = matches[0]
            condition = condition.strip()
            expression = expression.strip()
            
            # Extraer el nombre de la columna del lado izquierdo de la expresión
            column_name = re.findall(r'(\w+)\s*=', expression)[0]
            
            # Crea una función lambda que evalúa la expresión
            #eval_expression = lambda row: eval(expression)
            
            # Utiliza numpy.where() para aplicar la condición y la expresión
            fillna_if_not_exists(df,column_name)

            df[column_name].where(~df.eval(condition), df.eval(expression)[column_name],inplace=True)
        else:
            print("no condition",expression)
            if expression != "":
                df.eval(expression,inplace=True)
    return df


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
exec_code= sys.argv[3].split(";")  #query to process separated by;
query_list= sys.argv[4] #query to process separated by;
query_filt_list= sys.argv[5].split(";") #query to process separated by;

dataset = pd.read_csv(data_path)
"""
output_path="out.csv"
DF_data = pd.DataFrame({'sexo': ['Hombre', 'Mujer', 'Hombre', 'Mujer'],
                   'casos': [10, 5, 15, 8],
                   'poblacionHombre': [100, 200, 150, 300],
                   'poblacionMujer': [120, 180, 170, 250]})
query_list = "if sexo == 'Hombre' | sexo=='Mujer' : Tasa=casos/poblacionHombre;"
"""



# ==============================================================
#for exec (enviroment)
for q in exec_code:
        exec(q)

# for eval
q = FormatCommand(query_list)
if q != "":
        dataset = add_column_from_string(dataset,q)

#for query
for q in query_filt_list:
        q = FormatCommand(q)
        if q != "":
                dataset = dataset.query(q)

dataset.to_csv(output_path,index=False)



