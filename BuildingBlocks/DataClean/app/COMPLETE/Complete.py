import sys
import os
import json

import pandas as pd
import numpy as np
from scipy import stats
import janitor


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns

DF_data = pd.read_csv(data_path)

DF_data = DF_data.complete(*columns).fillna(0, downcast='infer')

DF_data.to_csv(output_path,index=False)