#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]

setwd(work_dir)


library(TDA)
library(RcppCNPy)


points_file = "base_points.npy"
points = npyLoad(points_file)

diagram = alphaShapeDiag(points)

png(file='base_diagram.png', width=800, height=800, res=200, units="px")

plot.diagram(diagram[["diagram"]], main = "Persistence Diagram")

write.table(diagram[["diagram"]], file="base_diagram.table", sep=",")
