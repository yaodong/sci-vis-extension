#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
work_dir = args[1]
base_filename = args[2]
proj_filename = args[3]
out_filename = args[4]
pic_filename = args[5]

library("TDA")

maxscale <- 10
maxdimension <- 1

base_file = paste(work_dir, "/", base_filename, sep="")
proj_file = paste(work_dir, "/", proj_filename, sep="")
out_file = paste(work_dir, "/", out_filename, sep="")


base_data <- read.csv(base_file, header=FALSE)
base_diagram = cbind(base_data[,1], base_data[,2], base_data[,3])

proj_data <- read.csv(proj_file, header=FALSE)
proj_diagram <- cbind(proj_data[,1], proj_data[,2], proj_data[,3])

bottleneckDist <- bottleneck(base_diagram, proj_diagram, dimension = 1)
write(bottleneckDist, file = out_file)

png(file=paste(work_dir, "/", pic_filename, sep=""), width=1280, height=1280, res=200, units="px")

plot.diagram(proj_diagram, main = "Persistence Diagram")

dev.off()
