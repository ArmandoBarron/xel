import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def json2dataframe(data):
    df = pd.DataFrame.from_records(data)
    return df

def DF_Filter(df,filtter):
    if filtter == "all": return df
    filtter = filtter.split(",")
    return df[filtter]

def Numeric(df):
    return df.apply(pd.to_numeric)

def scale(df):
    scaler = StandardScaler()
    # Fit on training set only.
    scaler.fit(df)
    # Apply transform to both the training set and the test set.
    scale_df = scaler.transform(df)
    return scale_df