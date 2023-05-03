import sys
import os
import json

import pandas as pd
import numpy as np
from scipy import stats

"""
python3 Clean_int.py CalidadAgua.csv clean_dataset.csv "ALC_mg/L,CONDUCT_mS/cm,SDT_mg/L,SDT_M_mg/L,FLUORUROS_mg/L,DUR_mg/L,COLI_FEC_NMP/100_mL,N_NO3_mg/L,AS_TOT_mg/L,CD_TOT_mg/L,CR_TOT_mg/L,HG_TOT_mg/L,PB_TOT_mg/L,MN_TOT_mg/L,FE_TOT_mg/L"

"""
data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns

DF_data = pd.read_csv(data_path)

DF_data[columns]= DF_data[columns].apply(pd.to_numeric, errors='coerce')

DF_data.to_csv(output_path,index=False)