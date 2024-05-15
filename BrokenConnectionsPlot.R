SYStoSSDF <- function(filepath){
    tempdf <- read.csv(filepath)
    
    time <- tempdf$X
    stress <- ((abs(tempdf[,4]) + abs(tempdf[,5]))/2)/ 0.03 
    #The 0.03 is the matrix height for these files; easier that loading the input log
    strain <- ((abs(tempdf[,6]) + abs(tempdf[,7]))/2)/ 0.75
    #The 0.75 is the matrix length... same reason
    return(data.frame(time, stress, strain))
    
}

FullyConnected <- SYStoSSDF("~/Grad/AFRL Research/Data/YNB-001/C80/Sys-lvl-rpt-0114.csv")
new_files <- list.files(path = r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A}",
                        pattern = "*.csv")
new_files <- paste0(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A\}", new_files )

storage <- list()
storage[[1]] <- FullyConnected
for(i in 1:15){
    storage[[i+1]] <- SYStoSSDF(new_files[i])
}


summaryfeatures1 <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\ElasticFeatures.csv}")
fail.time <- summaryfeatures1[summaryfeatures1$Name == "ElasticFeaturesC80-0114", 2]
summaryfeatures2 <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\ElasticFeatures.csv}")
fail.time <- c(fail.time, summaryfeatures2$Failure.Time)
fail.time



plot(storage[[1]]$strain[storage[[1]]$time < fail.time[1]],
     storage[[1]]$stress[storage[[1]]$time < fail.time[1]],
     type = "l", lwd = 4,
     ylab = "stress", xlab = "strain")
linetypes <- c(1,rep(c(2,3,4), each = 5))
for(i in 2:16){
    if(fail.time[i] != -1.0){
        lines(storage[[i]]$strain[storage[[i]]$time < fail.time[i]],
              storage[[i]]$stress[storage[[i]]$time < fail.time[i]],
              col = "darkgreen",
              lwd = 2,
              lty = linetypes[i])
    }
    else{
        lines(storage[[i]]$strain,
              storage[[i]]$stress,
              col = "red",
              lwd = 2,
              lty = linetypes[i])
    }
}
legend("bottomright", legend = c("Fully connected", "Good Simulation", "Bad Simulation",
                                 "Fully Connected", "25% Broken", "50% Broken", "75% Broken"),
       col = c("black", "darkgreen", "red", rep("black", 4)),
       lty = c(1, 1, 1, 1, 2, 3, 4),
       lwd = c(4, rep(2,6)))
