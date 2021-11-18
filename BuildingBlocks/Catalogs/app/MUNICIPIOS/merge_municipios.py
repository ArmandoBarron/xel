import pandas as pd
import sys
import os 
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

inputpath=sys.argv[1]
outputpath=sys.argv[2]

cve_ent = sys.argv[3]
cve_mun = sys.argv[4]

datasource_keys=[cve_ent,cve_mun] 
catalog_keys=['CVE_ENT','CVE_MUN']    

catalog = ACTUAL_PATH + "municipios_geo.csv"

df_data = pd.read_csv(inputpath)
df_mun =pd.read_csv(catalog)
print("merging..")
print(df_mun)
print(df_data)

df_data = pd.merge(df_data, df_mun,  how='inner', left_on=datasource_keys, right_on = catalog_keys)
df_data.to_csv(outputpath,index=False)
