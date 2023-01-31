# Tratamiento de datos
# ==============================================================================
from cProfile import label
import pandas as pd
import numpy as np

# Gráficos
# ==============================================================================
import matplotlib.pyplot as plt
from matplotlib import style

# Preprocesado y modelado
# ==============================================================================
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
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
var_x=sys.argv[3]
var_y=sys.argv[4].split(",")
ALPHA=float(sys.argv[5])
#optional
FILTTER_COLUMN=sys.argv[6]
FILTTER_VALUE=sys.argv[7].split(",") #array

datos = pd.read_csv(INPUT_PATH)



# Funcion para procesar la regresion linear , produce el modelo, la grafica y el reporte
# ==============================================================================
def REG(datos,var_x,list_var_y,alpha,outputpath,sufijo=""): 
    FIGSIZE=(8, 5.84)
    var_alpha=ALPHA
    fig, ax = plt.subplots(figsize=FIGSIZE)
    CI = (1-var_alpha) * 100
    first_var=False
    for var_y in list_var_y: 
        try:
            # quitar nulos y camiar valores de 0 a nulo
            # ==============================================================================
            datos.replace(to_replace=0, value=np.nan,inplace=True)
            datos.dropna(subset=[var_y,var_x],inplace=True)

            # Correlación lineal entre las dos variables
            # ==============================================================================
            corr_test = pearsonr(x = datos[var_x], y =  datos[var_y])

            # División de los datos en train y test
            # ==============================================================================
            X = datos[[var_x]]
            y = datos[var_y]
            print(X)
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
            modelo = sm.OLS(endog=y_train, exog=X_train,)
            modelo = modelo.fit()

            # Intervalos de confianza para los coeficientes del modelo
            # ==============================================================================
            modelo.conf_int(alpha=var_alpha)

            # Predicciones con intervalo de confianza del 95%
            # ==============================================================================
            predicciones = modelo.get_prediction(exog = X_train).summary_frame(alpha=var_alpha)
            predicciones.head(4)


            # Predicciones con intervalo de confianza del 95%
            # ==============================================================================
            print("----")
            predicciones['x'] = X_train[:, 1]
            predicciones['y'] = y_train
            predicciones = predicciones.sort_values('x')

            # Error de test del modelo 
            # ==============================================================================
            X_test = sm.add_constant(X_test, prepend=True)
            predicciones_test = modelo.predict(exog = X_test)
            rmse = mean_squared_error(
                    y_true  = y_test,
                    y_pred  = predicciones_test,
                    squared = False
                )

            # REPORT
            # ==============================================================================
            f = open("%s/%s_report.txt"% (outputpath,sufijo),"a")
            f.write("RESULTS OF REGRESSION OF %s and %s \n\n" %(var_x,var_y))
            f.write("RMSE: %s\n" % rmse)
            f.write("MODEL: %s \n" % modelo.summary())
            f.write("Pearson: %s\n" %corr_test[0])
            f.write("P-value: %s\n" %corr_test[1])
            f.close()

            # SAVE MODEL
            # ==============================================================================
            pickle.dump(modelo, open("%s/%s_RegressionModel.pkl" %(outputpath,sufijo), 'wb'))


            # Gráfico del modelo
            # ==============================================================================
            if first_var:
                line_color="-k"
                first_var=False
            else:
                line_color="-"

            ax.scatter(predicciones['x'], predicciones['y'], marker='o')
            ax.plot(predicciones['x'], predicciones["mean"], linestyle=line_color, label="OLS %s" %var_y )
            #ax.plot(predicciones['x'], predicciones["mean_ci_lower"], linestyle='--', color='red', label="%s% CI" %(CI))
            #ax.plot(predicciones['x'], predicciones["mean_ci_upper"], linestyle='--', color='red')
            #ax.fill_between(predicciones['x'], predicciones["mean_ci_lower"], predicciones["mean_ci_upper"], alpha=0.1)
        except Exception as e:
            print("fallo en algo, se ignoro",e) 

    ax.legend();
    ax.set_title("%s REGRESSION" %(sufijo))
    ax.set_xlabel(var_x)
    #ax.set_ylabel(var_y)

    plt.savefig("%s/%s_RegressionGraph.png" %(outputpath,sufijo), dpi=200)
    plt.clf()


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


