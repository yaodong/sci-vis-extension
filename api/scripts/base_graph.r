#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]

setwd(work_dir)


library(TDA)
library(RcppCNPy)


points_file = "base_points.npy"
points = npyLoad(points_file)

diagram = alphaShapeDiag(points)

png(file='base_diagram.png', width=1024, height=1024, res=200, units="px")

deathTimeList = diagram[["diagram"]][,"Death"]

orderedDeathTimeIndexes = order(deathTimeList, decreasing = TRUE)

diagramScaleLimit = 50

for (index in orderedDeathTimeIndexes) {
    if (deathTimeList[index] != Inf) {
        diagramScaleLimit = ceiling(deathTimeList[index] * 1.2)
        break
    }
}

plot.diagram(diagram[["diagram"]], main = "Persistence Diagram", diagLim = cbind(0, diagramScaleLimit))

write.table(diagram[["diagram"]], file="base_diagram.table", sep=",")
