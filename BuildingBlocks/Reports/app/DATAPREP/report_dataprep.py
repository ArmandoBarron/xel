import pandas as pd
from dataprep.eda import plot, plot_correlation, plot_missing
from dataprep.eda import create_report
from os import sys


def validate_att(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="" or att =="-":
        return False
    else:
        return True

def validate_bool(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="0":
        return False
    else:
        return True


"""

"""


inputpath = sys.argv[1] # "Suic_Medio_Derhab_tasasporsexo.csv"
outputpath = sys.argv[2] #  "./output/"
title = sys.argv[3] if validate_att(sys.argv[3]) else "Report"



df = pd.read_csv(inputpath)
report = create_report(df)
report.save(outputpath+'MyReport.html') # save report to local disk