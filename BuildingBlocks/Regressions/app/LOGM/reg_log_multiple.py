# Tratamiento de datos
# ==============================================================================
import pandas as pd
import numpy as np
import math
# Gráficos
# ==============================================================================
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns

# Preprocesado y modelado
# ==============================================================================
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,classification_report
from sklearn.metrics import plot_confusion_matrix
import statsmodels.api as sm
import statsmodels.formula.api as smf

# for dumping
# ==============================================================================
import pickle 
import sys

# Configuración matplotlib
# ==============================================================================
plt.rcParams['image.cmap'] = "bwr"
#plt.rcParams['figure.dpi'] = "100"
plt.rcParams['savefig.bbox'] = "tight"
style.use('ggplot') or plt.style.use('ggplot')

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

# Variables de entrada
# ==============================================================================

INPUT_PATH = sys.argv[1] #path of the csv file
OUTPUT_PATH = sys.argv[2]
var_x_list=sys.argv[3].split(",") #variables constantes
var_y=sys.argv[4] #variable binaria
ALPHA=float(sys.argv[5])
#optional
FILTTER_COLUMN=sys.argv[6]
FILTTER_VALUE=sys.argv[7].split(",") #array

datos = pd.read_csv(INPUT_PATH)



# Funcion para procesar la regresion linear , produce el modelo, la grafica y el reporte
# ==============================================================================
def REG(datos,var_x,var_y,alpha,outputpath,sufijo=""): 
    FIGSIZE=(8, 5.84)
    var_alpha=ALPHA
    cantidad_prediciones= 4
    list_var = var_x+[var_y]
    n_var= len(list_var)

    # quitar nulos y camiar valores de 0 a nulo
    # ==============================================================================
    datos.dropna(subset=list_var,inplace=True)

    # codificar clases como 0 y 1
    # ==============================================================================
    lista_clases = datos[var_y].unique()
    datos[var_y] = np.where(datos[var_y] == lista_clases[0], 1, 0)

    print("Número de observaciones por clase")
    print(datos[var_y].value_counts())
    print("")

    print("Porcentaje de observaciones por clase")
    print(100 * datos[var_y].value_counts(normalize=True))

    # División de los datos en train y test
    # ==============================================================================
    X = datos[var_x]
    y = datos[var_y]
    X_train, X_test, y_train, y_test = train_test_split(
                                            X,
                                            y.values.reshape(-1,1),
                                            train_size   = 0.8,
                                            random_state = 1234,
                                            shuffle      = True
                                        )

    # Creación del modelo utilizando matrices como en scikitlearn
    # ==============================================================================
    # A la matriz de predictores se le tiene que añadir una columna de 1s para el intercept del modelo
    X_train = sm.add_constant(X_train, prepend=True)
    modelo = sm.Logit(endog=y_train, exog=X_train,)
    modelo = modelo.fit()

    # Accuracy de test del modelo 
    # ==============================================================================
    X_test = sm.add_constant(X_test, prepend=True)
    predicciones = modelo.predict(exog = X_test)
    clasificacion = np.where(predicciones<0.5, 0, 1)
    accuracy = accuracy_score(
                y_true    = y_test,
                y_pred    = clasificacion,
                normalize = True
            )
    print(f"El accuracy de test es: {100*accuracy}%")

    # Matriz de confusión de las predicciones de test
    # ==============================================================================
    confusion_matrix = pd.crosstab(
        y_test.ravel(),
        clasificacion,
        rownames=['Real'],
        colnames=['Predicted value']
    )


    # REPORT
    # ==============================================================================
    f = open("%s/%s_RLM_report.txt"% (outputpath,sufijo),"w")
    f.write("RESULTS OF MULTIPLE LOGARITMIC REGRESSION OF %s and %s \n" %(var_x,var_y))
    f.write("\n Accuracy: %s" % (100*accuracy))
    f.write("\n MODEL:\n  %s " % modelo.summary())
    f.write("\n REPORT: \n %s " % classification_report(y_test, clasificacion))
    f.write("\n CONFUSSION MATRIX: \n %s " % confusion_matrix )
    f.close()

    # SAVE MODEL
    # ==============================================================================
    pickle.dump(modelo, open("%s/%s_LogRegressionModel.pkl" %(outputpath,sufijo), 'wb'))

# Filtrar datos en base a un valor o multiples valores en una columna
# ==============================================================================
if FILTTER_COLUMN != "":
    print("filtter...")
    if FILTTER_VALUE[0]=="":
        FILTTER_VALUE = datos[FILTTER_COLUMN].unique()
    print(FILTTER_VALUE)


    for fv in FILTTER_VALUE:
        data_temp = datos[datos[FILTTER_COLUMN]==fv]
        if len(data_temp)>1:
            REG(data_temp,var_x_list,var_y,ALPHA,OUTPUT_PATH,sufijo=fv)

else: #no se van a filtrar datos, pasan directo
    REG(datos,var_x_list,var_y,ALPHA,OUTPUT_PATH)


