#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]

setwd(work_dir)

library(TDA)
library(RcppCNPy)

maxscale <- 5
maxdimension <- 1

points_file = "base_points.npy"
points = npyLoad(points_file)

diagram = alphaShapeDiag(points, library = "GUDHI")

png(file='base.png', width=1280, height=1280, res=200, units="px")
write.table(diagram[["diagram"]], file="base_diagram.table", sep=",")

dev.off()
