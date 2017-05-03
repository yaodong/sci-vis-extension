#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]

library("TDA")

maxscale <- 10
maxdimension <- 1

data <- read.csv(paste(work_dir ,"/base.diagram", sep=""), header=FALSE)
diagram <- cbind(data[,1], data[,2], data[,3])


png(file=paste(work_dir, "/", 'base_diagram.png', sep=""), width=1280, height=1280, res=200, units="px")

plot.diagram(diagram, main = "Persistence Diagram")

dev.off()
