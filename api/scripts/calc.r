#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
dirname = args[1]

library("TDA")

maxscale <- 10
maxdimension <- 1

base_data <- read.csv(paste("../tmp/", dirname ,"/base.csv", sep=""), header=FALSE)
base_matrix = cbind(base_data[,1], base_data[,2], base_data[,3])
base_diag = ripsDiag(base_matrix, maxdimension, maxscale, library = "GUDHI")

phi_range = seq(-90, 85, by=5)
theta_range = seq(-90, 85, by=5)

for (zx_angle in phi_range) {
    for (zy_angle in theta_range) {
        rotated_file = paste("../tmp/", dirname, "/rotated/", toString(zx_angle), "__", toString(zy_angle) , ".csv", sep="")
        result_file = paste("../tmp/", dirname, "/distance/", toString(zx_angle), "__", toString(zy_angle) , ".txt", sep="")

        projection_data = read.csv(rotated_file, header=FALSE)
        projection_matrix = cbind(projection_data[,1], projection_data[,2])
        projection_diag = ripsDiag(projection_matrix, maxdimension, maxscale, library = "GUDHI")

        bottleneckDist <- bottleneck(base_diag[["diagram"]], projection_diag[["diagram"]], dimension = 1)
        write(bottleneckDist, file = result_file)
    }
}
