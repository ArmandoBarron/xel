# Transversal Processing Services (TPS)
Los TPS son microservicios para el procesamiento de datos provenientes de una o varias etapas dentro de flujos de trabajo. Para que sea considerado un TPS este debe seguir un efoque de procesamiento ETL (Extract-Transform-Load), mantener las caracteristicas de un microservicio (Escalabilidad, Modularidad, independiente, autocontenido, etc.), y ser capaz de ser desplegado en diferentes infraestructuras de computo.


# TPS de analitica de datos
A continuacion se describen los TPS utilizados para analitica de datos.

## __Summary__  : 
TPS para la obtencion de datos estadisticos programado en lenguaje R, el cual puede ser accedido a traves de peticiones rest. Cuenta con los siguientes servicios:

* _Corrleation_:  Obtiene la varianza, covarianza, y coeficiente de correlacion de un dataset.
    
    ### URL:
    > POST http://localhost:11002/api/v1/correlation
    
    ### Datos que recibe:

    > Parametro(__columns__) : Cadena de texto con los nombres de las variables a caulcuar el coeficiente de correlacion (las variables deben ir separadas por ',' y ser al menos 2) 
    >
    > Parametro(__method__) : Define el metodo de correlacion (pearson, spearman, kendall; pearson por default).
    >
    > __data__: Json en formato de registros con los datos a procesar. e.g:
    ```json 
    {"data":[
    {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
    {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
    {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
    {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
    {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
    {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
    {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
    {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"} 
    ]}
    ```
    ### Ejemplo de respuesta:

    ```json 
    {
        "correlation": {
            "size": 8,
            "variables": "test,Temperature,Radiation",
            "covariance": [
                {
                    "test": 58.6964,
                    "Temperature": -1.2083,
                    "Radiation": -1.4311,
                    "_row": "test"
                },
                {
                    "test": -1.2083,
                    "Temperature": 0.0482,
                    "Radiation": 0.0348,
                    "_row": "Temperature"
                },
                {
                    "test": -1.4311,
                    "Temperature": 0.0348,
                    "Radiation": 0.0584,
                    "_row": "Radiation"
                }
            ],
            "correlation": [
                {
                    "test": 1,
                    "Temperature": -0.7186,
                    "Radiation": -0.7728,
                    "_row": "test"
                },
                {
                    "test": -0.7186,
                    "Temperature": 1,
                    "Radiation": 0.656,
                    "_row": "Temperature"
                },
                {
                    "test": -0.7728,
                    "Temperature": 0.656,
                    "Radiation": 1,
                    "_row": "Radiation"
                }
            ],
            "correlationMethod": "pearson",
            "variance": {
                "test": 58.6964,
                "Temperature": 0.0482,
                "Radiation": 0.0584
            },
            "standarDeviation": {
                "test": 7.6614,
                "Temperature": 0.2195,
                "Radiation": 0.2417
            }
        }
}
    ```


* _Covariance_: Calcula la covarianza de al menos 2 variables dentro de un dataset.

    ### URL:
    > POST http://localhost:11002/api/v1/covariance
    ### Datos que recibe:

    > Parametro(__columns__) : Cadena de texto con los nombres de las variables a calcular la covarianza (las variables deben ir separadas por ',' y ser al menos 2).
    >
    > __data__: Json en formato de registros con los datos a procesar. e.g:
    ```json 
    {"data":[
    {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
    {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
    {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
    {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
    {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
    {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
    {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
    {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"} 
    ]}
    ```
    ### Ejemplo de respuesta:
    ```json 
        {
        "covariance": {
            "len": 3,
            "variables": "test,Temperature,Radiation",
            "result": [
                {
                    "test": 58.6964,
                    "Temperature": -1.2083,
                    "Radiation": -1.4311,
                    "_row": "test"
                },
                {
                    "test": -1.2083,
                    "Temperature": 0.0482,
                    "Radiation": 0.0348,
                    "_row": "Temperature"
                },
                {
                    "test": -1.4311,
                    "Temperature": 0.0348,
                    "Radiation": 0.0584,
                    "_row": "Radiation"
                }
            ],
            "var": {
                "test": 58.6964,
                "Temperature": 0.0482,
                "Radiation": 0.0584
            }
        }
    }
    ```

