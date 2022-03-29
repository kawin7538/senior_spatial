custom_package_install<-function(){
    install.packages("dplyr")
    install.packages("sp")
    install.packages("rgdal")
    install.packages("RColorBrewer")
    install.packages("geodata")
    install.packages("spdep")
    install.packages("INLA",repos=c(getOption("repos"),INLA="https://inla.r-inla-download.org/R/stable"), dep=TRUE)
}