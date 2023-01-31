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
query_str= sys.argv[6] #query to filter data
if_assign= sys.argv[7] #assign results to the original dataset


DF_data = pd.read_csv(data_path)
columns = DF_data.columns

columns= set(columns) - set(variables) #remove columns that are going to be group
columns= set(columns) - set(group_columns) 

applied_dict=dict()
#for x in columns:
#        applied_dict[x]="first"

for x in variables:
        applied_dict[x]=group_by

#print(DF_data)

if group_by == "count":
        DF_data=DF_data[group_columns]
        DF_data['count'] = 0
        temp_df = DF_data.groupby(group_columns)['count'].count()
else:
        temp_df = DF_data.groupby(group_columns).agg(applied_dict)

if if_assign =="1":
        DF_data=DF_data.join(temp_df, on=group_columns, rsuffix='_%s' %(group_by))
else:
        DF_data = temp_df.reset_index()
# ==============================================================
if query_str != "":
        try:
                DF_data = DF_data.query(query_str)
        except Exception as e:
                print("hay errores en el query")
                print(e)


DF_data.to_csv(output_path,index=False)



#print(DF_data)


