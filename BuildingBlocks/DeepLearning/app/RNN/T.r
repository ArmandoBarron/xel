library(keras)

completeFun <- function(data, desiredCols) {
  completeVec <- complete.cases(data[, desiredCols])
  return(data[completeVec, ])
}

args = commandArgs(trailingOnly=TRUE)

dataPath=args[1]
fileName=args[2]
destination=args[3]
columns = args[4]
trainSize = as.numeric(as.character(args[5]))
classColumn = args[6]
epoch = as.numeric(as.character(args[7]))
lossFunction = args[8]
metric = args[9]

dir.create(destination)


columns<-unlist(strsplit(columns, ","))
data <- read.table(paste(dataPath,fileName,sep=""), header=T, sep=",")

SPLT = (trainSize/100)
data <- completeFun(data, classColumn)




#define the prescribed inclusion probabilities
#pik <- runif(nrow(complete_data),0,1)
#select a sample
#s=UPrandomsystematic(pik)
#the sample is
#v<-(1:length(pik))[s==1]
#complete_sample<- complete_data[v,]


X <- data.matrix(data[,columns])
Y<- unlist(as.numeric(data[,classColumn]) -1)

featuresNumber = length(columns)
classNumber = length(unique(Y))


N_FILES <- nrow(X)
b = floor(SPLT*N_FILES)
x_train = array_reshape(X[1:b,], c(dim(X[1:b,]), 1))
x_test = array_reshape(X[(b+1):N_FILES,], c(dim(X[(b+1):N_FILES,]), 1))
y_train = to_categorical(Y[1:b], classNumber)
y_test = to_categorical(Y[(b+1):N_FILES], classNumber)



model <- keras_model_sequential() %>% 
  bidirectional(
    layer_gru(units = 32), input_shape = c(featuresNumber,1)
  ) %>% 
  layer_dense(units = classNumber, activation = 'softmax')

summary(model)
model %>% compile(
  loss = lossFunction,
  optimizer = optimizer_rmsprop(),
  metrics = c(metric)
)
history <- model %>% fit(
  x_train, y_train, 
  epochs = epoch, batch_size = 24, 
  validation_split = 0.2
)


report <- model %>% evaluate(x_test, y_test)
#accuracy <- paste("Accuracy", report$accuracy, sep=":")
accuracy <- paste("Accuracy", report[2], sep=":")

#loss <- paste("Loss", report$loss, sep=":")
loss <- paste("Loss", report[1], sep=":")

report_to_write<- paste(accuracy,loss, sep="\n")

fileConn<-file(paste(destination,"report.csv"))
writeLines(c(report_to_write), fileConn)
close(fileConn)

#save model 
save_model_tf(model, paste(destination,"CNNTrainedModel/"))