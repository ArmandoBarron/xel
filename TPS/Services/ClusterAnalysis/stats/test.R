source("stats.R")
source("api.R")
library('dplyr')

#json format type: array of objects
json_data1 <- '[
    {"Date": "2016-12-06", "Radiation":0.23, "test":34, "Temperature": 0.7895, "Source": "GCAG"},
    {"Date": "2016-11-06", "Radiation":0.64, "test":30, "Temperature": 0.7504, "Source": "GCAG"},
    {"Date": "2016-10-06", "Radiation":0.18, "test":35, "Temperature": 0.7292, "Source": "GCAG"},
    {"Date": "2016-05-06", "Radiation":0.73, "test":30, "Temperature": 0.93, "Source": "GISTEMP"},
    {"Date": "2016-04-06", "Radiation":0.65, "test":24, "Temperature": 1.0733, "Source": "GCAG"},
    {"Date": "2016-04-06", "Radiation":0.61, "test":31, "Temperature": 1.09, "Source": "GISTEMP"},
    {"Date": "2016-03-06", "Radiation":0.53, "test":30, "Temperature": 1.2245, "Source": "GCAG"},
    {"Date": "2016-03-06", "Radiation":0.89, "test":11, "Temperature": 1.3, "Source": "GISTEMP"}
]'

#json format type: object by column
json_data2 <- '{
    "Data": ["2016-12-06", "2016-11-06", "2016-10-06", "2016-05-06", "2016-04-06", "2016-04-06", "2016-03-06", "2016-03-06"],
    "Temperature": [0.7895, 0.7504, 0.7292, 0.93, 1.0733, 1.09, 1.2245, 1.3],
    "Source": ["GCAG", "GCAG", "GCAG", "GISTEMP", "GCAG", "GISTEMP", "GCAG", "GISTEMP"]
}'

json_data3 <- '[
  {
    "antena": "IGUALA",
    "latitud": 18.360277777778,
    "longitud": -99.524166666667,
    "codigo": "GR04",
    "temperatura": "Null",
    "temp_mean": 24.91241,
    "humedad": "Null"
  },
  {
    "antena": "IGUALA PC",
    "latitud": 18.341388888889,
    "longitud": -99.503055555556,
    "codigo": "GR42",
    "temperatura": "28.8",
    "temp_mean": 24.87711,
    "humedad": "35"
  },
  {
    "antena": "TAXCO",
    "latitud": 18.548055555556,
    "longitud": -99.602777777778,
    "codigo": "GR45",
    "temperatura": "23.3",
    "temp_mean": 24.59628,
    "humedad": "36"
  },
  {
    "antena": "SIERRA HUAUTLA",
    "latitud": 18.541388888889,
    "longitud": -98.936111111111,
    "codigo": "MO05",
    "temperatura": "26.3",
    "temp_mean": 24.19772,
    "humedad": "28"
  },
  {
    "antena": "ZACATEPEC",
    "latitud": 18.644166666667,
    "longitud": -99.207222222222,
    "codigo": "MO07",
    "temperatura": "27.2",
    "temp_mean": 23.52673,
    "humedad": "36"
  },
  {
    "antena": "IZUCAR MATAM",
    "latitud": 18.616666666667,
    "longitud": -98.451944444444,
    "codigo": "PU02",
    "temperatura": "24.8",
    "temp_mean": 22.61783,
    "humedad": "40"
  }
]'

data1 <- objarrayToDataframe(json_data1)
data2 <- jsoncolToDataframe(json_data2)
cdata <- cbind(data1=data1, data2=data1)

numericdata <- select(data1, test, Temperature, Radiation)

#describe(data1$Temperature)

numericData <- select_if(data1, is.numeric)
description <- apply(numericData, 2, describe)
var <- lapply(description, function(x) x$var)
var

#covariance(data1$test, data2$Temperature)
#data3 <- objarrayToDataframe(json_data3)
#data3[data3 == "Null"] = NA
#datacor <- select(data3, humedad, temperatura)
#datacor$temperatura <- as.numeric(datacor$temperatura)
#datacor$humedad <- as.numeric(datacor$humedad)
#datacor <- lapply(datacor, function(x) as.numeric(x))
#sapply(datacor, class)
#cova <- cor(datacor$temperatura, datacor$humedad, use="complete.obs")
#cova

API_covariance <- function() {
    
}

test <- function() {
    API_covariance()
}

test()

