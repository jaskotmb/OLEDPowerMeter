rm(list=ls())
# Ubuntu Directory
# homeDir = "/home/jaskotmb/Documents/OLED_Data/170926"
# Windows Directory
homeDir = "C:/Users/jasko/IdeaProjects/OLEDPowerMeter/"
setwd(homeDir)

sweep <- read.csv(file="test.csv",skip=0)
Area = 0.04

plot(sweep$Voltage..V.,log(1000*sweep$Current..A./Area))