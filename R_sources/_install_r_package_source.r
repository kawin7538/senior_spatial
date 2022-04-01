custom_package_install<-function(){
    install.packages("dplyr",dependencies=TRUE)
    install.packages("sp",dependencies=TRUE)
    install.packages("rgdal",dependencies=TRUE)
    install.packages("RColorBrewer",dependencies=TRUE)
    install.packages("geodata",dependencies=TRUE)
    install.packages("spdep",dependencies=TRUE)
    # install.packages(c("dplyr","sp","rgdal","RColorBrewer","geodata","spdep"),dependencies=TRUE)
    install.packages("INLA",repos=c(getOption("repos"),INLA="https://inla.r-inla-download.org/R/stable"), dependencies=TRUE)
    # installedPreviously<-read.csv("R_sources/r_installed_previously.csv")
    # baseR<-as.data.frame(installed.packages())
    # toInstall<-setdiff(installedPreviously,baseR)
    # toInstall=installedPreviously
    # print(toInstall[,"Package"])
    # install.packages(toInstall[,"Package"],dependencies=TRUE)
}