func1 <- function(x,y){
    png("plot_preview.png")
    plot(x,y)
    abline(0,1)
    dev.off()
}