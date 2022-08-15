import funciones
import argparse
from distutils.util import strtobool
#import re

from sklearn.neural_network import MLPClassifier
#from sklearn import metrics
#from sklearn import neighbors
import sklearn as sk
import numpy as np
#import matplotlib as plt
import pandas as pd

from sklearn.model_selection import train_test_split

def metricas (prueba_clase, prediccion_prueba, average='micro'):
    # y_true=prueba_clase.flatten().astype('int')
    # y_pred=prediccion_prueba.astype('int')

    texto=""

    y_true=prueba_clase#.values.ravel()
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

#def clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, average='micro',
#        C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, 
#        class_weight=None, verbose=False, max_iter=- 1, decision_function_shape='ovr', break_ties=False, random_state=None,
#        ):

#prueba_datos ya no es necesaria
def clasificar (entrenamiento_datos, entrenamiento_clase, average='micro',
    hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', 
    learning_rate_init=0.001, power_t=0.5, max_iter=200, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, 
    momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, 
    n_iter_no_change=10, max_fun=15000):


    clasificador = sk.neural_network.MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, activation=activation, solver=solver, 
        alpha=alpha, batch_size=batch_size, learning_rate=learning_rate, learning_rate_init=learning_rate_init, power_t=power_t,
        max_iter=max_iter, shuffle=shuffle, random_state=random_state, tol=tol, verbose=verbose, warm_start=warm_start, 
        momentum=momentum, nesterovs_momentum=nesterovs_momentum, early_stopping=early_stopping, validation_fraction=validation_fraction,
         beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, n_iter_no_change=n_iter_no_change, max_fun=max_fun)

    
    
    #print (entrenamiento_datos, entrenamiento_clase)

    clasificador_entrenado=clasificador
    clasificador_entrenado.fit (entrenamiento_datos, entrenamiento_clase)

    #prediccion_prueba=clasificador.predict(prueba_datos)
    #print (prediccion_prueba)
    #texto, disp=metricas (prueba_clase, prediccion_prueba, average=average)
    #return prueba_clase, prediccion_prueba
    
    #return texto, disp, prediccion_prueba, clasificador
    return clasificador_entrenado, clasificador

def clasificar_csv (ruta_entrada_entrenamiento,
    ruta_salida_clasificador=None, ruta_salida_reporte=None, ruta_salida_imagen_confusion=None, ruta_salida_imagen_densidad=None, ruta_salida_imagen_cajas=None,
    columnas_interes=None,columna_clase = None, num_iteraciones=5, is_indexed=True, average='micro',

    hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant', 
    learning_rate_init=0.001, power_t=0.5, max_iter=200, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False, 
    momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08, 
    n_iter_no_change=10, max_fun=15000):

    datos_entrada=funciones.cargar_csv(ruta_entrada_entrenamiento, is_indexed)

    if columna_clase == None:
        columna_clase=datos_entrada.columns [-1]

    if columnas_interes == None:
        #columnas_interes = datos_entrada.columns
        columnas_interes = datos_entrada.columns.to_list()
        columnas_interes.remove(columna_clase)
    else:
        columnas_interes = columnas_interes.split(",")

    entrenamiento_datos=datos_entrada[columnas_interes]
    entrenamiento_clase=datos_entrada[columna_clase]
    columnas_datos_clase=columnas_interes.copy()
    columnas_datos_clase.append(columna_clase)
    datos_clase=datos_entrada [columnas_datos_clase]

    #prueba_clase, prediccion_prueba=clasificar (entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase, tipo_clasificar)
    clasificador_entrenado, clasificador=clasificar (entrenamiento_datos, entrenamiento_clase, average=average,

        hidden_layer_sizes=hidden_layer_sizes, activation=activation, solver=solver, alpha=alpha, batch_size=batch_size, learning_rate=learning_rate, 
        learning_rate_init=learning_rate_init, power_t=power_t, max_iter=max_iter, shuffle=shuffle, random_state=random_state, tol=tol, verbose=verbose, warm_start=warm_start, 
        momentum=momentum, nesterovs_momentum=nesterovs_momentum, early_stopping=early_stopping, validation_fraction=validation_fraction, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon, 
        n_iter_no_change=n_iter_no_change, max_fun=max_fun)

    #print(texto)
    
    metricas_acumuladas, texto, disp=bootstrap (clasificador, datos_clase, columna_clase, num_iteraciones, average=average)

    #metricas_acumuladas.plot.density()
    #plt.show()
    #metricas_acumuladas.boxplot()
    #plt.show()

    #funciones.guardar_csv (pd.DataFrame(prediccion_prueba, columns = ['clase']), ruta_entrada_entrenamiento, ruta_salida_prueba, prefijo="resultados_prueba")
    funciones.guardar_pickle (clasificador_entrenado, ruta_entrada_entrenamiento, ruta_salida_clasificador, prefijo="clasificador")
    funciones.guardar_txt (texto, ruta_entrada_entrenamiento, ruta_salida_reporte, prefijo="reporte_entrenamiento")
    funciones.guardar_png (disp, ruta_entrada_entrenamiento, ruta_salida_imagen_confusion, prefijo="confusion")
    funciones.density_png (metricas_acumuladas, ruta_entrada_entrenamiento, ruta_salida_imagen_densidad, prefijo="densidad")
    funciones.boxplot_png (metricas_acumuladas, ruta_entrada_entrenamiento, ruta_salida_imagen_cajas, prefijo="boxplot")
    #disp.plot ()
    #return prueba_clase, prediccion_prueba

