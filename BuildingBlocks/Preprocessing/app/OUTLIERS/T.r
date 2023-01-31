remove_outliers <- function(x, na.rm = TRUE, ...) {
  qnt <- quantile(x, probs=c(.25, .75), na.rm = na.rm, ...)
  H <- 1.5 * IQR(x, na.rm = na.rm)
  y <- x
  y[x < (qnt[1] - H)] <- "Outlier"
  y[x > (qnt[2] + H)] <- "Outlier"
  y
}

print("OUTLIERS")
args = commandArgs(trailingOnly=TRUE)

dataPath=args[1]
fileName=args[2]
destination=args[3]
columns = args[4]

columns<-unlist(strsplit(columns, ","))


data <- read.table(paste(dataPath,fileName,sep=""), header=T, sep=",")


for (column in columns){
  data[,column] <- remove_outliers(data[,column]) 
}
data$new <- apply(data[,columns], 1, function(x) any(x %in% c("Outlier")))
data <- data[!(data$new==TRUE),]
data$new <- NULL

data$X<-NULL


write.table(data, sep=",", file=destination, row.names=FALSE,col.names = TRUE)