* _Describe_ : Realiza una descripcion estadistica de un dataset mediante el calculo de medidas de tendencia central.

    ### URL:
    > POST http://localhost:11002/api/v1/describe
    ### Datos que recibe:

    > Parametro(__columns__) (opcional): Cadena de texto con los nombres de las variables a realizar los calculos estadisticos por separado, por default se calcula para todas las columnas numericas (las variables deben ir separadas por ',' y ser al menos 2).
    >
    > __data__: Json en formato de registros con los datos a procesar. e.g:
    ```json 
    {"data":[
    {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
    {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
    {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
    {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
    {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
    {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
    {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
    {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"} 
    ]}
    ```
    ### Ejemplo de respuesta:
    ```json 
    {
        "description": {
            "Radiation": {
                "length": 8,
                "min": 0.18,
                "max": 0.89,
                "mean": 0.5575,
                "median": 0.625,
                "mode": 0.23,
                "range": [
                    0.18,
                    0.89
                ],
                "var": 0.0584,
                "sd": 0.2417,
                "quantile": {
                    "0%": 0.18,
                    "25%": 0.455,
                    "50%": 0.625,
                    "75%": 0.67,
                    "100%": 0.89
                }
            }
        }
    }
    ```
## __Clustering__  
TPS con algoritmos de agrupamiento de datos.

* _Kmeans_ [Presente en dislib] : Realiza el agrupamiento de los datos utilizando el algoritmo kmeans. Se agrega una etiqueta de clase (class) a cada registro.
    ### URL:

    > POST http://localhost:11001/kmeans
    ### Datos que recibe:
    El servicio recibe como entrada un json cons las siguientes caracteristicas:
    > __K__: Numero de grupos (2 por default).
    >
    > __columns__: cadena de texto con las variables a utilizar para el agrupamiento (separadas por ',').
    >
    > __data__: Json en formato de registros con los datos a procesar.
    ```json 
    {
        "K":3,
        "columns":"Temperature",
        "data":[
        {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
        {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
        {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
        {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
        {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
        {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
        {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
        {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"} 
        ]
    }
    ```
    ### Ejemplo de respuesta:
    ```json 
    {"status": "OK", "path": null, 
        "result": [
            {"Date": "2016-12-06", "Radiation": 0.23, "test": 34, "Temperature": 0.7895, "Source": "GCAG", "class": 1},
            {"Date": "2016-11-06", "Radiation": 0.64, "test": 30, "Temperature": 0.7504, "Source": "GCAG", "class": 1},
            {"Date": "2016-10-06", "Radiation": 0.18, "test": 35, "Temperature": 0.7292, "Source": "GCAG", "class": 1},
            {"Date": "2016-05-06", "Radiation": 0.73, "test": 30, "Temperature": 0.93, "Source": "GISTEMP", "class": 0},
            {"Date": "2016-04-06", "Radiation": 0.65, "test": 24, "Temperature": 1.0733, "Source": "GCAG", "class": 0},
            {"Date": "2016-04-06", "Radiation": 0.61, "test": 31, "Temperature": 1.09, "Source": "GISTEMP", "class": 0},
            {"Date": "2016-03-06", "Radiation": 0.53, "test": 30, "Temperature": 1.2245, "Source": "GCAG", "class": 2},
            {"Date": "2016-03-06", "Radiation": 0.89, "test": 11, "Temperature": 1.3, "Source": "GISTEMP", "class": 2}
        ]}
    ```

