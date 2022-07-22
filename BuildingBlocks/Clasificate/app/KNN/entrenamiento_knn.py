import funciones
import argparse
from distutils.util import strtobool

import matplotlib.pyplot as plt
import pandas as pd
import sklearn as sk
import numpy as np
import matplotlib

from sklearn import model_selection
from sklearn import metrics
from sklearn import svm
from sklearn import neighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split



def metricas (prueba_clase, prediccion_prueba, average='micro'):

    texto=""

    y_true=prueba_clase.values.ravel()
    y_pred=prediccion_prueba

    pres=sk.metrics.precision_score(y_true, y_pred, average=average)
    texto=texto+f"precision_score: {pres}\n" 
    rec=sk.metrics.recall_score(y_true, y_pred, average=average)
    texto=texto+f"recall_score: {rec}\n"
    acc=sk.metrics.accuracy_score(y_true, y_pred)
    texto=texto+f"accuracy: {acc}\n"
    f1=sk.metrics.f1_score(y_true, y_pred, average=average)
    texto=texto+f"f1_score: {f1}\n"

    texto=texto+f"\nPor clase: \n"

    texto=texto+sk.metrics.classification_report(y_true, y_pred, digits=3)+"\n"

    labels=np.unique(y_true)

    res = []
    for i in range(0,labels.size):
        prec,recall,_,_ = sk.metrics.precision_recall_fscore_support(y_true==labels[i],
                                                        y_pred==labels[i],
                                                        pos_label=True,average=None)
        res.append([recall[0],recall[1]])

    texto=texto+pd.DataFrame(res,columns = ['Sensibilidad','Especificidad'], index=labels).to_string()+ '\n\n'

    #Matriz de confusión
    conf=sk.metrics.confusion_matrix(y_true, y_pred)
    texto=texto+f"Matriz de confusión:\n{conf}\n"
    disp = sk.metrics.ConfusionMatrixDisplay(confusion_matrix=conf)
    
    return texto, disp


def clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, average='micro',
        n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', metric_params=None, n_jobs=None):

    clasificador = sk.neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm, leaf_size=leaf_size, p=p, metric=metric, metric_params=metric_params, n_jobs=n_jobs)
    
    clasificador.fit (entrenamiento_datos, entrenamiento_clase)

    prediccion_prueba=clasificador.predict(prueba_datos)
    
    texto, disp=metricas (prueba_clase, prediccion_prueba, average)
    
    return texto, disp, prediccion_prueba, clasificador



def clasificar_csv (ruta_entrada_entrenamiento, ruta_salida_prueba=None, 
        ruta_salida_clasificador=None, ruta_salida_reporte=None, ruta_salida_imagen=None,columnas_interes=None,columna_clase = None, is_indexed=True, average='micro',
        n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', metric_params=None, n_jobs=None):

    dataset=funciones.cargar_csv(ruta_entrada_entrenamiento, is_indexed)

    if columna_clase == None:
        columna_clase=dataset.columns [-1]

    if columnas_interes == None:
        columnas_interes = dataset.columns
        columnas_interes.remove(columna_clase)

    else:
        columnas_interes = columnas_interes.split(",")

    #entrenamiento, prueba = train_test_split(entrenamiento, test_size=0.2)
    entrenamiento_datos, prueba_datos, entrenamiento_clase, prueba_clase = train_test_split(dataset[columnas_interes], dataset[columna_clase], test_size=0.2)
    
    texto, disp, prediccion_prueba, clasificador=clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, average, 
        n_neighbors=n_neighbors, weights=weights, algorithm=algorithm, leaf_size=leaf_size, p=p, metric=metric, metric_params=metric_params, 
        n_jobs=n_jobs)


    funciones.guardar_csv (pd.DataFrame(prediccion_prueba, columns = ['clase']), ruta_entrada_entrenamiento, ruta_salida_prueba, prefijo="resultados_prueba")
    funciones.guardar_pickle (clasificador, ruta_entrada_entrenamiento, ruta_salida_clasificador, prefijo="clasificador")
    funciones.guardar_txt (texto, ruta_entrada_entrenamiento, ruta_salida_reporte, prefijo="reporte_entrenamiento")
    funciones.guardar_png (disp, ruta_entrada_entrenamiento, ruta_salida_imagen, prefijo="confusion")


