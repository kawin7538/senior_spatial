library(dplyr)
library(sp)
library(rgdal)
library(RColorBrewer)
library(geodata)
library(spdep)
library(INLA)
library(rsatscan)

pop.df<-read.csv("testcase_modules/DF_case_mean_allyears.csv",stringsAsFactors=FALSE)

thai_map2<-geodata::gadm(country="Thailand",level=1,path='preprocessed_data')
adj_list=adjacent(thai_map2[order(thai_map2$NAME_1),],type='queen',symmetrical=TRUE)
# add pair "Phung Nga" and "Phuket"
adj_list<-rbind(adj_list,c(39,48))
adj_mat<-matrix(0,77,77)
adj_mat[adj_list]<-1
adj_mat[adj_list[,c(2,1)]]<-1
W<-mat2listw(adj_mat,style='B')
centroid<-centroids(thai_map2)

run_besag <- function(test_df){
    test_df['ID']<-1:nrow(test_df)
    test_df['E']<-pop.df['total']*100000
    test_df['total_raw']<-test_df['total']
    test_df$total<-as.integer(with(test_df,total*E))

    thai_map2.corrected<-merge(thai_map2,test_df,by='NAME_1')

    formula<-total~1+f(ID,model="besag",graph=listw2mat(W))

    custommodel.besag<-inla(
        formula,
        data=test_df,
        family="poisson",
        E=E,
        control.compute=list(dic=TRUE, waic=TRUE, cpo=TRUE,return.marginals.predictor=TRUE),
        control.predictor=list(compute=TRUE)
    )

    thai_map2.corrected[,'besag']<-(custommodel.besag$summary.fitted.values$mean)
    thai_map2.corrected[,'besag_E']<-(custommodel.besag$summary.fitted.values$mean*test_df['E'])

    marginal<-custommodel.besag$marginals.fitted.values
    exc <- sapply(custommodel.besag$marginals.fitted.values,
                FUN = function(marg){1-inla.pmarginal(q=1, marginal = marg)})

    test_df['exc']<-exc
    test_df['cl']<-exc>0.95

    return(test_df)
}

run_bym <- function(test_df){
    test_df['ID']<-1:nrow(test_df)
    test_df['E']<-pop.df['total']*100000
    test_df['total_raw']<-test_df['total']
    test_df$total<-as.integer(with(test_df,total*E))

    thai_map2.corrected<-merge(thai_map2,test_df,by='NAME_1')

    formula<-total~1+f(ID,model="bym",graph=listw2mat(W))

    custommodel.besag<-inla(
        formula,
        data=test_df,
        family="poisson",
        E=E,
        control.compute=list(dic=TRUE, waic=TRUE, cpo=TRUE,return.marginals.predictor=TRUE),
        control.predictor=list(compute=TRUE)
    )

    thai_map2.corrected[,'bym']<-(custommodel.besag$summary.fitted.values$mean)
    thai_map2.corrected[,'bym_E']<-(custommodel.besag$summary.fitted.values$mean*test_df['E'])

    marginal<-custommodel.besag$marginals.fitted.values
    exc <- sapply(custommodel.besag$marginals.fitted.values,
                FUN = function(marg){1-inla.pmarginal(q=1, marginal = marg)})

    test_df['exc']<-exc
    test_df['cl']<-exc>0.95

    return(test_df)
}

run_satscan <- function(test_df){
    test_df['ID']<-1:nrow(test_df)
    test_df['E']<-pop.df['total']*100000
    test_df['total_raw']<-test_df['total']
    test_df['year']<-1
    test_df$total<-as.integer(with(test_df,total*E))

    thai_map2.corrected<-merge(thai_map2,test_df,by='NAME_1')

    test_df[,c('x','y')]<-geom(centroid)[,c('x','y')]
    case.df<-test_df[,c('ID','total')]
    case.df<-case.df%>%rename(cases=total)
    pop.df<-test_df[,c('ID','year','E')]
    pop.df<-pop.df%>%rename(population=E)
    geo.df<-test_df[,c('ID','x','y')]

    td = tempdir()
    write.cas(case.df, td,"Testcase")
    write.geo(geo.df, td,"Testcase")
    write.pop(pop.df, td,"Testcase")
    invisible(ss.options(reset=TRUE))
    ss.options(list(CaseFile="Testcase.cas", PrecisionCaseTimes=0,
                    PopulationFile="Testcase.pop",
                    CoordinatesFile="Testcase.geo", CoordinatesType=0, AnalysisType=1,
                    ModelType=0, ScanAreas=1, TimeAggregationUnits=0, MaxSpatialSizeInPopulationAtRisk_Reported=25,MaxSizeInMaxCirclePopulationFile_Reported=25))
    ss.options(c("NonCompactnessPenalty=0", "ReportGiniClusters=n", "LogRunToHistoryFile=n"))
    write.ss.prm(td,"Testcase")
    testcase_satscan = satscan(td,"Testcase",sslocation="satscan_sources",ssbatchfilename="satscan_stdc++6_x86_64_64bit",verbose = FALSE)
    
    cluster.center<-testcase_satscan$col
    hotspot<-testcase_satscan$gis

    hotspot.tmp<-hotspot
    hotspot.tmp<-as.integer(as.character(hotspot.tmp[hotspot.tmp$P_VALUE<0.05,"LOC_ID"]))
    test_df[,'cl']<-FALSE
    test_df[hotspot.tmp,'cl']<-TRUE

    return(test_df)
}