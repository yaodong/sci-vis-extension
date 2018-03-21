#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]

setwd(work_dir)


library(TDA)
library(RcppCNPy)

maxdimension <- 1

points_file = "base_points.npy"
points = npyLoad(points_file)

diagram = ripsDiag(points, dist="euclidean", maxdimension, maxscale <- 50, library = "GUDHI")

png(file='base_diagram.png', width=1024, height=1024, res=200, units="px")

deathTimeList = diagram[["diagram"]][,"Death"]

orderedDeathTimeIndexes = order(deathTimeList, decreasing = TRUE)

maxDeathTimeIndex = orderedDeathTimeIndexes[2]
diagramScaleLimit = deathTimeList[maxDeathTimeIndex] * 1.2

plot.diagram(diagram[["diagram"]], main = "Persistence Diagram (3D)", diagLim = cbind(0, diagramScaleLimit))

write.table(diagram[["diagram"]], file="base_diagram.table", sep=",")
