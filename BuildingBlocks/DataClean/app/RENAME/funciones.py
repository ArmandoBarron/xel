import pickle 
import json
import pandas as pd
from pathlib import Path


def generar_ruta (extension, ruta_entrada, ruta_salida=None, prefijo=None):
    if ruta_salida is None:
        path_salida=Path(ruta_entrada)
        return f"{str(path_salida.parent)}/{prefijo}_output.{extension}"
    else:
        path_salida=Path(ruta_salida)
        if path_salida.is_dir():
            return f"{str(path_salida)}/{prefijo}_output.{extension}"
        else:
            if (ruta_salida.endswith(f'{extension}')):
                return ruta_salida
            elif ruta_salida.endswith('/') or ruta_salida.endswith('\\'):
                path_salida.mkdir()
                return f"{ruta_salida}{prefijo}_output.{extension}"
            else:
                return f"{ruta_salida}.{extension}"

def guardar_json (datos_entrada, ruta_entrada, ruta_salida, prefijo=None):
    ruta=generar_ruta ('json', ruta_entrada, ruta_salida, prefijo)
    f=open(ruta, 'w')
    json.dump (datos_entrada, f)
    f.close()

def cargar_json (ruta_entrada):
    f=open(ruta_entrada, 'r')
    object = json.load(f)
    f.close()
    return object

def guardar_pickle (datos_entrada, ruta_entrada, ruta_salida, prefijo=None):
    ruta=generar_ruta ('pkl', ruta_entrada, ruta_salida, prefijo)
    f=open(ruta, 'wb')
    pickle.dump (datos_entrada, f)
    f.close()

def cargar_pickle (ruta_entrada):
    f=open(ruta_entrada, 'rb')
    object = pickle.load(f)
    f.close()
    return object

def guardar_txt (datos_entrada, ruta_entrada, ruta_salida, prefijo=None):
    ruta=generar_ruta ('txt', ruta_entrada, ruta_salida, prefijo)
    f=open(ruta, 'w')
    f.write(datos_entrada)
    f.close()

def guardar_csv (datos, ruta_entrada, ruta_salida=None, prefijo=None):
    ruta=generar_ruta ('csv', ruta_entrada, ruta_salida, prefijo)
    datos.to_csv(ruta)

def cargar_csv (ruta_entrada, is_indexed=True):
    if is_indexed==None or is_indexed:
        datos= pd.read_csv(ruta_entrada, index_col=0)
    else:
        datos= pd.read_csv(ruta_entrada)
    return datos
