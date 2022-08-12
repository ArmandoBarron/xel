import funciones
import argparse
import re
import pandas as pd
import numpy as np
from distutils.util import strtobool

def renombrar (datos_entrada, lista_clases, columna_clases=None):
    
    if columna_clases==None:
        columna_clases=datos_entrada.columns [-1]
        
    clases_anteriores = np.sort(datos_entrada [columna_clases].unique())
    datos_entrada[[columna_clases]]=datos_entrada[[columna_clases]].replace (clases_anteriores, lista_clases)
    return datos_entrada

def renombrar_csv (ruta_entrada, lista_clases, ruta_salida=None, is_indexed=None, columna_clases=None):
    datos_entrada=funciones.cargar_csv (ruta_entrada, is_indexed)
    datos_salida=renombrar(datos_entrada, lista_clases, columna_clases)
    funciones.guardar_csv (datos_salida, ruta_entrada, ruta_salida, prefijo="renombrado")




def parse_args():
    #Nombre y descicpicón del programa, se muestra desde consola con -h
    parser = argparse.ArgumentParser("Renombrar", description="Renombra las diferentes clases contenidas una columna del archivo .CSV de entrada, de numérico a texto. Por ejemplo, [1,2,3] -> [ClaseA,ClaseB,ClaseC]")

    #Cada variable se necesita declara como posible entrada con la descripción a mostrarse si se ejecuta el comando -h, -- se usa cuando es una variable opción
    parser.add_argument("ruta_entrada", help="Ruta completa de la ubicación del archivo con los datos a renombrar.",
                        type=str)
    parser.add_argument('-lista_clases',
                        type=lambda s: re.split(',', s),
                        required=True,
                        help='Nuevos nombres de las clases en orden de menor a mayor. Ingrese las clasases separadas por comas entre comillas sin espacios. Por ejemplo, --lista_clases="ClaseA,ClaseB,ClaseC"')                    
    parser.add_argument("--ruta_salida",
                        help="Ruta completa de la ubicación del archivo CSV de salida con los datos renombrados.",
                        type=str, nargs='?', const=None)
    parser.add_argument("--is_indexed",
                        help="Es necesario que los datos del archivo .CSV estén indexados en la primer columna, en caso de que no lo estén, ingrese --is_indexed=False para asignar uno en automático. --is_indexed=True por defecto",
                        type=str, nargs='?', default="True")
    parser.add_argument("--columna_clase",
                        help="Nombre de la columna que contiene las clases correspondientes a cada valor. Por defecto se toma la última columna",
                        type=str,nargs='?', const=None)
    

    return parser.parse_args()

if __name__ == "__main__":
    options = parse_args()
    
    print (options)
    renombrar_csv (options.ruta_entrada, options.lista_clases, options.ruta_salida, options.is_indexed, options.columna_clase)