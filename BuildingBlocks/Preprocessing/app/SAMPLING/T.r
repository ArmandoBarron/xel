library(sampling)

print("SAMPLING")
args = commandArgs(trailingOnly=TRUE)

dataPath=args[1]
fileName=args[2]
destination=args[3]

data <- read.table(paste(dataPath,fileName,sep=""), header=T, sep=",")

pik <- runif(nrow(data),0,1)
s=UPrandomsystematic(pik)
v<-(1:length(pik))[s==1]
data<- data[v,]


write.table(data, sep=",", file=destination, row.names=FALSE,col.names = TRUE)