* _Hierarchical clustering_ : Realiza el agrupamiento de los datos utilizando un algoritmo herarhico.
    ### URL:

    > POST http://localhost:11001/herarhical
    ### Datos que recibe:
    El servicio recibe como entrada un json cons las siguientes caracteristicas:
    > __K__: Numero de grupos (altura del arbol).
    >    
    > __columns__: cadena de texto con las variables a utilizar para el agrupamiento (separadas por ',').
    >
    >__method__: Criterio de vinculación utilizar (ward,complete,average,single). El criterio de vinculación determina qué distancia usar entre conjuntos de observación. El algoritmo fusionará los pares de clúster que minimizan este criterio. 
    >
    >> * _Ward_ minimiza la varianza de los grupos que se fusionan.
    >> * _Average_ usa el promedio de las distancias de cada observación de los dos conjuntos.
    >> * _Complete_ utiliza las distancias máximas entre todas las observaciones de los dos conjuntos.
    >> * _single_ usa el mínimo de las distancias entre todas las observaciones de los dos conjuntos.
    >
    > __index__ (opcional): Agrupa los registros en base a un index. e.g. si index es "DATA" se agrupan todos los registros con un mismo valor de "DATE" y se promedian, obteniendo un unico registro para el agrupamiento.
    >
    > __data__: Json en formato de registros con los datos a procesar.
    ```json 
    {
        "K":3,
        "columns":"Temperature",
        "method":"single",
        "data":[
        {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
        {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
        {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
        {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
        {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
        {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
        {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
        {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"} 
        ]
    }
    ```
    ### Ejemplo de respuesta:
    ```json 
    "status": "OK", "path": null, 
    "result": [
        {"Date": "2016-12-06", "Radiation": 0.23, "test": 34, "Temperature": 0.7895, "Source": "GCAG", "class": 1}, 
        {"Date": "2016-11-06", "Radiation": 0.64, "test": 30, "Temperature": 0.7504, "Source": "GCAG", "class": 1}, 
        {"Date": "2016-10-06", "Radiation": 0.18, "test": 35, "Temperature": 0.7292, "Source": "GCAG", "class": 1}, 
        {"Date": "2016-05-06", "Radiation": 0.73, "test": 30, "Temperature": 0.93, "Source": "GISTEMP", "class": 2}, 
        {"Date": "2016-04-06", "Radiation": 0.65, "test": 24, "Temperature": 1.0733, "Source": "GCAG", "class": 0}, 
        {"Date": "2016-04-06", "Radiation": 0.61, "test": 31, "Temperature": 1.09, "Source": "GISTEMP", "class": 0}, 
        {"Date": "2016-03-06", "Radiation": 0.53, "test": 30, "Temperature": 1.2245, "Source": "GCAG", "class": 0}, 
        {"Date": "2016-03-06", "Radiation": 0.89, "test": 11, "Temperature": 1.3, "Source": "GISTEMP", "class": 0}]
    }
    ```
* _Silhouette_ : Realiza una comparativa entre los algoritmos de kmeans y herarhico con el metodo single, comprobando valores de k de 1 a 15. El resultado de las pruebas se grafica.
    ### URL:

    > POST http://localhost:11001/silhouette
    ### Datos que recibe:
    El servicio recibe como entrada un json cons las siguientes caracteristicas:
   
    > __columns__: cadena de texto con las variables a utilizar para el agrupamiento (separadas por ',').
    >
    > __index__ (opcional): Agrupa los registros en base a un index. e.g. si index es "DATA" se agrupan todos los registros con un mismo valor de "DATE" y se promedian, obteniendo un unico registro para el agrupamiento.
    >
    > __data__: Json en formato de registros con los datos a procesar.
    ```json 
    {
        "K":3,
        "columns":"Temperature",
        "data":[
        {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
        {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
        {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
        {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
        {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
        {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
        {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
        {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"} 
        ]
    }
    ```
    ### Ejemplo de respuesta:
    ```json 
    {"status": "OK", "path": "/static/4483788386721272487.png","winner": "kmeans",
    "result": [
        {"Date": "2016-12-06", "Radiation": 0.23, "test": 34, "Temperature": 0.7895, "Source": "GCAG", "class": 0}, 
        {"Date": "2016-11-06", "Radiation": 0.64, "test": 30, "Temperature": 0.7504, "Source": "GCAG", "class": 0}, 
        {"Date": "2016-10-06", "Radiation": 0.18, "test": 35, "Temperature": 0.7292, "Source": "GCAG", "class": 0}, 
        {"Date": "2016-05-06", "Radiation": 0.73, "test": 30, "Temperature": 0.93, "Source": "GISTEMP", "class": 3}, 
        {"Date": "2016-04-06", "Radiation": 0.65, "test": 24, "Temperature": 1.0733, "Source": "GCAG", "class": 2}, 
        {"Date": "2016-04-06", "Radiation": 0.61, "test": 31, "Temperature": 1.09, "Source": "GISTEMP", "class": 2}, 
        {"Date": "2016-03-06", "Radiation": 0.53, "test": 30, "Temperature": 1.2245, "Source": "GCAG", "class": 1}, 
        {"Date": "2016-03-06", "Radiation": 0.89, "test": 11, "Temperature": 1.3, "Source": "GISTEMP", "class": 1}]}
    ```
    > Para ver la grafica, se utiliza el path que retorna el servicio de la forma:
    >   
    > http://localhost:11001/static/4483788386721272487.png