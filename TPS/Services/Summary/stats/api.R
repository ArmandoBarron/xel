source('stats.R')
library('dplyr')


#' API Index
#' @serializer contentType list(type="application/html")
#' @get /

function(res) {
	include_md('docs.md', res)
}



#' API DESCRIPTION
#' @serializer unboxedJSON
#' @get /api/v1/

function() {
	version <- "1.0"
	name <- "Stats"
	base_url <- "http://localhost:3030/api/v1/"
	author <- "Alfonso Lechuga Illingworth"
	licence <- paste(base_url, "licence", sep="")
	docs <- paste(base_url, "documentation", sep="")
	endpoints <- list(
		"01"=base_url,
		"02"=paste(base_url, "describe", sep=""),
		"03"=paste(base_url, "plot", sep=""),
		"04"=paste(base_url, "echo", sep="")
	)
	index <- list(version=version, name=name, author=author, licence=licence,
		docs=docs, apiUrl=base_url, endpoints=endpoints)
	index
}



#' API DOCS
#' @serializer contentType list(type="application/html")
#' @get /documentation

function(res) {
	include_md('docs.md', res)
}



#' Describe
#' @serializer unboxedJSON
#' @param columns If provide, return the description to only these numeric columns 
#' @post /api/v1/describe

function(data, columns="all") {
	numericData <- select_if(data, is.numeric)

	if (columns != "all")
		numericData <- select(numericData, unlist(strsplit(columns, ',')))
	column_names = colnames(numericData)

	description <- apply(numericData, 2, describe)
	list(
		description= description
	)
}



#' Covariance
#' @serializer unboxedJSON
#' @param columns variables to calculate covariance, at least two.
#' @post /api/v1/covariance

function(res, data, columns) {

	#select variables
	variables <- unlist(strsplit(columns, ','))
	data <- select(data, variables)

	#convert nulls to NA
	data[data == "Null"] = NA
	data[data == "null"] = NA
	data[data == ""] = NA

	#convert to numeric
	data <- as.data.frame(lapply(data, function(x) as.numeric(x)))
	
	#get covariance and variance
	if (length(variables) > 2)
		cova <- covarianceMatrix(data)
	else
		cova <- covariance(data[,1], data[,2])

	description <- apply(data, 2, describe)
	var <- lapply(description, function(column) column$var)

	list(
		covariance= list(
			len= length(variables),
			variables= columns,
			result= cova,
			var= var
		)
	)

}



#' Correlation
#' Get variance, covariance and correlation coefficient of a dataset
#' @serializer unboxedJSON
#' @param columns variables to calculate correlation coeffs, at least two.
#' @param method define the method for correlation (pearson, spearman, kendall)
#' @post /api/v1/correlation

function(data, columns, method="pearson") {
	
	#select variables
	variables <- unlist(strsplit(columns, ','))
	data <- select(data, variables)
	#convert nulls to NA
	data[data == "Null"] = NA
	data[data == "null"] = NA
	data[data == ""] = NA
	#convert to numeric
	data <- as.data.frame(lapply(data, function(x) as.numeric(x)))
	#get coefficients
	if (length(variables) > 2) {
		cova <- covarianceMatrix(data)
		corr <- correlationMatrix(data,method)
	} else {
		cova <- covariance(data[,1], data[,2])
		corr <- correlation(data[,1], data[,2], method)
	}
	description <- apply(data, 2, describe)
	var <- lapply(description, function(column) column$var)
	sd  <- lapply(description, function(column) column$sd)
	list(
		correlation= list(
			size= nrow(data),
			variables= columns,
			covariance= cova,
			correlation= corr,
			correlationMethod= method,
			variance= var,
			standarDeviation = sd
		)
	)
}



#' Plot out data from the iris dataset
#' @param spec If provided, filter the data to only this species (e.g. 'setosa')
#' @get /api/v1/plot
#' @png

function(spec) {
	myData <- iris
	title <- "All Species"
	
	# Filter if the species was specified
	if (!missing(spec)){
		title <- paste0("Only the '", spec, "' Species")
		myData <- subset(iris, Species == spec)
	}
	
	plot(myData$Sepal.Length, myData$Petal.Length,
		main=title, xlab="Sepal Length", ylab="Petal Length")
}
