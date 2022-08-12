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
        hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', 
        learning_rate_init=0.001, power_t=0.5, max_iter=200, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, 
        momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, 
        n_iter_no_change=10, max_fun=15000):
  

    clasificador = sk.neural_network.MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, activation=activation, solver=solver, 
        alpha=alpha, batch_size=batch_size, learning_rate=learning_rate, learning_rate_init=learning_rate_init, power_t=power_t,
        max_iter=max_iter, shuffle=shuffle, random_state=random_state, tol=tol, verbose=verbose, warm_start=warm_start, 
        momentum=momentum, nesterovs_momentum=nesterovs_momentum, early_stopping=early_stopping, validation_fraction=validation_fraction,
         beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, n_iter_no_change=n_iter_no_change, max_fun=max_fun)
    
    
    clasificador.fit (entrenamiento_datos, entrenamiento_clase)

    prediccion_prueba=clasificador.predict(prueba_datos)
    
    texto, disp=metricas (prueba_clase, prediccion_prueba, average)
    
    return texto, disp, prediccion_prueba, clasificador



def clasificar_csv (ruta_entrada_entrenamiento, ruta_salida_prueba=None, 
        ruta_salida_clasificador=None, ruta_salida_reporte=None, ruta_salida_imagen=None,columnas_interes=None,columna_clase = None, is_indexed=True, average='micro',

        hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', 
        learning_rate_init=0.001, power_t=0.5, max_iter=200, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, 
        momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, 
        n_iter_no_change=10, max_fun=15000):

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

    #entrenamiento, prueba = train_test_split(entrenamiento, test_size=0.2)
    entrenamiento_datos, prueba_datos, entrenamiento_clase, prueba_clase = train_test_split(dataset[columnas_interes], dataset[columna_clase], test_size=0.2)
    
    texto, disp, prediccion_prueba, clasificador=clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, average,
        hidden_layer_sizes=hidden_layer_sizes, activation=activation, solver=solver, alpha=alpha, batch_size=batch_size, learning_rate=learning_rate, 
        learning_rate_init=learning_rate_init, power_t=power_t, max_iter=max_iter, shuffle=shuffle, random_state=random_state, tol=tol, verbose=verbose, warm_start=warm_start, 
        momentum=momentum, nesterovs_momentum=nesterovs_momentum, early_stopping=early_stopping, validation_fraction=validation_fraction, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, 
        n_iter_no_change=n_iter_no_change, max_fun=max_fun)

    #print(texto)
    funciones.guardar_csv (pd.DataFrame(prediccion_prueba, columns = ['clase']), ruta_entrada_entrenamiento, ruta_salida_prueba, prefijo="resultados_prueba")
    funciones.guardar_pickle (clasificador, ruta_entrada_entrenamiento, ruta_salida_clasificador, prefijo="clasificador")
    funciones.guardar_txt (texto, ruta_entrada_entrenamiento, ruta_salida_reporte, prefijo="reporte_entrenamiento")
    funciones.guardar_png (disp, ruta_entrada_entrenamiento, ruta_salida_imagen, prefijo="confusion")
    #disp.plot ()
    #return prueba_clase, prediccion_prueba

def tuple_type(strings):
    strings = strings.replace("(", "").replace(")", "")
    mapped_int = map(int, strings.split(","))
    return tuple(mapped_int)

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
                        type=str, nargs='?', default="True")
    parser.add_argument("--average",
                        help="para la función de evaluación basada en sk.metrics.precision_score, etc. con la que se genera el reporte del entrenamiento, average{‘micro’, ‘macro’, ‘samples’, ‘weighted’, ‘binary’} or None, default=’binary’",
                        type=str, nargs='?', default='micro')

    parser.add_argument("--hidden_layer_sizes", help="hidden_layer_sizes, default=(100,)",
                        type=str, default="(100,)")#tuple
    parser.add_argument("--activation", help="activation, default='relu'",
                        type=str, nargs="?", default='relu')
    parser.add_argument("--solver", help="solver, default='adam'",
                        type=str, nargs="?", default='adam')
    parser.add_argument("--alpha", help="alpha, default=0.0001",
                        type=float, nargs="?", default=0.0001)
    parser.add_argument("--batch_size", help="batch_size, default='auto'",
                        type=str, nargs="?", default='auto')###int
    parser.add_argument("--learning_rate", help="learning_rate, default='constant'",
                        type=str, nargs="?", default='constant')
    parser.add_argument("--learning_rate_init", help="learning_rate_init, default=0.001",
                        type=float, nargs="?", default=0.001)
    parser.add_argument("--power_t", help="power_t, default=0.5",
                        type=float, nargs="?", default=0.5)
    parser.add_argument("--max_iter", help="max_iter, default=200",
                        type=int, nargs="?", default=200)
    parser.add_argument("--shuffle", help="shuffle, default=True",
                        type=str, nargs="?", default="True")###bool
    parser.add_argument("--random_state", help="random_state, default=None",
                        type=int, nargs="?", default=None)
    parser.add_argument("--tol", help="tol, default=0.0001",
                        type=float, nargs="?", default=0.0001)
    parser.add_argument("--verbose", help="verbose, default=False",
                        type=str, nargs="?", default="False")###bool
    parser.add_argument("--warm_start", help="warm_start, default=False",
                        type=str, nargs="?", default="False")##bool
    parser.add_argument("--momentum", help="momentum, default=0.9",
                        type=float, nargs="?", default=0.9)
    parser.add_argument("--nesterovs_momentum", help="nesterovs_momentum, default=True",
                        type=str, nargs="?", default="True")###bool
    parser.add_argument("--early_stopping", help="early_stopping, default=False",
                        type=str, nargs="?", default="False")###bool
    parser.add_argument("--validation_fraction", help="validation_fraction, default=0.1",
                        type=float, nargs="?", default=0.1)
    parser.add_argument("--beta_1", help="beta_1, default=0.9",
                        type=float, nargs="?", default=0.9)
    parser.add_argument("--beta_2", help="beta_2, default=0.999",
                        type=float, nargs="?", default=0.999)
    parser.add_argument("--epsilon", help="epsilon, default=1e-08",
                        type=float, nargs="?", default=1e-08)
    parser.add_argument("--n_iter_no_change", help="n_iter_no_change, default=10",
                        type=int, nargs="?", default=10)
    parser.add_argument("--max_fun", help="max_fun, default=15000",
                        type=int, nargs="?", default=15000)

    return parser.parse_args()

#main 
if __name__ == "__main__":
    options = parse_args()
    print (eval(options.hidden_layer_sizes))
    clasificar_csv (options.ruta_entrada_entrenamiento, options.ruta_salida_prueba,
        options.ruta_salida_clasificador, options.ruta_salida_reporte, options.ruta_salida_imagen, options.columnas_interes ,options.columna_clase,
        strtobool(options.is_indexed), options.average,
        eval(options.hidden_layer_sizes), options.activation, options.solver, options.alpha, options.batch_size, 
        options.learning_rate, options.learning_rate_init, options.power_t, options.max_iter, bool(strtobool(options.shuffle)), 
        options.random_state, options.tol, bool(strtobool(options.verbose)), options.warm_start, options.momentum, 
        bool(strtobool(options.nesterovs_momentum)), bool(strtobool(options.early_stopping)), options.validation_fraction, options.beta_1, 
        options.beta_2, options.epsilon, options.n_iter_no_change, options.max_fun)





#clasificar_csv ("data/entrenamiento_balanceado_output.csv", "data/prueba_balanceado_output.csv", tipo_clasificar="GaussianNB")