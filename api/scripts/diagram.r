#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
dirname = args[1]

library("TDA")

maxscale <- 10
maxdimension <- 1

base_data <- read.csv(paste(dirname ,"/base.csv", sep=""), header=FALSE)
base_matrix = cbind(base_data[,1], base_data[,2], base_data[,3])
base_diag = ripsDiag(base_matrix, maxdimension, maxscale, library = "GUDHI")

png(file=paste(dirname, "/images/diagram_base.png", sep=""), width=1280, height=1280, res=200, units="px")

plot(base_diag[["diagram"]])

dev.off()
