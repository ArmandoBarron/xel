import sys
import os
import json

import pandas as pd
import numpy as np
from scipy import stats

def validate_int(val,defult_value=0):
    if val != "" and val!="-":
        return int(val)
    else:
        return defult_value

def validate_string(val,defult_value=""):
    if val != "" and val!="-":
        return val
    else:
        return defult_value

def validate_numeric(val):
    if val.lstrip('-').isdigit(): # es un numero entero
        return int(val)
    else:
        try: #verificar si es float
            a =float(val)
            return a
        except ValueError: # no es, entonces no es un numero
            return val


def VerifyRule(dataset, column, variable,proceso,operador,valornumerico):
    if proceso =="corr":
        result = dataset[column].corr(dataset[variable])
    if proceso =="cov":
        result = dataset[column].cov(dataset[variable])

    if_satisfies_rule = False
    if operador=="<":
        if_satisfies_rule =  result < float(valornumerico)
    if operador==">":
        if_satisfies_rule =  result > float(valornumerico)
    if operador=="InRange":
        init,end = valornumerico.split("to")
        if_satisfies_rule =  result > float(init) and result < float(end)
    if operador=="OutRange":
        init,end = valornumerico.split("to")
        if_satisfies_rule =  result < float(init) or result > float(end)

    return if_satisfies_rule

data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns =sys.argv[3].split(",") # c1,c2,c3
rules= sys.argv[4].split(",")  #lista de reglas [variable::proceso::operador::valornumerico, variable::proceso::operador::valornumerico]
logical_operator= sys.argv[5] #and, or
action =sys.argv[6] # keep, drop

DF_data = pd.read_csv(data_path)
columns_to_drop = []
for col in columns:
    rules_results = []
    for rule in rules:
        rule = rule.split("::")
        if len(rule)==4:
            variable,proceso,operador,valornumerico = rule
        elif len(rule==3):
            variable = col
            proceso,operador,valornumerico = rule
        else:
            exit(1)
        rules_results.append(VerifyRule(DF_data,col,variable,proceso,operador,valornumerico))

    if col == variable:
        pass
    else:
        if logical_operator == "and":
            if_column = all(rules_results)
        if logical_operator == "or":
            if_column = any(rules_results)
        
        print("%s : %s" %(col,if_column))

        if if_column:
            if action=="drop":
                columns_to_drop.append(col)
        else:
            if action=="keep":
                columns_to_drop.append(col)


### drop columns ###

DF_data = DF_data.drop(columns=columns_to_drop)


DF_data.to_csv(output_path,index=False)


## example
#  python3 .\Filtercolumn.py .\Suic_Medio_Derhab_tasasporsexo.csv out.csv "suicAhogamiento,suicAhorcamiento,suicArma_fuego,anio,pob_00_04,tasa_suic,tasa_suic10_14,tasa_suic30_34" "tasa_suic::corr::>::-0.8,tasa_suic::corr::OutRange::0to.7" "and" "keep"

