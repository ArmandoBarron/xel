import sys
import os
import json

import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer,IterativeImputer,KNNImputer


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns
imputation_type= sys.argv[4] #simple numeric, simple categorical, multiple
strategy= sys.argv[5] #maan median or most_frequent (mode)
groups= sys.argv[6].split(",") 
n_neighbors= sys.argv[7] #
fill_value= sys.argv[8] #

if n_neighbors =="" or n_neighbors == "-":
    n_neighbors = 2
else:
    n_neighbors =int(n_neighbors)


if fill_value.lstrip('-+').isdigit(): #verificar si el string es numerico y se parsea
    try:
        fill_value = int(fill_value)
    except ValueError:
        fill_value = float(fill_value)

def imputeData(df):
    imp=SimpleImputer(missing_values=np.NaN,strategy=strategy)
    res= imp.fit_transform(df[columns])
    df[columns]=res
    return df

def imputeData_iterative(df):
    imp = IterativeImputer(max_iter=10)
    res= imp.fit_transform(df[columns])
    df[columns]=res
    return df

def imputeData_KNN(df):
    print(df[columns])
    imp = KNNImputer(n_neighbors=n_neighbors, weights="uniform")
    res= imp.fit_transform(df[columns])
    df[columns]=res
    return df

def imputeData_KNN(df):
    print(df[columns])
    imp = KNNImputer(n_neighbors=n_neighbors, weights="uniform")
    res= imp.fit_transform(df[columns])
    df[columns]=res
    return df

def imputeData_constant(df):
    print(df[columns])
    imp = SimpleImputer(strategy='constant', fill_value=fill_value)
    res= imp.fit_transform(df[columns])
    df[columns]=res
    return df


DF_data = pd.read_csv(data_path)
print(DF_data[columns])

print(DF_data.isna().sum())

if imputation_type == "Single_N":
    DF_data = imputeData(DF_data)
if imputation_type == "Single_G":
    DF_data = DF_data.groupby(groups).apply(imputeData)

if imputation_type == "Iter_N":
    DF_data = imputeData_iterative(DF_data)
if imputation_type == "Iter_G":
    DF_data = DF_data.groupby(groups).apply(imputeData_iterative)

if imputation_type == "Knn_N":
    DF_data = imputeData_KNN(DF_data)
if imputation_type == "Knn_G":
    DF_data = DF_data.groupby(groups).apply(imputeData_KNN)

if imputation_type == "Constant_N":
    DF_data = imputeData_constant(DF_data)

DF_data.to_csv(output_path,index=False)

#print(DF_data[groups+columns])