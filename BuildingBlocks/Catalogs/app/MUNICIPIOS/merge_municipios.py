import pandas as pd
import numpy as np
import sys
import os 
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

inputpath=sys.argv[1]
outputpath=sys.argv[2]

mode = int(sys.argv[3]) # 1 == clave entidad y clave municipio,  2 == clave entidadmunicipio EEMMM e.g. 32001

cve_ent = sys.argv[4]
cve_mun = sys.argv[5]

catalog = ACTUAL_PATH + "municipios_geo.csv"
df_data = pd.read_csv(inputpath)
df_mun =pd.read_csv(catalog)

df_mun= df_mun[['CVE_ENT','CVE_MUN','lat','lon']]
print("merging..")
print(df_mun)
print(df_data)

if mode == 1:
    datasource_keys=[cve_ent,cve_mun] 
    catalog_keys=['CVE_ENT','CVE_MUN']    
if mode == 2:
    datasource_keys=[cve_ent] 
    catalog_keys=['CVE_ENT_MUN']

    m1 = (df_mun['CVE_MUN'] < 100) & (df_mun['CVE_MUN'] > 9)
    m2 = df_mun['CVE_MUN'] < 10

    df_mun['CVE_MUN'] = df_mun['CVE_MUN'].astype(str)

    df_mun.loc[m1, 'CVE_MUN'] = "0"+df_mun.loc[m1, 'CVE_MUN']
    df_mun.loc[m2, 'CVE_MUN'] = "00"+df_mun.loc[m2, 'CVE_MUN']

    print(df_mun['CVE_MUN'])

    df_mun['CVE_ENT_MUN'] = (df_mun['CVE_ENT'].astype(str) + df_mun['CVE_MUN']).astype(int)
    
if mode == 3:
    # por nombre municipio
    datasource_keys=[cve_mun] 
    catalog_keys=['nombre municipio']
    query_estados = "(`Nombre Abreviado de AGEE`=='CDMX' or `Nombre Abreviado de AGEE`=='Mex.')"
    df_mun = df_mun.query(query_estados)

df_data = pd.merge(df_data, df_mun,  how='inner', left_on=datasource_keys, right_on = catalog_keys)
df_data.to_csv(outputpath,index=False)


