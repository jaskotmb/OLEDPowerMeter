rm(list=ls())
# Ubuntu Directory
# homeDir = "/home/jaskotmb/Documents/OLED_Data/170926"
# Windows Directory
homeDir = "C:/Users/jasko/IdeaProjects/OLEDPowerMeter/OLED_Data/170926"
setwd(homeDir)
fileList <- list.files()

# Initialize vector of dataframes length of number of files
numFiles = length(fileList)
dfList = list(seq(1,numFiles)) # dfList is an array to hold dataframes

# Reads all files into dataframes
for (i in seq(1,numFiles)){
  setwd(homeDir)
  setwd(fileList[i])
  fn <- list.files()[1]
  dfList[[i]] <- read.csv(file=fn,skip=3)
}
# Array of Data measurement lengths
lenData = seq(1,numFiles)
for (i in seq(1,numFiles)){
  lenData[i] = length(dfList[[i]][[1]])
}

tstep <- 1.12935
Area <- 0.02 #cm^2
# cols <- rainbow(numFiles,start=2/6,end=5/6)
cols = c(rep("red",130),rep("blue",7),rep("brown",8),rep("lightblue",5),rep("orange",2),"green")

# Brightness decay
plot(0,xlim=c(0,1800),ylim=c(-10,-4),xlab="Time (sec)",ylab="Log(Brightness)",
     main="50mA/cm^2 Current OLED Aging")
for (i in seq(2,numFiles)){
  lines(seq(1,lenData[i])*tstep,log(abs(dfList[[i]]$Brightness.Current..A./Area)),col=cols[i])
}
legend(200,-6.4,c("No getter film","Getter film"),col=c("blue","red"),pch=17)

plot(0,xlim=c(0,2200),ylim=c(0.000002,0.000003))
for (i in seq(1,numFiles)){
  lines(seq(1,lenData[i])*tstep,(dfList[[i]]$Brightness.Current..A.),col=cols[i])
}

plot(0,xlim=c(0,log(2200)),ylim=c(-8.5,-6.5))
for (i in seq(1,numFiles)){
  lines(log(seq(1,lenData[i])*tstep),log(dfList[[i]]$Brightness.Current..A./Area),col=cols[i])
}

## Voltage rise
plot(0,xlim=c(0,2000),ylim=c(5,6.1))
for (i in seq(1,numFiles)){
  lines(seq(1,lenData[i])*tstep,dfList[[i]]$Voltage..V.,col=cols[i])
}

## Power Efficiency
plot(0,xlim=c(0,2000),ylim=c(-8,-5.5))
for (i in seq(1,numFiles)){
  lines(seq(1,lenData[i])*tstep,
        log(dfList[[i]]$Brightness.Current..A./(dfList[[i]]$Voltage..V.*dfList[[i]]$Current..A.)),col=cols[i])
}

plot(0,xlim=c(0,log(2000)),ylim=c(-8,-5.5))
for (i in seq(1,numFiles)){
  lines(log(seq(1,lenData[i])*tstep),
        log(dfList[[i]]$Brightness.Current..A./(dfList[[i]]$Voltage..V.*dfList[[i]]$Current..A.)),col=cols[i])
}

plot(0,xlim=c(0,log(max(lenData))),ylim=c(-8.5,-5.5))
for (i in seq(1,numFiles)){
  lines(log(seq(1,lenData[i])*tstep),
        log(dfList[[i]]$Brightness.Current..A./(dfList[[i]]$Voltage..V.*dfList[[i]]$Current..A.)),col=cols[i])
}
