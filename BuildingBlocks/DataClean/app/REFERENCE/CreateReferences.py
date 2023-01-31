import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
column= sys.argv[3]#columns
new_column = sys.argv[4] #
References = sys.argv[5] #

# {  }

# }


DF_data = pd.read_csv(data_path)

if method =="DUMMY":
    # using .get_dummies function to convert
    # the categorical datatype to numerical
    # and storing the returned dataFrame
    df_dummy = pd.get_dummies(DF_data[columns])
    # using pd.concat to concatenate the dataframes
    # df and df1 and storing the concatenated
    DF_data = pd.concat([DF_data, df_dummy], axis=1).reindex(DF_data.index)

if method =="ENCODING":
    # Creating a instance of label Encoder.
    le = LabelEncoder()
    
    # Using .fit_transform function to fit label
    # encoder and return encoded label
    labels = le.fit_transform(DF_data[columns])
    
    # Appending the array to our dataFrame
    # with column name 'Purchased'
    DF_data[columns] = labels


DF_data.to_csv(output_path,index=False)

