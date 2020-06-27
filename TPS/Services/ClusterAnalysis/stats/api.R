#source('stats.R')
library('dplyr')
library(clusterCrit)



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
	name <- "Clustering tools"
	base_url <- "http://localhost:3030/api/v1/"
	author <- "Juan Armando Barrón lugo"
	licence <- paste(base_url, "licence", sep="")
	docs <- paste(base_url, "documentation", sep="")
	endpoints <- list(
		"01"=base_url,
		"02"=paste(base_url, "validate", sep=""),
		"03"=paste(base_url, "jaccard", sep="")
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


#' Validation
#' @serializer unboxedJSON
#' @param indexes If provide, return the description using only the given indexes
#' @param column If provide, return the description to only these numeric columns 
#' @param ignore_columns If provide, the columns are ignore 

#' @post /api/v1/validation

function(data, indexes="all",column="last",ignore_columns="",cluster_columns="") {

	




	if (column != "last"){
		clust_label <- data[,column]
		data <- select(data, -one_of(column)) #only data expeting this one
		if (ignore_columns != ""){
			ignore_list <- unlist(strsplit(ignore_columns, ','))
			datos <- select(data, -one_of(ignore_list)) #data used for clustering
		}
		else if (cluster_columns!="") {
			columns_list <- unlist(strsplit(cluster_columns, ','))
			datos <- select(data, columns_list) #data used for clustering
		}
		else
			datos <-data #data used for clustering

	}else{
		clust_label <- data[,ncol(data)]
		data <- data[,-ncol(data)]
		if (ignore_columns != ""){
			ignore_list <- unlist(strsplit(ignore_columns, ','))
			datos <- select(data, -one_of(ignore_list)) #data used for clustering
		}
		else if (cluster_columns!="") {
			columns_list <- unlist(strsplit(cluster_columns, ','))
			datos <- select(data, columns_list) #data used for clustering
		}
		else
			datos <- data#data used for clustering
	}
	if (indexes != "all")
		indexes_list <- unlist(strsplit(indexes, ','))
	else
		indexes_list <-list('Calinski_Harabasz','Davies_Bouldin','Silhouette','SD_Dis','Point_Biserial','Ratkowsky_Lance','GDI11')


	#get distribution
	#d<-dist(table)

	#datos is DF
	datos = apply(datos, 2, as.numeric)
	datos = data.matrix(datos)

	indexes_results = list()
	for (p in indexes_list) {
		key <- p
		value <- intCriteria(datos,clust_label,p)
		indexes_results[[ key ]] <- value 
		
	}
	list(result=indexes_results)
}



#' Jaccard
#' @serializer unboxedJSON
#' @param columns If provide, return the description to only these numeric columns 
#' @post /api/v1/jaccard

function(data,columns="last") {

	if (columns != "last"){
		columns <- unlist(strsplit(columns, ','))
		data <- data.matrix(select(data, columns)) #data used for clustering

	}
	label1 <- data[,ncol(data)-1] #group 1 label
	label2 <- data[,ncol(data)] #group 2 label


	r = extCriteria(label1,label2,"Jaccard")

	list(result=r)
}


