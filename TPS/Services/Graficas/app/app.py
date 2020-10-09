from flask import Flask, request, redirect, Response, send_file
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.mplot3d import Axes3D
#from flask_cors import CORS
import io
import json
import os
import zipfile
import pathlib
import datetime
from datetime import date
import pandas as pd
import numpy as np
import seaborn as sns



app = Flask(__name__)
#CORS(app)

app.config['JSON_AS_ASCII'] = False

FOLDER = 'static/images'

def Numeric(df):
    return df.apply(pd.to_numeric)

def clean_array(df,variables):
    df.replace('None', np.nan, inplace=True)
    df.replace('NA', np.nan, inplace=True)
    df.replace('Na', np.nan, inplace=True)
    df.replace('null', np.nan, inplace=True)
    df.replace('Null', np.nan, inplace=True)

    for v in variables: #cleaning from nulls all variables to graph
        df[v] = Numeric(df[v])
        df[v] = df[v].fillna(df[v].mean()) #llenar con la media

    return df


def clean_arrays(arr1, arr2):

    clean1 = []
    clean2 = []

    for i in range(len(arr1)):
        e1 = arr1[i]
        e2 = arr2[i]
        if (e1 != 'Null' and e1 != 'null' and e1 != 'NA') and (e2 != 'Null' and e2 != 'null' and e2 != 'NA'):
            clean1.append(e1)
            clean2.append(e2)

    res = [clean1, clean2]
    return res

@app.route('/')
def init():
    return 'It works!'

@app.route('/scatter', methods=['POST'])
def get_scatter():
    """
    json with the next parameters:

    data: list of records
    variables: columns to graphicate (max 3. there are just 3 dimensions)
    labels: column with labels (clusters, class, etc.) 
    """

    json_file = request.get_json(force=True)
    data = pd.DataFrame.from_records(json_file['data']) #Dataframe
    variables = json_file['variables'] #list
    if 'labels' in json_file:
        labels = json_file['labels']
        color_labels = data[labels].unique()
    else:
        labels= "group_labels"
        data['group_labels'] = 'FALSE'
        color_labels = data[labels].unique()


    if 'point_label' in json_file:
        point_label = json_file['point_label']
    else:
        point_label= None

    dimensions = len(variables)
    clean_array(data,variables) #cleaning arrarys
    print(dimensions)
    if dimensions <=2:
        X = variables[0]
        Y = variables[1]
        rgb_values = sns.color_palette("Set2", 8)
        # Map label to RGB
        color_map = dict(zip(color_labels, rgb_values))
        ax1=None
        for lb in color_labels:
            d = data.loc[data[labels] == lb]
            ax1 = d.plot(kind='scatter', x=X, y=Y, color=d[labels].map(color_map),ax=ax1,label="Cluster %s" % lb )    
            
            #give the labels to each point
            if point_label is not None:
                for x_label, y_label, label in zip(d[X], d[Y], d[point_label]):
                    ax1.annotate(label,(x_label, y_label))
        
        ax1.set_ylabel(Y)
        ax1.set_xlabel(X)

    if dimensions >=3:
        X = variables[0]
        Y = variables[1]
        Z = variables[2]
        rgb_values = sns.color_palette("Set2", 8)
        # Map label to RGB
        color_map = dict(zip(color_labels, rgb_values))
        
        ax1=None
        threedee = plt.figure().gca(projection='3d')

        for lb in color_labels:
            d = data.loc[data[labels] == lb]
            threedee.scatter(d[X], d[Y], d[Z],color=d[labels].map(color_map),label="Cluster %s" % lb)

            #give the labels to each point
            if point_label is not None:
                for x_label, y_label, z_label, label in zip(d[X], d[Y], d[Z], d[point_label]):
                    threedee.text(x_label, y_label, z_label, label)

        threedee.set_xlabel(X)
        threedee.set_ylabel(Y)
        threedee.set_zlabel(Z)
        threedee.legend()
    today = date.today()

    graphic_name = "scatter_%sd_%s" %( dimensions,today.strftime("%d-%m-%Y"))
    fileDir = FOLDER + '/' + graphic_name +".png"

    if os.path.isfile(fileDir):
        os.remove(fileDir)   # Opt.: os.system("rm "+strFile)
    plt.savefig(fileDir)
    return json.dumps({"status":"ok","file":graphic_name})

