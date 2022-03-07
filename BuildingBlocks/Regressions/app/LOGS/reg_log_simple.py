# Tratamiento de datos
# ==============================================================================
import pandas as pd
import numpy as np

# Gráficos
# ==============================================================================
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns

# Preprocesado y modelado
# ==============================================================================
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.weightstats import ttest_ind

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
var_x=sys.argv[3] # variable constante
var_y=sys.argv[4] # varible binaria
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

    # quitar nulos 
    # ==============================================================================
    datos.dropna(subset=[var_y,var_x],inplace=True)

    # Correlación lineal entre las dos variables
    # Gráfico
    # ==============================================================================
    fig, ax = plt.subplots(figsize=(6, 3.84))

    sns.violinplot(
            x     = var_y,
            y     = var_x,
            data  = datos,
            #color = "white",
            ax    = ax
        )
    ax.set_title('Distribution by class');
    plt.savefig("%s/%s_DistributionLogRegGraph.png" %(outputpath,sufijo), dpi=200)
    plt.clf()

    # codificar clases como 0 y 1
    # ==============================================================================
    lista_clases = datos[var_y].unique()
    datos[var_y] = np.where(datos[var_y] == lista_clases[0], 1, 0)
    
    # T-test entre clases
    # ==============================================================================
    class1 = datos[datos[var_y]==0]
    class2 = datos[datos[var_y]==1]

    res_ttest = ttest_ind(
                    x1 = class1,
                    x2 = class2,
                    alternative='two-sided'
                )

    # División de los datos en train y test
    # ==============================================================================
    X = datos[[var_x]]
    y = datos[var_y]
    X_train, X_test, y_train, y_test = train_test_split(
                                            X.values.reshape(-1,1),
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

    # Intervalos de confianza para los coeficientes del modelo
    # ==============================================================================
    intervalos_ci = modelo.conf_int(alpha=var_alpha)
    intervalos_ci = pd.DataFrame(intervalos_ci)
    intervalos_ci.columns = ['2.5%', '97.5%']


    # Predicción de probabilidades
    # ==============================================================================
    #predicciones = modelo.predict(exog = X_train)
    #predicciones[:4]
    # Clasificación predicha
    # ==============================================================================
    #clasificacion = np.where(predicciones<0.5, 0, 1)
    #clasificacion

    # Predicciones en todo el rango de X
    # ==============================================================================
    # Se crea un vector con nuevos valores interpolados en el rango de observaciones.
    grid_X = np.linspace(
                start = min(datos[var_x]),
                stop  = max(datos[var_x])
            ).reshape(-1,1)

    grid_X = sm.add_constant(grid_X, prepend=True)
    predicciones = modelo.predict(exog = grid_X)

    # Gráfico del modelo
    # ==============================================================================
    fig, ax = plt.subplots(figsize=(6, 3.84))

    ax.scatter(
        X_train[(y_train == 1).flatten(), 1],
        y_train[(y_train == 1).flatten()].flatten()
    )
    ax.scatter(
        X_train[(y_train == 0).flatten(), 1],
        y_train[(y_train == 0).flatten()].flatten()
    )
    ax.plot(grid_X[:, 1], predicciones, color = "gray")
    ax.set_title("Logistic regression model")
    ax.set_ylabel("P(%s | %s)" %(var_y,var_x))
    ax.set_xlabel(var_x);
    plt.savefig("%s/%s_LogRegressionGraph.png" %(outputpath,sufijo), dpi=200)
    plt.clf()


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
    print(f"\nEl accuracy de test es: {100*accuracy}%")

    # REPORT
    # ==============================================================================
    f = open("%s/%s_report.txt"% (outputpath,sufijo),"w")
    f.write("RESULTS OF REGRESSION OF %s and %s \n" %(var_x,var_y))
    f.write("\n Accuracy: %s" % (100*accuracy))
    f.write("\n MODEL: \n %s " % modelo.summary())
    f.write("\n Intervals: \n %s " % intervalos_ci)
    f.write("\n t=%s, P-value=%s" %(res_ttest[0],res_ttest[1]))
    f.close()

    # SAVE MODEL
    # ==============================================================================
    pickle.dump(modelo, open("%s/%s_LogisticRegressionModel.pkl" %(outputpath,sufijo), 'wb'))

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
            REG(data_temp,var_x,var_y,ALPHA,OUTPUT_PATH,sufijo=fv)

else: #no se van a filtrar datos, pasan directo
    REG(datos,var_x,var_y,ALPHA,OUTPUT_PATH)


