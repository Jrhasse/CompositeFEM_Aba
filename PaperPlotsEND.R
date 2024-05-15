library(latex2exp)
library(stringr)
library(readxl)

library(extrafont)
#font_import()
#loadfonts(device="win")
##Mesh sensitivty Analysis ####
windowsFonts(A = windowsFont("Calibri"))

##Figure 4 ####
#Take C80-0100 for the good simulation
#Take C80-0104 for the bad simulation 
#can probably use the same C80-0100 for the stress strain curve labelled plot.
###First plot####
dat1 <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\C80\Sys-lvl-rpt-0100.csv}")
dat1$KEperTotal <- dat1$Kinetic.energy..ALLKE.for.Whole.Model/(dat1$Internal.energy.ALLIE.for.Whole.Model + dat1$Kinetic.energy..ALLKE.for.Whole.Model)
dat1$KEperTotal[1] <- 0.5
summary.data <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\ElasticFeatures.csv}")
dat1.failuretime <- summary.data[summary.data$Name == "ElasticFeaturesC80-0100", "Failure.Time"]


dat2 <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\C80\Sys-lvl-rpt-0104.csv}")
dat2$KEperTotal <- dat2$Kinetic.energy..ALLKE.for.Whole.Model/(dat2$Internal.energy.ALLIE.for.Whole.Model + dat2$Kinetic.energy..ALLKE.for.Whole.Model)
dat2$KEperTotal[1] <- 0.5



png(file = "PaperPlots/Figure4.png", width = 8, height = 6, units = "in",
    res = 300)
plot(dat1$X, dat1$KEperTotal * 100, type = "l",
     ylab = "Kinetic Energy % per Total Energy",
     xlab = "Simulation Time",
     lwd = 2, ylim = c(0, 60),
     family = "A", cex.lab = 1.2, cex.axis = 1.2)
abline(v = dat1.failuretime, lty = 2)
abline(h = 5, lty = 2)
polygon(c(-0.2,-0.2, dat1$X[floor(0.2*nrow(dat1))], dat1$X[floor(0.2*nrow(dat1))]), 
        c(-0.2, 0.7, 0.7, -0.2)*100,
        col = rgb(0.2,0.2,0.2, alpha = 0.2))
lines(dat2$X, dat2$KEperTotal*100, lwd = 2, col = "blue", lty = 4)
polygon(c(-0.2,-0.2, dat2$X[floor(0.2*nrow(dat2))], dat2$X[floor(0.2*nrow(dat2))]), 
        c(-0.2, 0.7, 0.7, -0.2)*100,
        col = rgb(0,0,1, alpha = 0.2))
text(0.26, 50, "Burn-in \n phase", family = "A", cex = 1.2)
arrows(0.21, 50, dat1$X[floor(0.2*nrow(dat1))], 45, code = 2,
       lwd = 1.5, length = 0.125, col = "blue")
arrows(0.21, 50, dat2$X[floor(0.2*nrow(dat2))], 50,
       lwd = 1.5, length = 0.125, col = "blue")

text(0.38, 13, "Maximum Energy Cutoff (5%)", family = "A", cex = 1.2)
arrows(0.38, 11, 0.38, 5, lwd = 1.5, length = 0.125, col = "blue")

text(0.70, 13, "Failure Time", family = "A", cex = 1.2)
arrows(0.77, 13, dat1.failuretime, dat1$KEperTotal[dat1$X == dat1.failuretime],
       lwd = 1.5, length = 0.125, col = "blue")
legend(x = 0.5, y = 62, legend = c("Accepted Simulation", "Rejected Simulation"),
       col = c("black", "blue"), lty = c(1, 4), lwd = 2)
dev.off()

###Second Plot####
SYStoSSDF <- function(filepath){
    tempdf <- read.csv(filepath)
    
    time <- tempdf$X
    stress <- ((abs(tempdf[,4]) + abs(tempdf[,5]))/2)/ 0.03 
    #The 0.03 is the matrix height for these files; easier that loading the input log
    strain <- ((abs(tempdf[,6]) + abs(tempdf[,7]))/2)/ 0.75
    #The 0.75 is the matrix length... same reason
    return(data.frame(time, stress, strain))
    
}

SS.dat1 <- SYStoSSDF(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\C80\Sys-lvl-rpt-0100.csv}")


ind1 <- 400
ind2 <- 600


png(file = "PaperPlots/Figure4b.png", width = 6, height = 6, units = "in",
    res = 300)
