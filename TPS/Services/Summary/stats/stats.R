library(jsonlite)



objarrayToDataframe <- function(json) {
    # Convert a JSON to dataframe object with format: array of objects
    # [{"col1": obs1, "col2": obs1, "..": ..}, {"col1": obs1, "col2": obs1, "..": ..}, {...}]
    # str -> dataframe
    data <- fromJSON(json, simplifyDataFrame=TRUE)
    data <- as.data.frame(data)
    return(data)
}


jsoncolToDataframe <- function(json) {
    # Convert a JSON to dataframe object with format: object by column
    # { "index":[1, 2, 3, ...], "column1": [obs1, obs2, obs3, ...], "column2": ...}
    # str -> dataframe
    data <- fromJSON(json, simplifyMatrix=TRUE)
    data <- as.data.frame(data)
    return(data)
}


getMode <- function(value) {
   uniqvalue <- unique(value)
   uniqvalue[which.max(tabulate(match(value, uniqvalue)))]
}


describe <- function(column) {
    # Return basic descriptive statistics
    # list -> list
    description <- list(
        length= length(column),
        min= min(column, na.rm=TRUE),
        max= max(column, na.rm=TRUE),
        mean= mean(column, na.rm=TRUE),
        median= median(column, na.rm=TRUE),
        mode= getMode(column),
        range= range(column, na.rm=TRUE),
        var= var(column, na.rm=TRUE),
        sd= sd(column, na.rm=TRUE),
        quantile= list(
            "0%"= quantile(column, na.rm=TRUE)[1],
            "25%"= quantile(column, na.rm=TRUE)[2],
            "50%"= quantile(column, na.rm=TRUE)[3],
            "75%"= quantile(column, na.rm=TRUE)[4],
            "100%"= quantile(column, na.rm=TRUE)[5]
        )
    )
    return(description)
}

covariance <- function(xvar, yvar) {
    # Return covariance of two variables x and y
    # list, list -> numeric
    cov(xvar, yvar, use="complete.obs")
}

covarianceMatrix <- function(variables) {
    # Return a covariance matrix
    # matrix -> matrix
    as.data.frame(cov(variables, use="complete.obs"))
}

correlation <- function(xvar, yvar, method) {
    # Return covariance of two variables x and y
    # list, list -> numeric
    cor(xvar, yvar, method=method, use="complete.obs")
}

correlationMatrix <- function(variables, method) {
    # Return a covariance matrix
    # matrix -> matrix
    as.data.frame(cor(variables, method=method, use="complete.obs"))
}