@app.route('/line', methods=['POST'])
def get_line():
    """
    json with the next parameters:

    data: list of records
    variables: columns to graphicate (max 3. there are just 3 dimensions)
    labels: column with labels (clusters, class, etc.) 
    """
    json_file = request.get_json(force=True)
    data = pd.DataFrame.from_records(json_file['data']) #Dataframe
    variables = json_file['variables'] #list
    if 'labels' in json_file:
        labels = json_file['labels']
        color_labels = data[labels].unique()
    else:
        labels= "group_labels"
        data['group_labels'] = 'FALSE'
        color_labels = data[labels].unique()

    dimensions = len(variables)
    data= clean_array(data,variables) #cleaning arrarys
    print(dimensions)
    if dimensions <=2:
        X = variables[0]
        Y = variables[1]
        rgb_values = sns.color_palette("Set2", 8)
        # Map label to RGB
        color_map = dict(zip(color_labels, rgb_values))
        ax1=None
        for lb in color_labels:
            d = data.loc[data[labels] == lb]
            ax1 = d.plot(kind='line', x=X, y=Y, color=d[labels].map(color_map),ax=ax1,label="Cluster %s" % lb )    
        
        
        ax1.set_ylabel(Y)
        ax1.set_xlabel(X)
    if dimensions >=3:
        X = variables[0]
        Y = variables[1]
        Z = variables[2]
        rgb_values = sns.color_palette("Set2", 8)
        # Map label to RGB
        color_map = dict(zip(color_labels, rgb_values))
        
        ax1=None
        threedee = plt.figure().gca(projection='3d')

        for lb in color_labels:
            d = data.loc[data[labels] == lb]
            threedee.plot(d[X], d[Y], d[Z],color=d[labels].map(color_map).iloc[0],label="Cluster %s" % lb)

        threedee.set_xlabel(X)
        threedee.set_ylabel(Y)
        threedee.set_zlabel(Z)
        threedee.legend()
    today = date.today()

    graphic_name = "line_%sd_%s" %( dimensions,today.strftime("%d-%m-%Y"))
    fileDir = FOLDER + '/' + graphic_name +".png"

    if os.path.isfile(fileDir):
        os.remove(fileDir)   # Opt.: os.system("rm "+strFile)
    plt.savefig(fileDir)
    return json.dumps({"status":"ok","file":graphic_name})

@app.route('/bar', methods=['POST'])
def get_gral():
    """
    json with the next parameters:

    data: list of records
    variables: columns to graphicate (max 3. there are just 3 dimensions)
    labels: column with labels (clusters, class, etc.) 
    """
    json_file = request.get_json(force=True)
    data = pd.DataFrame.from_records(json_file['data']) #Dataframe
    variables = json_file['variables'] #list
    if 'labels' in json_file:
        labels = json_file['labels']
        color_labels = data[labels].unique()
    else:
        labels= "group_labels"
        data['group_labels'] = 'FALSE'
        color_labels = data[labels].unique()

    dimensions = len(variables)
    clean_array(data,variables) #cleaning arrarys
    print(dimensions)
    if dimensions <=2:
        X = variables[0]
        Y = variables[1]
        # Map label to RGB
        ax= data.plot(kind='bar', x=X, y=Y,rot=0)
        ax.set_ylabel(Y)
        ax.set_xlabel(X)

    if dimensions >=3:
        X = variables[0]
        Y = variables[1]
        Z = variables[2]
        rgb_values = sns.color_palette("Set2", 8)
        # Map label to RGB
        color_map = dict(zip(color_labels, rgb_values))
        
        ax1=None
        threedee = plt.figure().gca(projection='3d')

        for lb in color_labels:
            d = data.loc[data[labels] == lb]
            threedee.bar(d[X], d[Y], d[Z],color=d[labels].map(color_map).iloc[0],label="Cluster %s" % lb)

        threedee.set_xlabel(X)
        threedee.set_ylabel(Y)
        threedee.set_zlabel(Z)
        threedee.legend()
    today = date.today()

    graphic_name = "bar_%sd_%s" %( dimensions,today.strftime("%d-%m-%Y"))
    fileDir = FOLDER + '/' + graphic_name +".png"

    if os.path.isfile(fileDir):
        os.remove(fileDir)   # Opt.: os.system("rm "+strFile)
    plt.savefig(fileDir)
    return json.dumps({"status":"ok","file":graphic_name})


@app.route('/hist', methods=['POST'])
def get_hist():
    """
    json with the next parameters:

    data: list of records
    variables: columns to graphicate (max 3. there are just 3 dimensions)
    labels: column with labels (clusters, class, etc.) 
    """
    json_file = request.get_json(force=True)
    data = pd.DataFrame.from_records(json_file['data']) #Dataframe
    if 'variables' in json_file:
        variables = json_file['variables'] #list
    else:
        variables = data.columns

    if 'alpha' in json_file:
        alp = float(json_file['alpha']) #list
    else:
        alp = .25

    if 'bins' in json_file:
        bins = int(json_file['bins']) #list
    else:
        bins = 25

    data= clean_array(data,variables) #cleaning arrarys

    data[variables].plot.hist(grid=False, figsize=(12,8),alpha=alp,bins=bins)
    today = date.today()

    graphic_name = "hist_%s" %(today.strftime("%d-%m-%Y"))
    fileDir = FOLDER + '/' + graphic_name +".png"

    if os.path.isfile(fileDir):
        os.remove(fileDir)   # Opt.: os.system("rm "+strFile)
    plt.savefig(fileDir)
    return json.dumps({"status":"ok","file":graphic_name})

@app.route('/get_images')
def get_images():
    base_path = pathlib.Path('static/images/')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(str(f_name))
    data.seek(0)
    zipname = str(datetime.datetime.now()) + '.zip'
    return send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename=zipname)

@app.route('/<img_name>')
def get_image(img_name):
    url = 'static/images/' + img_name + '.png'
    return send_file(url, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