plot(SS.dat1$strain * 100, SS.dat1$stress, type = "l", lwd = 2,
     xlab = "Strain % ", ylab = "Stress", family = "A",
     cex.axis = 1.4, cex.lab = 1.4)
polygon(c(SS.dat1$strain * 100, SS.dat1$strain[nrow(SS.dat1)]*100, 0),
        c(SS.dat1$stress, 0, 0), col = rgb(0.2,0.2,0.2, 0.3), border = NA)
points(SS.dat1$strain[which.max(SS.dat1$stress)]*100,
       SS.dat1$stress[which.max(SS.dat1$stress)],
       pch = 15, cex = 1.5)
text(SS.dat1$strain[which.max(SS.dat1$stress)]*100 - 0.02,
     SS.dat1$stress[which.max(SS.dat1$stress)],
     TeX("Ultimate tensile strength $(\\sigma_{UTS})$"),
     family = "A", adj = 1)
arrows(SS.dat1$strain[which.max(SS.dat1$stress)]*100 - 0.02,
       SS.dat1$stress[which.max(SS.dat1$stress)],
       SS.dat1$strain[which.max(SS.dat1$stress)]*100,
       SS.dat1$stress[which.max(SS.dat1$stress)],
       length = 0.125, lwd = 1.5, col = "blue")

points(SS.dat1$strain[nrow(SS.dat1)]*100,
       SS.dat1$stress[nrow(SS.dat1)],
       pch = 18, cex = 2)
text(SS.dat1$strain[nrow(SS.dat1)]*100,
     SS.dat1$stress[nrow(SS.dat1)]-125,
     TeX("Failure strength $(\\sigma_{FS})$"),
     family = "A",
     adj = 1)
arrows(SS.dat1$strain[nrow(SS.dat1)] * 100 - 0.02,
       SS.dat1$stress[nrow(SS.dat1)] -100,
       SS.dat1$strain[nrow(SS.dat1)] * 100,
       SS.dat1$stress[nrow(SS.dat1)], lwd = 1.5,
       length = 0.125, col = "blue")


segments(SS.dat1$strain[ind1]*100, SS.dat1$stress[ind1],
         SS.dat1$strain[ind2]*100, SS.dat1$stress[ind1])
segments(SS.dat1$strain[ind2]*100, SS.dat1$stress[ind2],
         SS.dat1$strain[ind2]*100, SS.dat1$stress[ind1])
text(SS.dat1$strain[ind1]*100 - 0.01, SS.dat1$stress[ind2]+50, "Elastic \n Modulus (E)",
     family= "A", adj = 0.25)
arrows(SS.dat1$strain[ind1]*100, SS.dat1$stress[ind2],
       SS.dat1$strain[mean(c(ind1, ind2))]*100, 
       SS.dat1$stress[mean(c(ind1, ind2))],
       lwd = 1.5, length = 0.125, col = "blue")
text(0.15, 100, TeX("Toughness $(U_{T})$"), family = "A")

dev.off()


#Figure 6 ####
#Reduced data plots
###Setup####
storage <- list()
sheetnames <- c("YNB001-Weak", "YNB001-Strong", "YNB002-Weak", "YNB002-Strong",
                "YNB003-Weak", "YNB003-Strong")
cols <- c("red", "red", "blue", "blue", "darkgreen", "darkgreen")
pchs <- c(1,19,1,19,1,19)
ars <- c(75,75,60,60,40,40)
for(i in 1:length(sheetnames)){
    tmp <- read_excel(path = r"{C:\Users\jason\Documents\Grad\AFRL Research\AFRL-Code\R - AFRL\ReducedDataPrasad.xlsx}",
                        sheet = sheetnames[i])
    storage[[i]] <- as.data.frame(tmp)
}


options(digits = 10, scipen = 100)
plotsize <- 6
extraheader <- rep(1, 2*plotsize + 1)
layoutmat <- c(c(1, rep(2, plotsize), rep(3, plotsize)),
    rep(c(4, rep(5, plotsize), rep(6, plotsize)), plotsize),
    rep(c(7, rep(8, plotsize), rep(9, plotsize)), plotsize),
    rep(c(10, rep(11, plotsize), rep(12, plotsize)), plotsize))

###Elastic Mod####
png(file = "PaperPlots/ElasticMod.png", height = 8, width = 6,
    units = "in", res = 300)
layout(mat = matrix(c(extraheader, layoutmat+1), ncol = 2*plotsize + 1,
                    nrow = 3*plotsize + 1 + 1, byrow = TRUE))
