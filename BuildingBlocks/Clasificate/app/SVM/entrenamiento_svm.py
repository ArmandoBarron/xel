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
    # y_true=prueba_clase.flatten().astype('int')
    # y_pred=prediccion_prueba.astype('int')

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


    #Son las mismas métricas que el reporte anterior (sk.metrics.classification_report):
    #precision, recall, f1s, support = sk.metrics.precision_recall_fscore_support(y_true, y_pred)
    #print ("precision: ", precision)
    #print ("recall: ", recall)
    #print ("f1_score: ", f1s)
    #print ("Número de ocurrecias: ", support)

    labels=np.unique(y_true)

    res = []
    for i in range(0,labels.size):
        prec,recall,_,_ = sk.metrics.precision_recall_fscore_support(y_true==labels[i],
                                                        y_pred==labels[i],
                                                        pos_label=True,average=None)
        #print (i)
        #print (recall)    
        #print(prec)
        res.append([recall[0],recall[1]])

    texto=texto+pd.DataFrame(res,columns = ['Sensibilidad','Especificidad'], index=labels).to_string()+ '\n\n'

    #Matriz de confusión
    conf=sk.metrics.confusion_matrix(y_true, y_pred)
    texto=texto+f"Matriz de confusión:\n{conf}\n"
    disp = sk.metrics.ConfusionMatrixDisplay(confusion_matrix=conf)
    #disp.plot()
    #plt.show()
    return texto, disp


def clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, average='micro',

        C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, 
        class_weight=None, verbose=False, max_iter=- 1, decision_function_shape='ovr', break_ties=False, random_state=None,
        ):

    clasificador=svm.SVC(C=C, kernel=kernel, degree=degree, gamma=gamma, coef0=coef0, shrinking=shrinking, probability=probability, tol=tol, cache_size=cache_size, 
        class_weight=class_weight, verbose=verbose, max_iter=max_iter, decision_function_shape=decision_function_shape, break_ties=break_ties, random_state=random_state)
    
    
    #print (entrenamiento_datos, entrenamiento_clase)

    clasificador.fit (entrenamiento_datos, entrenamiento_clase)

    prediccion_prueba=clasificador.predict(prueba_datos)
    #print (prediccion_prueba)
    texto, disp=metricas (prueba_clase, prediccion_prueba, average=average)
    #return prueba_clase, prediccion_prueba
    return texto, disp, prediccion_prueba, clasificador



def clasificar_csv (ruta_entrada_entrenamiento, ruta_salida_prueba=None, 
ruta_salida_clasificador=None, ruta_salida_reporte=None, ruta_salida_imagen=None,columnas_interes=None,columna_clase = None, is_indexed=True, average='micro',

C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, 
class_weight=None, verbose=False, max_iter=- 1, decision_function_shape='ovr', break_ties=False, random_state=None
):

    dataset=funciones.cargar_csv(ruta_entrada_entrenamiento, is_indexed)

    if columna_clase == None:
        columna_clase=dataset.columns [-1]

    if columnas_interes == None:
        columnas_interes = dataset.columns
        columnas_interes.remove(columna_clase)

    else:
        columnas_interes = columnas_interes.split(",")

    entrenamiento_datos, prueba_datos, entrenamiento_clase, prueba_clase = train_test_split(dataset[columnas_interes], dataset[columna_clase], test_size=0.2)
    
    #prueba_clase, prediccion_prueba=clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, tipo_clasificar)
    texto, disp, prediccion_prueba, clasificador=clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, average=average, C=C, kernel=kernel, degree=degree, gamma=gamma, coef0=coef0, shrinking=shrinking, probability=probability, tol=tol, cache_size=cache_size, 
        class_weight=class_weight, verbose=verbose, max_iter=max_iter, decision_function_shape=decision_function_shape, break_ties=break_ties, random_state=random_state)
    #print(texto)
    funciones.guardar_csv (pd.DataFrame(prediccion_prueba, columns = ['clase']), ruta_entrada_entrenamiento, ruta_salida_prueba, prefijo="resultados_prueba")
    funciones.guardar_pickle (clasificador, ruta_entrada_entrenamiento, ruta_salida_clasificador, prefijo="clasificador")
    funciones.guardar_txt (texto, ruta_entrada_entrenamiento, ruta_salida_reporte, prefijo="reporte_entrenamiento")
    funciones.guardar_png (disp, ruta_entrada_entrenamiento, ruta_salida_imagen, prefijo="confusion")
    #disp.plot ()
    #return prueba_clase, prediccion_prueba


