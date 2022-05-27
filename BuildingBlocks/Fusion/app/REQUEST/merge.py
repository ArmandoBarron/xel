import sys
import pandas as pd
from pandas.errors import ParserError
import logging
import os
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
'''
Este script se usa para realizar un 'merge' entre los datasets indicados.
Recibe como argumentos de entrada una lista de datasets y las columnas para el 'merge' y el tipo de 'merge'.
Produce como salida un nuevo dataset con el resultado del 'merge' en un archivo .csv
'''

''' 
Aquí se define la clase loggin para generar y mantener el log de errores del script.
'''
logging.basicConfig(filename=ACTUAL_PATH+'/log/merge_errors.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

'''
Aquí se verifica que al ejecutar el script se reciba el número correcto de argumentos para poder realizar
el 'merge'
'''
if len(sys.argv) <= 3:
    print('''No hay argumentos suficientes: Este script requiere de 4 argumentos: 
    1. Lista de datasets de entrada y columnas a usar para cada dataset. Se separa el dataset de las columnas usando ':' Las columnas van dentro de corchetes y separadas por un "." Cada dataset y columnas se separan por ','.
    2. Tipo de 'merge' a realizar (iner, outer, left, right)
    3. Ubicación de salida para almacenar el dataset resultante en formato .csv 
    
    Ejemplo: merge.py data/file1.csv:[column_name1.column_name2],data/file2.csv:[column_name3.column_name4] inner output/output.csv''')
    logger.error('Argumentos insuficientes para ejecutar el script')
    quit()

'''
Separa el primer argumento en una lista de datasets con sus columnas
'''
file_list = sys.argv[1].split(';')
print('datasets para el merge:', file_list)

'''
Verifica que se hayan recibido al menos 2 archivos para el 'merge'
'''
if len(file_list) < 2:
    error = 'Solo se recibió 1 archivo, no se puede hacer el merge'
    print(error)
    logger.error(error)
    quit()

'''
Verifica que el tipo de merge sea "inner", "outer", "left" o "right"
'''
merge_type = sys.argv[2]
print('merging type:', merge_type)
if (merge_type != "inner" and merge_type != "outer" and merge_type != "left" and merge_type != "right"):
    error = 'Tipo de merge no soportado'
    print(error)
    logger.error(error)
    quit()
    
'''
Trata de leer cada archivo .csv y generar un DataFrame
'''
datasets = []
count = 0
for file in file_list:
    file_column = file.split(':')
    data_file = file_column[0]
    column_list = file_column[1].replace('[','').replace(']','').split(',')
    print('cargando dataset:', data_file)
    
    #Si el archivo no es .csv, descartarlo
    if  not data_file.endswith('.csv'):
        print('El archivo', data_file, 'no es un archivo .csv')
        logger.error('El archivo ' + data_file + ' no es un archivo .csv')
        quit()
        
    #Trata de leer el archivo csv en un DataFrame
    try:
        data_frame = pd.read_csv(data_file)
        
        #Verificar que el DataFrame contiene las columnas indicadas
        print('buscando las columnas:', column_list)            
        for column in column_list: 
            if column not in data_frame.columns:
                print('La columna', column, 'no existe en el dataset', column)
                logger.error('La columna ' + column + " no existe en el dataset")
                quit()
        #Genera una lista con diccionarios que asocian cada DataFrame con su lista de columnas
        datasets.append({'id':count, 'dataframe':data_frame, 'columns':column_list})
        count = count + 1
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))

'''
Verifica que se hayan creado satisfactoriamente al menos 2 DataFrames para el 'merge'
'''
df_aux = None
if len(datasets) > 1:
    try:
        for data_set in datasets:
            if (data_set['id'] != 0):
                column_right = data_set['columns']
                print('merging:', source_aux['columns'], "with", data_set['columns'])
                df_aux = df_aux.merge(data_set['dataframe'], how = merge_type, 
                        left_on=source_aux['columns'],
                        right_on=column_right)	
            else:
                df_aux = data_set['dataframe'].copy()
                source_aux = data_set
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))
        quit()
else:
    print('Insuficientes datasets para merge')
    logger.error('Insuficientes datasets para merge')
    quit()

'''
Genera un dataset en formato .csv con los resultados del merge en la ubicación indicada
'''
output_dir = sys.argv[3]
print('ubicación de salida:', output_dir)
try:
    df_aux.to_csv(output_dir, index=False)
    print('dataset resultante almacenado en', output_dir)
except Exception as exc:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))
    