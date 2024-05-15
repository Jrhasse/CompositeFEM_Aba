SYStoSSDF <- function(filepath){
    tempdf <- read.csv(filepath)
    
    time <- tempdf$X
    stress <- ((abs(tempdf[,4]) + abs(tempdf[,5]))/2)/ 0.03 
    #The 0.03 is the matrix height for these files; easier that loading the input log
    strain <- ((abs(tempdf[,6]) + abs(tempdf[,7]))/2)/ 0.75
    #The 0.75 is the matrix length... same reason
    return(data.frame(time, stress, strain))
    
}

library(stringr)
folder <-r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A\}"
csvs <- list.files(path = folder, pattern = "Sys-lvl-rpt-")

for(i in 1:length(csvs)){
    write.csv(SYStoSSDF(paste0(folder,csvs[i])),
              file = paste0(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\SS-}", str_pad(i, 4, side = "left", pad  = 0), ".csv"))
}
