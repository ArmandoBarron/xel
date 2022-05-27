import sys
import pandas as pd
from pandas.errors import ParserError
import seaborn as sns
import logging
import os
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

'''
Este script se usa para calcular correlaciones en un dataset. 
Recibe como argumentos de entrada: la ubicación del dataset (archivo .csv) los parámetros para calcular la correlación 
y produce como salida un archivo .csv con los valores de la matríz de correlación y una imagen png. con el heatmap de correlación.
'''

''' 
Aquí se define la clase loggin para generar y mantener el log de errores del script.
'''
logging.basicConfig(filename=ACTUAL_PATH+'/log/correlation_errors.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logging.disable('DEBUG')
logger=logging.getLogger('__main__')

'''
Aquí se verifica que al ejecutar el script se reciba el número correcto de argumentos para poder calcular
la correlación.
'''
if len(sys.argv) <= 5:
    print('''No hay argumentos suficientes: Este script requiere de 5 argumentos: 
    1. Ubicación del dataset (debe ser un archivo .csv) 
    2. Método para calcular la correlación (pearson, kendall, spearman)
    3. Nímero de periodos (observaciones) para calcular la correlación (solo útil para los métodos: 'pearson' y 'spearman')
    4. Lista de columnas a correlacionar en formato csv (separado por comas) ('all' si se desea usar todas las columnas)
    5. Ubicación de salida para almacenar los archivos resultantes (imagen del heatmap y archivo .csv de valores) incluyendo el nombre que llevaran los archivos(sin extensión)
    Ejemplo: correlate.py data/file1.csv pearson 3 column1,column2,column3 output/correlation_result''')
    logger.error('Argumentos insuficientes para ejecutar el script')
    quit()

'''
Obtener el archivo del dataset como primer argumento
'''
dataset_file = sys.argv[1]
print('dataset a correlacionar:', dataset_file)

'''
Verificar que el archivo ingresado sea un .csv
'''
if  not dataset_file.endswith('.csv'):
    error = "El archivo " + dataset_file + " no es .csv"
    print(error)
    logger.error(error)
    quit()

'''
Verificar que el método de correlación ingresado sea válido
'''
correlation_method = sys.argv[2]
print('método de correlación:', correlation_method)
if (correlation_method != "pearson" and correlation_method != "kendall" and correlation_method != "spearman"):
    error = "método de correlación no soportado: " + correlation_method
    print(error)
    logger.error(error)
    quit()

'''
Verificar que el número de periodos ingresado sea un número entero válido
'''
try:
    periods = int(sys.argv[3])
    print('Número de periodos a ejecutar: ' + str(periods))
except ValueError as err:
    error = "El número de periodos debe ser un un número entero"
    print(error)
    logger.error(error)
    quit()
    
'''
Verificar si se van a correlacionar todas las columnas, en caso de que no, verificar
que se hayan ingresado al menos 2 columnas
'''
use_all_columns = False
column_list = sys.argv[4].split(',')
print('Columnas para el cálculo de correlación:', column_list )
if len(column_list) == 1 and column_list[0] == 'all':
    print('se usaran todas las columnas')
    use_all_columns = True
elif len(column_list) < 2:
    error = "Se necesitan al menos 2 columnas para calcular correlación"
    print(error)
    logger.error(error)
    quit()

'''
Intenta leer el archivo .csv en un DataFrame y verificar que las columnas ingresadas
esten contenidas en el dataset
'''
try:
    data_frame = pd.read_csv(dataset_file)
    if use_all_columns == False:
        for column in column_list:
            if column not in data_frame.columns:
                error = "La columna " + column + " no existe en el dataset" 
                print(error)
                logger.error(error)
                quit()
except Exception as exc:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))
    quit()

'''
Ejecuta el cálculo de la correlación utilizando el método ingresado y las columnas indicadas.
'''
if use_all_columns == True:
    print('Calculando la correlación en todas las columnas utilizando el método ' + correlation_method + ' con' + str(periods) + ' periodos')
    result_df = data_frame.corr(method=correlation_method, min_periods=periods)
else:
    print('Calculando correlación en las columnas ' + str(column_list) +  ' usando el método ' + correlation_method + ' con ' + str(periods) + ' periodos')
    columns_to_correlate = []
    for column in column_list:
        columns_to_correlate.append(column)
    #print(columns_to_correlate)
    result_df = data_frame[columns_to_correlate].corr(method=correlation_method, min_periods=periods)
    
'''
Escribe la matríz de valores resultante en un archivo .csv en la ubicación indicada.
'''
output_dir = sys.argv[5]
print('directorio de salida:', output_dir)
try:
    result_df.to_csv(output_dir + '.csv', index=False)
    print('Matríz de valores almacenada en', output_dir + '.csv')
except Exception as exc:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))
    
'''
Genera el heatmap usando el DataFrame con los resultados de la correlación
'''
try:
    result_df = result_df.astype(float)
    print(result_df.dtypes)
    plt = sns.heatmap(result_df)

except Exception as exc:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(exc)
    #logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))
    quit()
    
'''
Almacena el heatmap de correlación en una imágen .png en la ubicación indicada. 
'''
try: 
    fig = plt.get_figure()
    fig.savefig(output_dir + '.png')
    print('Heatmap de resultados almacenado en', output_dir + '.png')
except Exception as exc:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    logger.error(str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno))
    