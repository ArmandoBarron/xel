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
from scipy.stats import normaltest,shapiro
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


# Correlación entre columnas numéricas
# ==============================================================================

def tidy_corr_matrix(corr_mat):
    '''
    Función para convertir una matriz de correlación de pandas en formato tidy
    '''
    corr_mat = corr_mat.stack().reset_index()
    corr_mat.columns = ['variable_1','variable_2','r']
    corr_mat = corr_mat.loc[corr_mat['variable_1'] != corr_mat['variable_2'], :]
    corr_mat['abs_r'] = np.abs(corr_mat['r'])
    corr_mat = corr_mat.sort_values('abs_r', ascending=False)
    
    return(corr_mat)


# Variables de entrada
# ==============================================================================


INPUT_PATH = sys.argv[1] #path of the csv file
OUTPUT_PATH = sys.argv[2]
var_x_list=sys.argv[3].split(",")
var_y=sys.argv[4]
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
    datos.replace(to_replace=0, value=np.nan,inplace=True)
    datos.dropna(subset=list_var,inplace=True)

    # Correlación lineal entre las variables
    # ==============================================================================

    corr_matrix = datos[list_var].corr(method='pearson')
    tidy_corr_matrix(corr_matrix).head(10) #imprimir la matriz

    # Heatmap matriz de correlaciones
    # ==============================================================================
    fig, ax  = plt.subplots(nrows=1, ncols=1, figsize=(n_var,n_var))

    sns.heatmap(
        corr_matrix,
        annot     = True,
        cbar      = False,
        annot_kws = {"size": 8},
        vmin      = -1,
        vmax      = 1,
        center    = 0,
        cmap      = sns.diverging_palette(20, 220, n=200),
        square    = True,
        ax        = ax
    )
    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation = 45,
        horizontalalignment = 'right',
    )
    ax.tick_params(labelsize = 10)
    plt.savefig("%s/%s_correlation.png" %(outputpath,sufijo), dpi=200)
    plt.clf()

    # Gráfico de distribución para cada variable numérica
    # ==============================================================================
    # Ajustar número de subplots en función del número de columnas
    fig, axes = plt.subplots(nrows=math.ceil(n_var/3), ncols=3, figsize=(9, 5))
    axes = axes.flat
    columnas_numeric = datos[list_var].columns
    for i, colum in enumerate(columnas_numeric):
        sns.histplot(
            data    = datos,
            x       = colum,
            stat    = "count",
            kde     = True,
            color   = (list(plt.rcParams['axes.prop_cycle'])*2)[i]["color"],
            line_kws= {'linewidth': 2},
            alpha   = 0.3,
            ax      = axes[i]
        )
        axes[i].set_title(colum, fontsize = 7, fontweight = "bold")
        axes[i].tick_params(labelsize = 8)
        axes[i].set_xlabel("")

    fig.tight_layout()
    plt.subplots_adjust(top = 0.9)
    fig.suptitle('DISTRIBUTIONS', fontsize = 10, fontweight = "bold");
    plt.savefig("%s/%s_distribution.png" %(outputpath,sufijo), dpi=200)
    plt.clf()

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
    modelo = sm.OLS(endog=y_train, exog=X_train,)
    modelo = modelo.fit()

    # Intervalos de confianza para los coeficientes del modelo
    # ==============================================================================
    intervalos_ci = modelo.conf_int(alpha=0.05)

    # Diagnóstico errores (residuos) de las predicciones de entrenamiento
    # ==============================================================================
    y_train = y_train.flatten()
    prediccion_train = modelo.predict(exog = X_train)
    residuos_train   = prediccion_train - y_train

    # Graficos del modelo
    # ==============================================================================
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(9, 8))

    axes[0, 0].scatter(y_train, prediccion_train, edgecolors=(0, 0, 0), alpha = 0.4)
    axes[0, 0].plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()],
                    'k--', color = 'black', lw=2)
    axes[0, 0].set_title('Predicted value vs Real value', fontsize = 10, fontweight = "bold")
    axes[0, 0].set_xlabel('Real')
    axes[0, 0].set_ylabel('Predicted')
    axes[0, 0].tick_params(labelsize = 7)

    axes[0, 1].scatter(list(range(len(y_train))), residuos_train,
                    edgecolors=(0, 0, 0), alpha = 0.4)
    axes[0, 1].axhline(y = 0, linestyle = '--', color = 'black', lw=2)
    axes[0, 1].set_title('Residuos of the model', fontsize = 10, fontweight = "bold")
    axes[0, 1].set_xlabel('id')
    axes[0, 1].set_ylabel('Residuos')
    axes[0, 1].tick_params(labelsize = 7)

    sns.histplot(
        data    = residuos_train,
        stat    = "density",
        kde     = True,
        line_kws= {'linewidth': 1},
        color   = "firebrick",
        alpha   = 0.3,
        ax      = axes[1, 0]
    )

    axes[1, 0].set_title('Residuos distribution', fontsize = 10,
                        fontweight = "bold")
    axes[1, 0].set_xlabel("Residuo")
    axes[1, 0].tick_params(labelsize = 7)


    sm.qqplot(
        residuos_train,
        fit   = True,
        line  = 'q',
        ax    = axes[1, 1], 
        color = 'firebrick',
        alpha = 0.4,
        lw    = 2
    )
    axes[1, 1].set_title('Q-Q residuos of the model', fontsize = 10, fontweight = "bold")
    axes[1, 1].tick_params(labelsize = 7)

    axes[2, 0].scatter(prediccion_train, residuos_train,
                    edgecolors=(0, 0, 0), alpha = 0.4)
    axes[2, 0].axhline(y = 0, linestyle = '--', color = 'black', lw=2)
    axes[2, 0].set_title('Residuos of the model vs prediction', fontsize = 10, fontweight = "bold")
    axes[2, 0].set_xlabel('Prediction')
    axes[2, 0].set_ylabel('Residuo')
    axes[2, 0].tick_params(labelsize = 7)

    # Se eliminan los axes vacíos
    fig.delaxes(axes[2,1])

    fig.tight_layout()
    plt.subplots_adjust(top=0.9)
    fig.suptitle('Residuos diagnosis', fontsize = 12, fontweight = "bold");
    plt.savefig("%s/%s_RLM_results_residuos.png" %(outputpath,sufijo), dpi=200)
    plt.clf()

    # Normalidad de los residuos Shapiro-Wilk test
    # ==============================================================================
    shapiro_stat, shapiro_p_value = shapiro(residuos_train)
    # Normalidad de los residuos D'Agostino's K-squared test
    # ==============================================================================
    k2, p_value = normaltest(residuos_train)
    print(f"Estadítico= {k2}, p-value = {p_value}")

    # Predicciones con intervalo de confianza 
    # ==============================================================================
    predicciones = modelo.get_prediction(exog = X_train).summary_frame(alpha=0.05)

    # Error de test del modelo 
    # ==============================================================================
    X_test = sm.add_constant(X_test, prepend=True)
    predicciones = modelo.predict(exog = X_test)
    rmse = mean_squared_error(
            y_true  = y_test,
            y_pred  = predicciones,
            squared = False
        )
    print(f"El error (rmse) de test es: {rmse}")

    # REPORT
    # ==============================================================================
    f = open("%s/%s_RLM_report.txt"% (outputpath,sufijo),"w")
    f.write("RESULTS OF MULTIPLE LINEAR REGRESSION OF %s and %s \n" %(var_x,var_y))
    f.write("\nMODEL: \n %s " % modelo.summary())
    f.write("\nRMSE: %s" % rmse)
    f.write("\nConfidence intervals:\n %s" %intervalos_ci)
    f.write("\n -- Normality test--")
    f.write("\nD'Shapiro test: statistic=%s, p-value=%s " %(shapiro_stat,shapiro_p_value))
    f.write("\nD'Agostino's K-squared test: statistic=%s, p-value=%s " %(k2,p_value))
    f.write("\nPredictions (%s): \n %s" %(cantidad_prediciones,predicciones.head(cantidad_prediciones)))
    f.close()

    # SAVE MODEL
    # ==============================================================================
    pickle.dump(modelo, open("%s/%s_RegressionModel.pkl" %(outputpath,sufijo), 'wb'))

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