def parse_args():
    #Nombre y descicpicón del programa, se muestra desde consola con -h
    parser = argparse.ArgumentParser("Clasificador", description="Entrenamiento de un clasificador. Los datos de entrada deben estar normalizados, y separados en prueba y entrenamiento. El modelo entrenado se alamacena en un archivo .pkl.")

    #Cada variable se necesita declara como posible entrada con la descripción a mostrarse si se ejecuta el comando -h, -- se usa cuando es una variable opción
    parser.add_argument("ruta_entrada_entrenamiento", help="Ruta completa del archivo con los datos normalizados de entrenamiento.",
                        type=str)
    parser.add_argument("--ruta_salida_prueba",
                        help="Salida de la clasificación de los datos de prueba",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_clasificador",
                        help="Ruta de salida donde se guardará el archivo .pkl del clasificador entrenado",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_reporte",
                        help="Ruta del reporte de entrenamiento en formato .txt.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_imagen",
                        help="ruta de salida de la matriz de confusión en formato .png",
                        type=str, nargs='?', default=None)
    parser.add_argument("--columnas_interes",
                        help="Nombre de las columnas que que se utilizaran para generar el modelo. Por defecto son todas menos la columna de clase",
                        type=str, nargs='?', default=None)

    parser.add_argument("--columna_clase",
                        help="Nombre de la columna que contiene la clase de cada valor, por defecto se toma la última columna.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--is_indexed",
                        help="Es necesario que los datos del archivo .CSV estén indexados en la primer columna, en caso de que no lo estén, ingrese --is_indexed=False para asignar uno en automático. --is_indexed=True por defecto",
                        type=str, nargs='?', default="False")
    parser.add_argument("--average",
                        help="para la función de evaluación basada en sk.metrics.precision_score, etc. con la que se genera el reporte del entrenamiento, average{‘micro’, ‘macro’, ‘samples’, ‘weighted’, ‘binary’} or None, default=’binary’",
                        type=str, nargs='?', default='micro')
    parser.add_argument("--n_neighbors", help="n_neighbors, default=5",
                        type=int, nargs="?", default=5)
    parser.add_argument("--weights", help="weights, default='uniform'",
                        type=str, nargs="?", default='uniform')
    parser.add_argument("--algorithm", help="algorithm, default='auto'",
                        type=str, nargs="?", default='auto')
    parser.add_argument("--leaf_size", help="leaf_size, default=30",
                        type=int, nargs="?", default=30)
    parser.add_argument("--p", help="p, default=2",
                        type=int, nargs="?", default=2)
    parser.add_argument("--metric", help="metric, default='minkowski'",
                        type=str, nargs="?", default='minkowski')
    parser.add_argument("--metric_params", help="metric_params, default=None",
                        type=dict, nargs="?", default=None)
    parser.add_argument("--n_jobs", help="n_jobs, default=None",
                        type=int, nargs="?", default=None)

    return parser.parse_args()

#main 
if __name__ == "__main__":
    options = parse_args()
    
    clasificar_csv (options.ruta_entrada_entrenamiento, options.ruta_salida_prueba,
     options.ruta_salida_clasificador, options.ruta_salida_reporte, options.ruta_salida_imagen, options.columnas_interes,options.columna_clase,
     strtobool(options.is_indexed), options.average, 	options.n_neighbors, 
     options.weights, options.algorithm, options.leaf_size, options.p, options.metric, options.metric_params, options.n_jobs)
