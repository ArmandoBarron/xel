import funciones
import pandas as pd
import argparse
from distutils.util import strtobool

def clasificar (datos, modelo):
    clases = modelo.predict (datos)
    return clases
    

def clasificar_csv (ruta_entrada, ruta_modelo,columnas_interes, ruta_salida=None, is_indexed=True):
    datos_entrada=funciones.cargar_csv(ruta_entrada, is_indexed)

    if columnas_interes == None:
        columnas_interes = datos_entrada.columns
    else:
        columnas_interes = columnas_interes.split(",")

    modelo=funciones.cargar_pickle(ruta_modelo)
    clases_salida=clasificar (datos_entrada[columnas_interes], modelo)
    datos_entrada['class'] = clases_salida
    funciones.guardar_csv (datos_entrada, ruta_entrada, ruta_salida, prefijo="predicciones")


def parse_args():
    #Nombre y descicpicón del programa, se muestra desde consola con -h
    parser = argparse.ArgumentParser("Clasificador", description="Predicciones de un clasificador. Los datos de entrada deben estar normalizados. El modelo entrenado se carga de un archivo .pkl.")

    #Cada variable se necesita declara como posible entrada con la descripción a mostrarse si se ejecuta el comando -h, -- se usa cuando es una variable opción
    parser.add_argument("ruta_entrada", help="Ruta completa del archivo con los datos normalizados de entrada.",
                        type=str)
    parser.add_argument("ruta_modelo", help="Ruta completa del archivo .pkl con el modelo entrenado.",
                        type=str)
    parser.add_argument("--columnas_interes",
                        help="Nombre de las columnas que que se utilizaran para generar el modelo. Por defecto son todas menos la columna de clase",
                        type=str, nargs='?', default=None)

    parser.add_argument("--ruta_salida",
                        help="Salida de la clasificación de los datos de entrada.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--is_indexed",
                        help="Es necesario que los datos del archivo .CSV estén indexados en la primer columna, en caso de que no lo estén, ingrese --is_indexed=False para asignar uno en automático. --is_indexed=True por defecto",
                        type=str, nargs='?', default="False")

    return parser.parse_args()


#main 
if __name__ == "__main__":
    options = parse_args()
    clasificar_csv (options.ruta_entrada, options.ruta_modelo,  options.columnas_interes ,options.ruta_salida, strtobool(options.is_indexed))

