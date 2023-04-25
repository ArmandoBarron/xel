import pandas as pd
import bar_chart_race as bcr
import numpy as np
import sys
#$from matplotlib.animation import FuncAnimation, PillowWriter 

"""
python top10.py Suic_Medio_Derhab_tasasporsexo.csv ./out/ 'anio' 'tasa_suic' 'cve_ent,sexo' 10 "titulo"

python3 top10.py Suic_Medio_Derhab_tasasporsexo.csv ./out/ "anio" "total_suic" "sexo, cve_ent" "10" "sum" "test"

python /home/app/TOP_K/top10.py /tmp/tmp6014lxkl.csv /tmp/tmpba8kl8um/ "anio" "total_suic" "sexo,cve_ent_mun" "10" "sum" "test"

python3 top10.py defunciones_all_5anios.csv ./out/ "ANIO_REGIS" "CONTEO" "Descripcion" "10" "sum" ""

python3 top10.py subset.csv ./out/ "ANIO_REGIS" "CONTEO" "NAME_CAUSA" "5" "sum" "Top5 - Mortalidad por cancer infantil"

"""

def create_transpose(df,values,indez,columns,func="sum"):
    df_by = pd.pivot_table(df,
                            values=values,
                            index=indez,
                            columns=columns,
                            aggfunc=np.sum)
    df_by = df_by.fillna(0)
    window = len(df.index.unique())
    if func =="sum":
        df_by = df_by.rolling(min_periods=1, window=window).sum()
    elif func =="mean":
        df_by = df_by.rolling(min_periods=1, window=window).mean()
        
    print(df_by)
    return df_by

def bar_race(df,filename,title,n_bars):
    bcr.bar_chart_race(
        df = df,
        filename=r"{}.mp4".format(filename),
        title=title,
        bar_kwargs={'alpha': .7},
        n_bars=n_bars,
        period_length=1200,
        #perpendicular_bar_func=func,
        steps_per_period=40,
        interpolate_period=False,
        label_bars=True,
        period_label={'x': .99, 'y': .25, 'ha': 'right', 'va': 'center'},
        figsize=(17,17),
        bar_label_size=14,
        tick_label_size=10,
        dpi=110,
        filter_column_colors=True
    )



inputpath = sys.argv[1] # "Suic_Medio_Derhab_tasasporsexo.csv"
outputpath = sys.argv[2] #  "./output/"
TIME_COLUMN =sys.argv[3]
VALUE_COLUMN =sys.argv[4]
NAME_COLUMN = sys.argv[5].split(",")
TOP_N = int(sys.argv[6]) 
function = sys.argv[7] #mean. median, sum

TITLE = sys.argv[8] 

df= pd.read_csv(inputpath)

df = df.set_index(TIME_COLUMN)
df_by = create_transpose(df=df,
        values=VALUE_COLUMN,
        indez=TIME_COLUMN,
        columns=NAME_COLUMN)

bar_race(df = df_by,
        filename="%s/bar_race_TOP" % outputpath , 
        title=TITLE,
        n_bars=TOP_N)