par(mar = rep(0.1,4))
plot.new()
text(0.5, 0.25, "Elastic Modulus (GPa)", cex = 2, adj = 0.5, xpd = TRUE,
     family = "A")
#Header plot ^^
plot.new()
plot.new()
text(0.5,0.25,"Weak Cohesive Properties", cex = 1.5, adj = 0.5, xpd = TRUE,
     family = "A")
plot.new()
text(0.5,0.25,"Strong Cohesive Properties", cex = 1.5, adj = 0.5, xpd = TRUE,
     family = "A")
for(i in 1:length(sheetnames)){
    if(i %% 2 == 1){
        par(mar = rep(0.1,4))
        plot.new()
        text(0.5, 0.5, paste0("AR = ", ars[i]), srt = 90, cex = 1.5, family = "A")
    }
    par(mar = c(3,2,2,2) + 0.1)
    plot(storage[[i]]$area, storage[[i]]$Slope,
         ylab = "Elastic Modulus", xlab = "",
         col = cols[i], pch = pchs[i],
         ylim = c(1,6)*100000,
         xlim = c(0.75, 0.95),
         cex = 1.25,
         family = "A")
    tmp_mod <- lm(storage[[i]]$Slope ~ storage[[i]]$area)
    abline(tmp_mod, lty = 4)
    legend("topleft", legend = TeX(sprintf(r"{$R^2 = %f$}", round(summary(tmp_mod)$r.squared, 4)))) 
               #paste0(TeX("$R\\^2 = $"), round(summary(tmp_mod)$r.squared,3)))
}
dev.off()

###Ultimate Strength ####
png(file = "PaperPlots/UTS.png", height = 8, width = 6,
    units = "in", res = 300)
layout(mat = matrix(c(extraheader, layoutmat+1), ncol = 2*plotsize + 1,
                    nrow = 3*plotsize + 1 + 1, byrow = TRUE))
par(mar = rep(0.1,4))
plot.new()
text(0.5, 0.25, "Ultimate Tensile Strength", cex = 2, adj = 0.5, xpd = TRUE,
     family = "A")
#Header plot ^^
plot.new()
plot.new()
text(0.5,0.25,"Weak Cohesive Properties", cex = 1.5, adj = 0.5, xpd = TRUE,
     family = "A")
plot.new()
text(0.5,0.25,"Strong Cohesive Properties", cex = 1.5, adj = 0.5, xpd = TRUE,
     family = "A")
for(i in 1:length(sheetnames)){
    if(i %% 2 == 1){
        par(mar = rep(0.1,4))
        plot.new()
        text(0.5, 0.5, paste0("AR = ", ars[i]), srt = 90, cex = 1.5,
             family = "A")
    }
    par(mar = c(3,2,2,2) + 0.1)
    plot(storage[[i]]$area, storage[[i]]$Max_y,
         ylab = "Elastic Modulus", xlab = "",
         col = cols[i], pch = pchs[i],
         ylim = c(40, 750),
         xlim = c(0.75, 0.95),
         cex = 1.25,
         family = "A")
    tmp_mod <- lm(storage[[i]]$Max_y ~ storage[[i]]$area)
    abline(tmp_mod, lty = 4)
    legend("topleft", legend = TeX(sprintf(r"{$R^2 = %f$}", round(summary(tmp_mod)$r.squared, 4)))) 
}
dev.off()



options(scipen = 0, digits = 7)


#Figure 8####

#Need to modify this plot yet.

