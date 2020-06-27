#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for
import json

import numpy as np
import pandas as pd
import time

app = Flask(__name__)


def NAN_format(replacment_list,df):
    for value in replacment_list:
        df.replace(value, np.nan, inplace=True)
    return df

@app.route('/')
def prueba():
    return "Data tools Service"

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


@app.route('/transform/group', methods=['POST'])
def group_data():
    message = request.get_json()
    data = message['data']
    DF_data = pd.DataFrame.from_records(data) #pandas dataframe with all data
    group = message['group']
    variable = message['variable']
    group_by = message['group_by']

    if group_by == "median": DF_data = DF_data.groupby(group, as_index=False)[variable].median()
    elif group_by == "mean": DF_data = DF_data.groupby(group, as_index=False)[variable].mean()
    elif group_by == "mode": DF_data = DF_data.groupby(group, as_index=False)[variable].mode()
    return json.dumps({"status": "OK" , "result": json.loads(DF_data.to_json(orient='records'))})

@app.route('/transform/melt', methods=['POST'])
def mealt_data(id_vars=[], var_name="", value_name=""):
    message = request.get_json()
    DF_data = message['data']
    DF_data = pd.DataFrame.from_records(DF_data) #pandas dataframe with all data
    id_vars = message['id_vars']
    var_name=message['var_name']
    value_name= message['value_name']
    DF_data = DF_data.melt(id_vars=id_vars,var_name=var_name,value_name=value_name)
    return json.dumps({"status": "OK" , "result": json.loads(DF_data.to_json(orient='records'))})

@app.route('/cleaning/basic', methods=['POST'])
def Basic_cleaning(columns='all',ReplaceWithNa=["NA","NAN","NaN","None"],DropNa=None,NaReaplace="mode",DataTypes=[]):
    #DropNA={"how":"all","tresh":3,subset="station_name"}
    message = request.get_json()
    data = message['data']
    DF_data = pd.DataFrame.from_records(data) #pandas dataframe with all data

    if 'DataTypes' in message: DataTypes = message['DataTypes']#filter by index (mean)
    if 'columns' in message: columns = message['columns'] #filter by index (mean)

    if 'ReplaceWithNa' in message: ReplaceWithNa = message['ReplaceWithNa']
    if 'DropNa' in message: 
        DropNa = message['DropNa'] #drop na has priority
    if 'NaReaplace' in message: NaReaplace = message['NaReaplace'] #replacing Na's with this value

    # STEP 1.- replace values in list with NaN type
    DF_data= NAN_format(ReplaceWithNa,DF_data)

    # STEP 2.- drop or replace all Na Values
    if DropNa is not None:
        DF_data=DF_data.dropna(**DropNa)

    #NaReaplace= NaReaplace.lower()
    if columns == "all":
        if NaReaplace =="mode": DF_data= DF_data.fillna(DF_data.mode().iloc[0] )
        elif NaReaplace =="mean": DF_data= DF_data.fillna(DF_data.mean())
        elif NaReaplace == "interpolate": DF_data=  DF_data.interpolate(method ='linear')
        elif NaReaplace == "": pass
        else: DF_data= DF_data.fillna(NaReaplace)
    else:
        for col in columns:
            if NaReaplace =="mode": DF_data[col]= DF_data[col].fillna(DF_data[col].mode().iloc[0])
            elif NaReaplace =="mean": DF_data[col]= DF_data[col].fillna(DF_data[col].mean())
            elif NaReaplace == "interpolate": DF_data[col]= DF_data[col].interpolate(method ='linear') 
            elif NaReaplace == "": pass
            else: DF_data[col]= DF_data[col].fillna(NaReaplace)


    # STEP 4.- replace again
    DF_data= DF_data.replace(to_replace=np.nan, value=-99)

    # STEP 3.- fromating data types
    castall=False
    for value in DataTypes: 
        if value['column'] == "all":
            castall=True
            except_list = value['except']
            cast_type = value['type']
            break
        DF_data[value["column"]]=  DF_data[value["column"]].astype(value['type'])

    if castall == True:
        cols=[i for i in DF_data.columns if i not in except_list]
        for col in cols:
            DF_data[col]=DF_data[col].astype(cast_type)

    return json.dumps({"status": "OK" , "result": json.loads(DF_data.to_json(orient='records'))})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True) 