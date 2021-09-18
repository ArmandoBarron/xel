import sys
import os
import time
import pandas as pd
import json



data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path

group_columns= sys.argv[3].split(",") #group 
variables = sys.argv[4].split(",") #variables list
group_by= sys.argv[5] #group_by


DF_data = pd.read_csv(data_path)
columns = DF_data.columns

columns= set(columns) - set(variables) #remove columns that are going to be group
columns= set(columns) - set(group_columns) 

applied_dict=dict()
for x in columns:
        applied_dict[x]="first"

for x in variables:
        applied_dict[x]=group_by

#print(DF_data)

DF_data = DF_data.groupby(group_columns,as_index=False).agg(applied_dict)

DF_data.to_csv(output_path,index=False)

#print(DF_data)