def parse_args():
    #Nombre y descicpicón del programa, se muestra desde consola con -h
    parser = argparse.ArgumentParser("normalizar", description="Funciones de normalización de datos con z-score o min-max. \n Los datos se normalizan con respecto a los valores propios del archivo .csv de entrada, o con los parámetros guardados en un archivo .pkl.")

    #Cada variable se necesita declara como posible entrada con la descripción a mostrarse si se ejecuta el comando -h, -- se usa cuando es una variable opción
    parser.add_argument("ruta_entrada_entrenamiento", help="Ruta completa de la ubicación del archivo con los datos a normalizar.",
                        type=str)

    parser.add_argument("--ruta_salida_prueba",
                        help="Ruta completa de la ubicación del archivo CSV de salida con los datos normalizados.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_clasificador",
                        help="Ruta completa de la ubicación del archivo CSV de salida con los datos normalizados.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_reporte",
                        help="Ruta completa de la ubicación del archivo CSV de salida con los datos normalizados.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_imagen",
                        help="Ingrese cualquiera de las dos opciones (z-score por defecto): \n z-score \n min-max",
                        type=str, nargs='?', default=None)


    parser.add_argument("--columnas_interes",
                        help="Nombre de las columnas que que se utilizaran para generar el modelo. Por defecto son todas menos la columna de clase",
                        type=str, nargs='?', default=None)
    parser.add_argument("--columna_clase",
                        help="Ingrese cualquiera de las dos opciones (z-score por defecto): \n z-score \n min-max",
                        type=str, nargs='?', default=None)
    parser.add_argument("--is_indexed",
                        help="Es necesario que los datos del archivo .CSV estén indexados en la primer columna, en caso de que no lo estén, ingrese --is_indexed=False para asignar uno en automático. --is_indexed=True por defecto",
                        type=str, nargs='?', default="True")###
    parser.add_argument("--average",
                        help="Ingrese cualquiera de las dos opciones (z-score por defecto): \n z-score \n min-max",
                        type=str, nargs='?', default='micro')
    parser.add_argument("--C", help="C, default=1.0",
						type=float, nargs="?", default=1.0)
    parser.add_argument("--kernel", help="kernel, default='rbf'",
						type=str, nargs="?", default='rbf')
    parser.add_argument("--degree", help="degree, default=3",
                        type=int, nargs="?", default=3)
    parser.add_argument("--gamma", help="gamma, default='scale'",
                        type=str, nargs="?", default='scale')
    parser.add_argument("--coef0", help="coef0, default=0.0",
                        type=float, nargs="?", default=0.0)
    parser.add_argument("--shrinking", help="shrinking, default=True",
                        type=str, nargs="?", default="True")###
    parser.add_argument("--probability", help="probability, default=False",
                        type=str, nargs="?", default='False')##
    parser.add_argument("--tol", help="tol, default=0.001",
                        type=float, nargs="?", default=0.001)
    parser.add_argument("--cache_size", help="cache_size, default=200",
                        type=int, nargs="?", default=200)
    parser.add_argument("--class_weight", help="class_weight, default=None",
                        type=int, nargs="?", default=None)
    parser.add_argument("--verbose", help="verbose, default=False",
                        type=str, nargs="?", default='False')###
    parser.add_argument("--max_iter", help="max_iter, default=- 1",
                        type=int, nargs="?", default=- 1)
    parser.add_argument("--decision_function_shape", help="decision_function_shape, default='ovr'",
                        type=str, nargs="?", default='ovr')
    parser.add_argument("--break_ties", help="break_ties, default=False",
                        type=str, nargs="?", default='False')###
    parser.add_argument("--random_state", help="random_state, default=None",
                        type=int, nargs="?", default=None)

    return parser.parse_args()

#main 
if __name__ == "__main__":
    options = parse_args()
    #print (options)
    clasificar_csv (options.ruta_entrada_entrenamiento, options.ruta_salida_prueba,
        options.ruta_salida_clasificador, options.ruta_salida_reporte, options.ruta_salida_imagen, options.columnas_interes,options.columna_clase,
        strtobool(options.is_indexed), options.average, 
        options.C, options.kernel, options.degree, options.gamma, options.coef0, strtobool(options.shrinking), strtobool(options.probability), 
        options.tol, options.cache_size, options.class_weight, strtobool(options.verbose), options.max_iter, 
        options.decision_function_shape, strtobool(options.break_ties), options.random_state )



