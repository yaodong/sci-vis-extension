#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]
index = args[2]
maxscale = as.integer(args[3])

library(TDA)
library(RcppCNPy)

maxdimension <- 1

setwd(work_dir)

points_file = paste("projected", index, "points.npy", sep="_")
points = npyLoad(points_file)
diagram = ripsDiag(points, dist="euclidean", maxdimension, maxscale, library = "GUDHI")

image_file = paste("projected", index, "diagram.png", sep="_")
png(file=image_file, width=1024, height=1024, res=200, units="px")

deathTimeList = diagram[["diagram"]][,"Death"]
orderedDeathTimeIndexes = order(deathTimeList, decreasing = TRUE)
maxDeathTimeIndex = orderedDeathTimeIndexes[2]
diagMaxScale = deathTimeList[maxDeathTimeIndex] * 1.2

plot.diagram(diagram[["diagram"]], main = "Persistence Diagram", diagLim = cbind(0, diagMaxScale))

diagram_file = paste("projected", index, "diagram.table", sep="_")
write.table(diagram[["diagram"]], file=diagram_file, sep=",")

base_diagram_table = read.table("base_diagram.table", header=TRUE, sep=",")
base_diagram = cbind(base_diagram_table[,1], base_diagram_table[,2], base_diagram_table[,3])

bottleneckDist <- bottleneck(base_diagram, diagram[["diagram"]], dimension = 1)
wassersteinDist <- wasserstein(base_diagram, diagram[["diagram"]], dimension = 1)

results <- list(bottleneck = bottleneckDist, wasserstein = wassersteinDist)
result_file = paste("projected", index, "results.csv", sep="_")

write.csv(results, file = result_file)
