#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]
index = args[2]

library(TDA)
library(RcppCNPy)

maxscale <- 50
maxdimension <- 1

setwd(work_dir)

points_file = paste("projected", index, "points.npy", sep="_")
points = npyLoad(points_file)
diagram = ripsDiag(points, maxdimension, maxscale, library = "GUDHI")

deathTimeList = diagram[["diagram"]][,"Death"]
orderedDeathTimeIndexes = order(deathTimeList, decreasing = TRUE)

diagramScaleLimit = 20

for (index in orderedDeathTimeIndexes) {
    if (deathTimeList[index] != Inf) {
        diagramScaleLimit = ceiling(deathTimeList[index] * 1.2)
        break
    }
}

image_file = paste("projected", index, "diagram.png", sep="_")
png(file=image_file, width=800, height=1024, res=1024, units="px")
plot.diagram(diagram[["diagram"]], main = "Persistence Diagram", diagLim = diagramScaleLimit)

diagram_file = paste("projected", index, "diagram.table", sep="_")
write.table(diagram[["diagram"]], file=diagram_file, sep=",")

base_diagram_table = read.table("base_diagram.table", header=TRUE, sep=",")
base_diagram = cbind(base_diagram_table[,1], base_diagram_table[,2], base_diagram_table[,3])

bottleneckDist <- bottleneck(base_diagram, diagram[["diagram"]], dimension = 1)
distance_file = paste("projected", index, "distance.txt", sep="_")

write(bottleneckDist, file = distance_file)