#return texto, disp, prediccion_prueba, clasificador

#def metricas_bootstrap (datos_entrada):
#    #return pres, rec, acc, f1
#    pass

def metricas_bootStrap (prueba_clase, prediccion_prueba):

    y_true=prueba_clase.flatten()#.astype('int')
    y_pred=prediccion_prueba#.astype('int')

    pres=sk.metrics.precision_score(y_true, y_pred, average='macro')
    rec=sk.metrics.recall_score(y_true, y_pred, average='macro')
    acc=sk.metrics.accuracy_score(y_true, y_pred)
    f1=sk.metrics.f1_score(y_true, y_pred, average='macro')
    return pres, rec, acc, f1

def bootstrap_split (datosEntrada):
    entrenamiento=datosEntrada.sample(n=len(datosEntrada.index),replace=True)
    try:
        prueba=(entrenamiento.merge(datosEntrada, how='right', indicator=True)
        .query('_merge == "right_only"')
        .drop('_merge', 1))
    except Exception as e:
        print()
    return entrenamiento, prueba

def bootstrap_split_datos_clase (datos_entrada, columna_clase):
    entrenamiento, prueba = bootstrap_split(datos_entrada)

    entrenamiento_datos=entrenamiento.drop(columna_clase, axis='columns').to_numpy()
    entrenamiento_clase=entrenamiento[[columna_clase]].to_numpy()
    
    #entrenamiento_datos=entrenamiento [["edadRecalc", "hba1c", "imc", "HOMA2 %B'", "HOMA2 IR'"]].to_numpy()
    #entrenamiento_clase=(entrenamiento [["clase"]]-1).to_numpy()

    prueba_datos=prueba.drop(columna_clase, axis='columns').to_numpy()
    prueba_clase=prueba[[columna_clase]].to_numpy()

    #prueba_datos=prueba [["edadRecalc", "hba1c", "imc", "HOMA2 %B'", "HOMA2 IR'"]].to_numpy()
    #prueba_clase=(prueba [["clase"]]-1).to_numpy()

    return entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase


#def bootstrap (clasificador, datos_entrada, num_iteraciones, epocs=None):   ###Para ANN
def bootstrap (clasificador, datos_entrada, columna_clase, num_iteraciones, average):
    for i in range (num_iteraciones):
        print (i)
        entrenamiento_datos, entrenamiento_clase, prueba_datos, prueba_clase = bootstrap_split_datos_clase (datos_entrada, columna_clase)
        
        clasificador.fit (entrenamiento_datos, entrenamiento_clase)
        prediccion_prueba=clasificador.predict(prueba_datos)
        pres, rec, acc, f1=metricas_bootStrap (prueba_clase, prediccion_prueba)
        if i==0:
            prueba_clase_acumulado=prueba_clase
            prediccion_prueba_acumulado=prediccion_prueba

            pres_acumulado=pres
            rec_acumulado=rec
            acc_acumulado=acc
            f1_acumulado=f1
        else:
            prueba_clase_acumulado=np.append(prueba_clase_acumulado, prueba_clase)
            prediccion_prueba_acumulado=np.append(prediccion_prueba_acumulado, prediccion_prueba)

            pres_acumulado=np.append (pres_acumulado, pres)
            rec_acumulado=np.append (rec_acumulado, rec)
            acc_acumulado=np.append (acc_acumulado, acc)
            f1_acumulado=np.append (f1_acumulado, f1)
    metricas_acumuladas=pd.DataFrame ()
    metricas_acumuladas["pres_acumulado"]=pres_acumulado
    metricas_acumuladas["rec_acumulado"]=rec_acumulado
    metricas_acumuladas["acc_acumulado"]=acc_acumulado
    metricas_acumuladas["f1_acumulado"]=f1_acumulado
    print ("\n\n\n\n1______________", metricas_acumuladas.columns.to_list(), "\n\n\n\n")
    print ("\n\n\n\n2______________", prueba_clase_acumulado, "\n\n\n\n")
    print ("\n\n\n\n3______________", prediccion_prueba_acumulado, "\n\n\n\n")
    texto, disp=metricas (prueba_clase_acumulado, prediccion_prueba_acumulado, average)

    return metricas_acumuladas, texto, disp



#def bootstrap_csv (datos_entrada, clasificador, ruta_entrada, ruta_salida):
#    metricas_acumuladas=bootstrap(datos_entrada)
#    funciones.guardar_csv(datos_entrada, ruta_entrada, ruta_salida)
#    #return metricas_acumuladas
#    pass

