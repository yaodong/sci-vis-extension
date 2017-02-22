#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
dirname = args[1]
zx_angle = args[2]
zy_angle = args[3]

library("TDA")

maxscale <- 10
maxdimension <- 1

base_data <- read.csv(paste(dirname ,"/base.csv", sep=""), header=FALSE)
base_matrix = cbind(base_data[,1], base_data[,2], base_data[,3])
base_diag = ripsDiag(base_matrix, maxdimension, maxscale, library = "GUDHI")

rm("base_data")
rm("base_matrix")

rotated_file = paste(dirname, "/rotated/", toString(zx_angle), "__", toString(zy_angle) , ".csv", sep="")
result_file = paste(dirname, "/distance/", toString(zx_angle), "__", toString(zy_angle) , ".txt", sep="")

projection_data = read.csv(rotated_file, header=FALSE)
projection_matrix = cbind(projection_data[,1], projection_data[,2])
projection_diag = ripsDiag(projection_matrix, maxdimension, maxscale, library = "GUDHI")

bottleneckDist <- bottleneck(base_diag[["diagram"]], projection_diag[["diagram"]], dimension = 1)
write(bottleneckDist, file = result_file)

png(file=paste(dirname, "/images/diagram_", toString(zx_angle), "__", toString(zy_angle), ".png", sep=""), width=1280, height=1280, res=200, units="px")

plot(projection_diag[["diagram"]])

dev.off()
