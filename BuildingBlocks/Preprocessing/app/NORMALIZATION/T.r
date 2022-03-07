print("NORMALIZATION")
args = commandArgs(trailingOnly=TRUE)

dataPath=args[1]
fileName=args[2]
destination=args[3]
columns = args[4]

columns<-unlist(strsplit(columns, ","))

data <- read.table(paste(dataPath,fileName,sep=""), header=T, sep=",")

for (column in columns){
    data[,column] <- as.numeric(as.character(data[,column],na.rm=TRUE),na.rm=TRUE)
    data[,column] <- (data[,column]-min(data[,column])+0.001)/(max(data[,column])-min(data[,column])+0.002)
  
}


write.table(data, sep=",", file=destination, row.names=FALSE,col.names = TRUE)