# main 
#clasificador, datos_entrada, ruta_entrada, ruta_salida_imagen, ruta_salida=None

#metricas_acumuladas=bootstrap_csv(clasificador, datos_entrada, ruta_salida)
#funciones.graficar_png(metricas_acumuladas, ruta_entrada, ruta_salida_imagen)
#funciones.guardar_txt (metricas_acumuladas, ruta_entrada, ruta_salida)





def parse_args():
    #Nombre y descicpicón del programa, se muestra desde consola con -h
    parser = argparse.ArgumentParser("normalizar", description="Funciones de normalización de datos con z-score o min-max. \n Los datos se normalizan con respecto a los valores propios del archivo .csv de entrada, o con los parámetros guardados en un archivo .pkl.")

    #Cada variable se necesita declara como posible entrada con la descripción a mostrarse si se ejecuta el comando -h, -- se usa cuando es una variable opción
    parser.add_argument("ruta_entrada_entrenamiento", help="Ruta completa de la ubicación del archivo con los datos para entrenar el modelo.",
                        type=str)

#Parámetro eliminado

    #parser.add_argument("--ruta_salida_prueba",
    #                    help="Ruta completa de la ubicación del archivo CSV de salida con los datos normalizados.",
    #                    type=str, nargs='?', default=None)
    
    parser.add_argument("--ruta_salida_clasificador",
                        help="Ruta completa de la ubicación del archivo pkl de salida con el modelo entrenado.",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_reporte",
                        help="Ruta completa de la ubicación del archivo txt de salida del reporte.",
                        type=str, nargs='?', default=None)

#--ruta_salida_imagen ahora son 3 nuevos parámetros:
    parser.add_argument("--ruta_salida_imagen_confusion",
                        help="ruta salida del reporte de salida en png, por defecto se usa la ruta de los datos de entrada",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_imagen_densidad",
                        help="ruta salida del reporte de salida en png, por defecto se usa la ruta de los datos de entrada",
                        type=str, nargs='?', default=None)
    parser.add_argument("--ruta_salida_imagen_cajas",
                        help="ruta salida del reporte de salida en png, por defecto se usa la ruta de los datos de entrada",
                        type=str, nargs='?', default=None)


    parser.add_argument("--columnas_interes",
                        help="Nombre de las columnas que que se utilizaran para generar el modelo. Por defecto son todas menos la columna de clase",
                        type=str, nargs='?', default=None)
    parser.add_argument("--columna_clase",
                        help="Indique la culumna que contiene las clases",
                        type=str, nargs='?', default=None)


#Nuevo parámetro:
    parser.add_argument("--num_iteraciones", help="Número de veces que se ejecutará el entrenamiento y evaluiación. Default=5",
                        type=int, nargs="?", default=5)

    parser.add_argument("--is_indexed",
                        help="Es necesario que los datos del archivo .CSV estén indexados en la primer columna, en caso de que no lo estén, ingrese --is_indexed=False para asignar uno en automático. --is_indexed=True por defecto",
                        type=str, nargs='?', default="False")###
    parser.add_argument("--average",
                        help="Tipo de evaluación, micro por defecto",
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
    #print (options)
    clasificar_csv (options.ruta_entrada_entrenamiento, 
        options.ruta_salida_clasificador, options.ruta_salida_reporte, 
        options.ruta_salida_imagen_confusion,options.ruta_salida_imagen_densidad,options.ruta_salida_imagen_cajas,
        options.columnas_interes,options.columna_clase,
        options.num_iteraciones,
        strtobool(options.is_indexed), options.average,
        eval(options.hidden_layer_sizes), options.activation, options.solver, options.alpha, options.batch_size, 
        options.learning_rate, options.learning_rate_init, options.power_t, options.max_iter, bool(strtobool(options.shuffle)), 
        options.random_state, options.tol, bool(strtobool(options.verbose)), options.warm_start, options.momentum, 
        bool(strtobool(options.nesterovs_momentum)), bool(strtobool(options.early_stopping)), options.validation_fraction, options.beta_1, 
        options.beta_2, options.epsilon, options.n_iter_no_change, options.max_fun)



    #clasificar_csv (options.ruta_entrada_entrenamiento, options.ruta_salida_prueba,
    #    options.ruta_salida_clasificador, options.ruta_salida_reporte, options.ruta_salida_imagen, options.columnas_interes ,options.columna_clase,
    #    strtobool(options.is_indexed), options.average,
    #    eval(options.hidden_layer_sizes), options.activation, options.solver, options.alpha, options.batch_size, 
    #    options.learning_rate, options.learning_rate_init, options.power_t, options.max_iter, bool(strtobool(options.shuffle)), 
    #    options.random_state, options.tol, bool(strtobool(options.verbose)), options.warm_start, options.momentum, 
    #    bool(strtobool(options.nesterovs_momentum)), bool(strtobool(options.early_stopping)), options.validation_fraction, options.beta_1, 
    #    options.beta_2, options.epsilon, options.n_iter_no_change, options.max_fun)