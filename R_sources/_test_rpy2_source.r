library(dplyr)
library(sp)
library(rgdal)
library(RColorBrewer)
library(geodata)
library(spdep)
library(INLA)

pop.df<-read.csv("testcase_modules/DF_case_mean_allyears.csv",stringsAsFactors=FALSE)

thai_map2<-geodata::gadm(country="Thailand",level=1,path='preprocessed_data')
adj_list=adjacent(thai_map2[order(thai_map2$NAME_1),],type='queen',symmetrical=TRUE)
# add pair "Phung Nga" and "Phuket"
adj_list<-rbind(adj_list,c(39,48))
adj_mat<-matrix(0,77,77)
adj_mat[adj_list]<-1
adj_mat[adj_list[,c(2,1)]]<-1
W<-mat2listw(adj_mat,style='B')

func1 <- function(test_df){
    test_df['ID']<-1:nrow(test_df)
    test_df['E']<-pop.df['total']*100000
    test_df['total_raw']<-test_df['total']
    test_df$total<-as.integer(with(test_df,total*E))

    thai_map2.corrected<-merge(thai_map2,test_df,by='NAME_1')
    
    print(test_df)

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

    # spplot(thai_map2.corrected,"total_raw",do.log=TRUE,scales=list(draw=TRUE))

    # spplot(thai_map2.corrected,"besag",do.log=TRUE,scales=list(draw=TRUE))

    plot(thai_map2.corrected$total,thai_map2.corrected$besag_E)
    abline(0,1)

    marginal<-custommodel.besag$marginals.fitted.values$fitted.Predictor.72
    marginal<-inla.smarginal(marginal)
    marginal<-data.frame(marginal)
    # library(ggplot2)
    # ggplot(marginal, aes(x = x, y = y)) + geom_line() +
    # labs(x = expression(beta[1]), y = "Density") +
    # geom_vline(xintercept = 0, col = "black") + theme_bw()

    marginal<-custommodel.besag$marginals.fitted.values
    exc <- sapply(custommodel.besag$marginals.fitted.values,
                FUN = function(marg){1-inla.pmarginal(q=2, marginal = marg)})
    # thai_map2.corrected[,'exc']<-exc

    # spplot(thai_map2.corrected,"exc",do.log=TRUE,scales=list(draw=TRUE))
    # print(thai_map2.corrected)
    # return(exc>0.95)

    test_df['exc']<-exc
    test_df['hotspot']<-exc>0.95

    return(test_df)
}