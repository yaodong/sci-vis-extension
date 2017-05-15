#!/usr/bin/env bash

# for more details:
# https://www.digitalocean.com/community/tutorials/how-to-install-r-on-ubuntu-16-04-2

apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9

add-apt-repository 'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu xenial/'

apt-get update

apt-get install r-base

which R