# FullyConnected <- SYStoSSDF("~/Grad/AFRL Research/Data/YNB-001/C80/Sys-lvl-rpt-0114.csv")
# new_files <- list.files(path = r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A}",
#                         pattern = "*.csv")
# new_files <- paste0(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A\}", new_files )
# 
# storage <- list()
# storage[[1]] <- FullyConnected
# for(i in 1:15){
#     storage[[i+1]] <- SYStoSSDF(new_files[i])
# }
# 
# 
# summaryfeatures1 <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\ElasticFeatures.csv}")
# fail.time <- summaryfeatures1[summaryfeatures1$Name == "ElasticFeaturesC80-0114", 2]
# summaryfeatures2 <- read.csv(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\ElasticFeatures.csv}")
# fail.time <- c(fail.time, summaryfeatures2$Failure.Time)
# fail.time
# 
# 
# 
# plot(storage[[1]]$strain[storage[[1]]$time < fail.time[1]],
#      storage[[1]]$stress[storage[[1]]$time < fail.time[1]],
#      type = "l", lwd = 4,
#      ylab = "stress", xlab = "strain")
# linetypes <- c(1,rep(c(2,3,4), each = 5))
# for(i in 2:16){
#     if(fail.time[i] != -1.0){
#         lines(storage[[i]]$strain[storage[[i]]$time < fail.time[i]],
#               storage[[i]]$stress[storage[[i]]$time < fail.time[i]],
#               col = "darkgreen",
#               lwd = 2,
#               lty = linetypes[i])
#     }
#     else{
#         lines(storage[[i]]$strain,
#               storage[[i]]$stress,
#               col = "red",
#               lwd = 2,
#               lty = linetypes[i])
#     }
# }
# legend("bottomright", legend = c("Fully connected", "Good Simulation", "Bad Simulation",
#                                  "Fully Connected", "25% Broken", "50% Broken", "75% Broken"),
#        col = c("black", "darkgreen", "red", rep("black", 4)),
#        lty = c(1, 1, 1, 1, 2, 3, 4),
#        lwd = c(4, rep(2,6)))



#Broken Connections plots4

SS1 <- SYStoSSDF(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\C80\Sys-lvl-rpt-0114.csv}")
folder1 <- r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\B}"
fp1 <- list.files(path = folder1, pattern = "*.csv")

SS2 <- SYStoSSDF(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\C80\Sys-lvl-rpt-0110.csv}")
folder2 <- r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\C}"
fp2 <- list.files(path = folder2, pattern = "*.csv")

SS3 <- SYStoSSDF(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002\C80\Sys-lvl-rpt-0118.csv}")
folder3 <- r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\D}"
fp3 <- list.files(path = folder3, pattern = "*.csv")

SS4 <- SYStoSSDF(r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003\C80\Sys-lvl-rpt-0108.csv}")
folder4 <- r"{C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\E}"
fp4 <- list.files(path = folder4, pattern = "*.csv")

SS.list <- list(SS1, SS2, SS3, SS4)
folder.list <- list(folder1, folder2, folder3, folder4)
fp.list <- list(fp1, fp2, fp3, fp4)



# pdf(file = "PaperPlots/MeshSens.pdf", height = 8, width = 8)
# 
# mycols <- rep(c("red", "blue", "green"), each = 5)
# par(mar = c(3.1, 3.1, 2.1, 2.1),
#     xpd = FALSE)
# bb <- 5
# layoutmat2 <- matrix(c(rep(1, bb), rep(2, bb), 5,
#                        rep(3, bb), rep(4, bb), 5),
#                      nrow = 2, ncol = 2*bb+1,
#                      byrow = TRUE)
# layout(layoutmat2)
# for(aa in 1:length(SS.list)){
#     plot(SS.list[[aa]]$strain, SS.list[[aa]]$stress, type = "l", lwd = 3,
#          xlab = "Strain", ylab = "Stress")
#     for(i in 1:length(fp1)){
#         tmp <- SYStoSSDF(paste0(folder.list[[aa]], "\\", fp.list[[aa]][i]))
#         lines(tmp$strain, tmp$stress, col = mycols[i])
#     }
# }
# plot.new()
# par(xpd = TRUE)
# legend("center", legend = c("0%", "10%", "25%", "50%"),
#        col = c("black", "red", "blue", "green"),
#        lwd = c(3,1,1,1), lty = 1)
# 
# dev.off()
# 


#Just the top left plot and reduce the plot per the cutoff time. 


SS1
#fail.time1 <- 0.921501

windowsFonts(A = windowsFont("Calibri"))


png(file = "PaperPlots/UpdatedBrokenConnections.png", width = 8, height = 8,
    units = "in", res = 300)
par(mar = c(5.1, 4.1, 2.1, 2.1))
plot(SS1$strain*100, SS1$stress,
     type = "l", xlim = c(0, 0.055), ylim = c(0, 250),
     family = "A", cex.lab = 1.6, cex.axis = 1.6,
     lwd = 3, xlab = "Strain %", ylab = "Stress (MPa)")
for(i in 1:length(fp1)){
    tmp <- SYStoSSDF(paste0(folder1, "\\", fp1[i]))
    lines(tmp$strain*100, tmp$stress, col = mycols[i], lwd = 1.5)
}
legend("topleft", legend = c("0%", "10%", "25%", "50%"),
       col = c("black", "red", "blue", "green"),
       lwd = c(3,1.5,1.5,1.5))
dev.off()
