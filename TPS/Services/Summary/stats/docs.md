# Stats API
### http://localhost:3030/api/v1/

## Describe
### POST
Get basic descriptive statistics from a dataset
```
http://localhost:3030/api/v1/describe?columns=Temperatura
```
#### Params
| Parameter | Description                                            | Example                             |
|-----------|--------------------------------------------------------|-------------------------------------|
| columns   | Define columns to get summaries, 'All' by default      | `?columns=Temperatura,C02,altitude` |
#### Request
```
{
    "data": [
        {"Date": "2016-12-06", "Temperatura": 0.7895, "Source": "GCAG"},
        {"Date": "2016-12-06", "Temperatura": 0.81, "Source": "GISTEMP"},
        {"Date": "2016-11-06", "Temperatura": 0.7504, "Source": "GCAG"},
        {"Date": "2016-11-06", "Temperatura": 0.93, "Source": "GISTEMP"},
        {"Date": "2016-10-06", "Temperatura": 0.7292, "Source": "GCAG"},
        {"Date": "2016-10-06", "Temperatura": 0.89, "Source": "GISTEMP"},
        {"Date": "2016-09-06", "Temperatura": 0.8767, "Source": "GCAG"},
        {"Date": "2016-09-06", "Temperatura": 0.87, "Source": "GISTEMP"},
        {"Date": "2016-08-06", "Temperatura": 0.8998, "Source": "GCAG"}
    ]
}
```
#### Response
```
{
    "summary": {
        "Temperatura": {
            "length": 0,
            "columns": 0,
            "min": 0,
            "max": 0,
            "mean": 0,
            "median": 0,
            "mode": 0,
            "range": 0,
            "var": 0,
            "sd": 0,
            "quantile": {
                "0": 0.0,
                "25": 0.0,
                "75": 0.0,
                "100": 0.0
            }
        }
    }
}
```

## Correlation
### POST
Get variance, standar deviation, covariance and correlation coefficient from a dataset
```
http://localhost:3030/api/v1/correlation?columns=test,Temperature
```
#### Params
| Parameter | Description                                            | Example                             |
|-----------|--------------------------------------------------------|-------------------------------------|
| columns   | Define columns to get cor and cov, 'All' by default      | `?columns=test,Temperature` |
| method   | Define the method to get correlation('pearson', 'kendall', 'spearman'), 'pearson' by default    | `?method=pearson` |
#### Request
```
{
    "data": [
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
#### Response
```
{
  "correlation": {
    "size": 73,
    "variables": "test,Temperature",
    "covariance": 17.0051,
    "correlation": 0.7767,
    "correlationMethod": "pearson",
    "variance": {
      "test": 36.0638,
      "Temperature": 13.4418
    },
    "standarDeviation": {
      "test": 6.0053,
      "Temperature": 3.6663
    }
  }
}
```
more than two columns return a matrix of correlations and covariances, Response of `http://localhost:3030/api/v1/correlation?columns=test,Radiation,Temperature`:
```
...
"correlation": [
      {
        "test": 1,
        "Radiation": -0.7728,
        "Temperature": -0.7186,
        "_row": "test"
      },
      {
        "test": -0.7728,
        "Radiation": 1,
        "Temperature": 0.656,
        "_row": "Radiation"
      },
      {
        "test": -0.7186,
        "Radiation": 0.656,
        "Temperature": 1,
        "_row": "Temperature"
      }
    ]
...
```
