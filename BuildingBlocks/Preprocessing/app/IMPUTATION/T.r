fill_mean <- function(columns,data){
  
  for (column in columns){
    data[is.na(data[,column]), column] <- mean(data[,column],na.rm = TRUE)
}
  return(data)
}


fill_test <- function(columns,data){
  
  for (column in columns){
    data[is.na(data[,column]), column] <- "MEAN"
    
  }
  return(data)
}

fill_mode <- function(columns,data){
  
  for(column in columns){
    
    val <- unique(data[!is.na(data[,column]),column])
    mode <- val[which.max(tabulate(match(data, val)))]
    data[is.na(data[,column]), column] <- mode
    
  }
  return(data)
}



print("IMPUTACION")
args = commandArgs(trailingOnly=TRUE)

dataPath=args[1]
fileName=args[2]
destination=args[3]
columns = args[4]
method = toupper(args[5])

data <- read.table(paste(dataPath,fileName,sep=""), header=T, sep=",")

columns<-unlist(strsplit(columns, ","))

if(method=="MEAN"){
    data<-fill_mean(columns,data)
}
if(method=="MODE"){
    data<-fill_mode(columns,data)
}


data$X <- NULL


write.table(data, sep=",", file=destination, row.names=FALSE,col.names = TRUE)