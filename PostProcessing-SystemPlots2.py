# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:26:43 2022

@author: jason
"""
import math
import os
import shutil
import matplotlib.pyplot as plt

def MyNumDeriv(x, y, plot_tf = None, burnin = None, der_threshold = None,
               y_threshold = None, job_number = None):
    if(plot_tf is None):
        plot_tf = False
    if(burnin is None):
        burnin = 0.20
    if(der_threshold is None):
        der_threshold = 5
    if(y_threshold is None):
        y_threshold = 0.75
    if(job_number is None):
        job_number = ""
    burn_x = int(math.floor(burnin*len(x)))
        #if y falls below this value after burnin and before ending "indices"
        #raise a flag to say this shouldnt simulation be used.
        #time of -999
        
        
        
    #returns the x(s) that have a numerical derivative close to 0.
    #maybe it should return when the internal energy dips
    #x and y should be lists
    f_primes = []
    for i in range(len(y)-1):
        temp = (y[i+1] - y[i])/(x[i+1] - x[i])
        f_primes.append(temp)
    
    indices = []
    flag_1 = False
    flag_2 = False
    for j in range(burn_x, len(f_primes)):
        #This logic seems overcomplex but seems to work
        if((f_primes[j] < der_threshold and f_primes[j] > -1*der_threshold) or flag_1):
            flag_1 = True #inside the region at some point
            if(f_primes[j] > der_threshold or f_primes[j] < -1*der_threshold or flag_2):
                flag_2 = True
                #outside the region again
                indices.append(j)

    
    #Check if the kinetic energy is too high after the burnin
    flag_sim_good = True    
    if(len(indices) == 0):
        max_for_rejection = len(y)
    else:
        max_for_rejection = indices[0]
    
    for j in range(burn_x, max_for_rejection):
        if(y[j] < y_threshold):
            flag_sim_good = False
        
    
    if(plot_tf):
        plt.figure()
        plt.plot(x[1:len(x)], f_primes, linewidth = 0.5)
        plt.ylim(-10,10)
        plt.rcParams["figure.figsize"] = (8,6)
        plt.axhline(y = 0, color = "black")
        plt.axhline(y = der_threshold, color = "gray", linewidth = 0.5)
        plt.axhline(y = -1*der_threshold, color = "gray", linewidth = 0.5)
        if(not max_for_rejection == len(y)):
            plt.axvline(x = x[max_for_rejection], color = "green", linewidth = 0.5)
        plt.axvline(x = x[burn_x], color = "purple", linewidth = 0.5)
        plt.ylabel("Numerical Derivative Value")
        plt.xlabel("Time")
        plt.title("Numerical Derivatives Value over Time :{}".format(str(job_number)))
        
    
    if(flag_sim_good):
        return([indices, x[burn_x]])
    else:
        return([-999, x[burn_x]])

def GetFailureTime(energies_csv, plot_tf = None, file_aug = None, save_tf = None):
    job_number = energies_csv[(energies_csv.rfind("-")+1):(len(energies_csv)-4)]
    if(plot_tf is None):
        plot_tf = False
    if(file_aug is None):
        file_aug = ""
    if(save_tf is None):
        save_tf = False

    with open(energies_csv, "r", encoding = "utf-8") as energies:
        energies_lines = energies.readlines()


    #now extract out the X, Internal and Kinetic energies
    time = []
    internal = []
    kinetic = []
    total = []
    for i in range(1,len(energies_lines)):
        temp_line = energies_lines[i]
        temp_split = temp_line.split(",")
        time.append(float(temp_split[0]))
        internal.append(float(temp_split[1]))
        kinetic.append(float(temp_split[2]))
        total.append(float(temp_split[1]) + float(temp_split[2]))
        
    IoT = []
    KoT = []
    IoT.append(0.5)
    KoT.append(0.5)
    for i in range(1,len(internal)):
        IoT.append(internal[i] / total[i])
        KoT.append(kinetic[i] / total[i])
    
    axis_font = {'size':'18'}
    tick_size = 14
    legend_font_size = 14
    
    temp = MyNumDeriv(x= time, y = IoT, plot_tf = plot_tf, job_number = job_number)
    indices = temp[0]
    burn_time = temp[1]
    if(indices == -999):
        FT = -999
        if(plot_tf):
            plt.figure()
            plt.rcParams["figure.figsize"] = (8,6)
            plt.rc('xtick', labelsize = tick_size)
            plt.rc('ytick', labelsize = tick_size)
            plt.plot(time, IoT, linestyle = "solid", label = "Internal", color = "darkblue", linewidth = 2)
            plt.plot(time, KoT, linestyle = "dashed", label= "Kinetic", color = "orange", linewidth = 2)
            #plt.axvline(x = FT, linestyle = "solid", label = "Failure Time", color = "green", linewidth = 1)
            plt.axline([0,0], [time[len(time)-1], 1] , color = "Red", linewidth = 3)
            plt.axline([0,1], [time[len(time)-1], 0], color = "Red", linewidth = 3)
            plt.xlabel("Time", **axis_font)
            plt.ylabel("Relative Energy", **axis_font)
            #plt.title("Relative Energies over Time :{}".format(str(job_number)))
            #plt.title(str(job_number))
            plt.legend(prop = {'size': legend_font_size})
            if(save_tf):
                plt.savefig("RelativeEnegeriesPlot" + file_aug + "-" + job_number + ".png", dpi = 300, bbox_inches = "tight")
    else:
        if(not len(indices) == 0):
            FT = time[indices[0]]
        else:
            FT = -1
        if(plot_tf):
            plt.figure()
            plt.rcParams["figure.figsize"] = (8,6)
            plt.rc('xtick', labelsize = tick_size)
            plt.rc('ytick', labelsize = tick_size)
            plt.plot(time, IoT, linestyle = "solid", label = "Internal", color = "darkblue", linewidth = 2)
            plt.plot(time, KoT, linestyle = "dashed", label= "Kinetic", color = "orange", linewidth = 2)
            plt.axvline(x = FT, linestyle = "solid", label = "Failure Time", color = "green", linewidth = 1)
            plt.fill_between(x = [-0.05, burn_time], y1 = [1.5,1.5], y2 = [-0.5, -0.5],
                             facecolor = "lightgray", label = "Burn-in")
            plt.xlim(left = -0.02)
            plt.ylim(bottom = -0.05, top = 1.05)
            #plt.axvline(x = burn_time, label = "Burn-in", color = "lightgray", linewidth = 0.5)
            plt.xlabel("Time", **axis_font)
            plt.ylabel("Relative Energy", **axis_font)
            #plt.title("Relative Energies over Time :{}".format(str(job_number)))
            #plt.title(str(job_number))
            plt.legend(prop = {'size': legend_font_size})
            if(save_tf):
                plt.savefig("RelativeEnegeriesPlot" + file_aug + "-" + job_number + ".png", dpi = 300, bbox_inches = "tight")
    return(FT)

#now get the Stress strain plots
import matplotlib.pyplot as plt
import os
import math
# energies_csv = r"C:\Users\jason\OneDrive\Documents\SDSU\Grad\AFRL-Research\YNB-001\A70\Sys-lvl-rpt-0002.csv"
# fail_time = GetFailureTime(energies_csv, plot_tf = False, file_aug= False, save_tf = False)

def GetLinearElastic(rf, sd, proportion_data = None, scale_down_factor = None):
    if(proportion_data is None):
        proportion_data = 0.15

    #take the first 'proportion_data' of the data and fit a linear regression line to it
    #then scale down the slope and return those line values
    x = []
    y = []
    for i in range(math.floor(proportion_data * len(rf))):
        x.append(sd[i])
        y.append(rf[i])
    
    x_iy_i = []
    x_i_sq = []
    for i in range(len(x)):
        x_iy_i.append(x[i] * y[i])
        x_i_sq.append(x[i] * x[i])
    if(not(sum(x_i_sq) == 0)):
        beta_1 = sum(x_iy_i)/sum(x_i_sq)
    else:
        beta_1 = 0
        
    #need to shift the line to the right by x strain
    return(beta_1)


def GetAreaUnderCurve(Stress, Strain):
    #Used within GetVariousElasticFeatures
    #Should use
    total_int = 0
    for i in range((len(Stress)-1)):
        temp_width = (Strain[i+1] - Strain[i])
        temp_height = (Stress[i+1] + Stress[i])/2
        total_int = total_int + temp_width*temp_height
    return(total_int)
    

import math
def GetSingleRsq(X, Y):
    #X is whichever variable is on the X-axis, likewise for Y
    #X and Y same length
    Xbar = sum(X)/len(X)
    Ybar = sum(Y)/len(Y)
    
    numer = 0
    for i in range(len(X)):
        numer = numer + (X[i]-Xbar)*(Y[i]-Ybar)
    denom1 = 0
    denom2 = 0
    for i in range(len(X)):
        denom1 = denom1 + (X[i] - Xbar)**2
        denom2 = denom2 + (Y[i] - Ybar)**2
    denom = math.sqrt(denom1 * denom2)
    
    r = numer/denom
    r_sq = r**2
    return([r, r_sq])
    
    
    


def GetVariousElasticFeatures(slope, x_int_list, Stress, Strain, file_name, fail_time):
    #Should probably write them to a .txt file.
    #merge them to a csv file later
    
    master_list = []
    master_list.append(slope)
    
    mymax_y = max(Stress)
    for i in range(len(Stress)):
        if(Stress[i] == mymax_y):
            mymax_x = Strain[i]
    
    master_list.append([mymax_x, mymax_y])
    master_list.append([Strain[-1], Stress[-1]])
    
    
    #first get the equation of the lines
    residuals_list = []
    b_0_list = []
    for i in range(len(x_int_list)):
        b_0 = -1*slope*x_int_list[i]
        b_0_list.append(b_0)
        temp_resid_list = []
        for j in range(len(Strain)):
            temp_fitted = b_0 + slope*Strain[j]
            temp_resid = Stress[j] - temp_fitted
            temp_resid_list.append(temp_resid)
        residuals_list.append(temp_resid_list)
    
        
    for i in range(len(residuals_list)):
        flag_tf = False
        for j in range((len(residuals_list[i])-1)):
            if((residuals_list[i][j] * residuals_list[i][j+1] < 0) or (residuals_list[i][j] == 0)):
                flag_tf = True
                index = j
                break
        if(flag_tf):
            m = (residuals_list[i][index] - residuals_list[i][index+1])/(Strain[index] - Strain[index + 1])
            x_d = -1*residuals_list[i][index]/m
            predicted_intersection_x = x_d + Strain[index]
            predicted_intersection_y = b_0_list[i] + slope*predicted_intersection_x
            master_list.append([predicted_intersection_x, predicted_intersection_y])
        else:
            master_list.append([-999,-999])
    
    total_energy = GetAreaUnderCurve(Stress, Strain)
    with open(file_name, "w") as file:
        file.write("Failure Time: " + str(fail_time) + "\n")
        file.write("Slope: " + str(master_list[0]) + "\n")
        file.write("AUC: " + str(total_energy) + "\n")
        file.write("Max: " + str(master_list[1])[1:-1] + "\n")
        file.write("Failure: " + str(master_list[2])[1:-1] + "\n")
        for i in range(len(x_int_list)):
            file.write("Offset Line " + str(x_int_list[i]) + ": " +  str(master_list[i + 3])[1:-1] + "\n")
        
    return(master_list)

import os
def MergeElasticProperties(directory_list, output_location):
    flag = True #to print the header
    k = 3 #This is for me to remember how many things I want to put in front of the lines
    with open(output_location + "/ElasticFeatures.csv", "w") as master_file:
        for a in range(len(directory_list)):
            file_names = os.listdir(directory_list[a])
            mytxtfiles = []
            for i in range(len(file_names)):
                if("ElasticFeatures" in file_names[i]):
                    mytxtfiles.append(file_names[i])
            #get header information out once
            if(flag):
                header = []
                header.append("Name")           #k = 0
                header.append("Failure Time")   #k = 1
                header.append("Slope")          #k = 2
                header.append("AUC")            #k = 3
                with open(directory_list[a] + "/" + mytxtfiles[0]) as temp_file:
                    header_lines = temp_file.readlines()
                for zz in range(k,len(header_lines)):
                    temp_line = header_lines[zz]
                    header.append(temp_line[:temp_line.find(":")] + "_x")
                    header.append(temp_line[:temp_line.find(":")] + "_y")
                header_str = ", ".join(header) + "\n"
                master_file.write(header_str)
                flag = False
            #Now the header should be written once
            
            for i in range(len(mytxtfiles)):
                with open(directory_list[a] + "/" + mytxtfiles[i]) as txt_file:
                    txt_files_lines = txt_file.readlines()
                new_line_master = []
                new_line_master.append(mytxtfiles[i][:mytxtfiles[i].find(".")])#whatever the file name is??
                new_line_master.append(str(txt_files_lines[0][(txt_files_lines[0].find(":")+2):txt_files_lines[0].find("\n")])) #Failure Time
                new_line_master.append(str(txt_files_lines[1][(txt_files_lines[1].find(":")+2):txt_files_lines[1].find("\n")])) #Slope
                new_line_master.append(str(txt_files_lines[2][(txt_files_lines[2].find(":")+2):txt_files_lines[2].find("\n")])) #AUC
                #the above two defined indices the first part of "k" above
                for j in range(k,len(txt_files_lines)):
                    #finish getting the info from the text files
                    temp_line = txt_files_lines[j]
                    #get the first value out
                    First = str(temp_line[(temp_line.find(":")+2):temp_line.find(",")])
                    Second = str(temp_line[(temp_line.find(",")+2):temp_line.find("\n")])
                    new_line_master.append(First)
                    new_line_master.append(Second)
                new_line_master_entry = ", ".join(new_line_master) +"\n"
                master_file.write(new_line_master_entry)


#energies_csv = r"C:\Users\jason\OneDrive\Documents\SDSU\Grad\AFRL-Research\YNB-001\A70\Sys-lvl-rpt-0000.csv"
#input_log = r"C:\Users\jason\OneDrive\Documents\SDSU\Grad\AFRL-Research\YNB-001\A70\InputLog-0000.txt"

def StressStrainPlots(energies_csv, input_log, fail_time = None, file_aug = None,
                      proportion_data = None, scale_down_factor = None, save_tf = None, plot_tf = None):
    job_number = energies_csv[(energies_csv.rfind("-")+1):(len(energies_csv)-4)]
    
    bad_sim = False
    if(fail_time is None):
        fail_time = 1000 #get all results
    if(fail_time < 0):
        fail_time = 1000
        bad_sim = True
    if(file_aug is None):
        file_aug = ""
    if(plot_tf is None):
        plot_tf = False
    
    
    with open(energies_csv, "r", encoding = "utf-8") as energies:
        energies_lines = energies.readlines()
    #closes the file right away if there is an error
    
    rf_l = []
    rf_r = []
    sd_l = []
    sd_r = []
    for i in range(1, len(energies_lines)):
        temp_line = energies_lines[i]
        temp_split = temp_line.split(",")
        temp_time = float(temp_split[0])
        if(temp_time < fail_time):
            rf_l.append(abs(float(temp_split[3])))
            rf_r.append(float(temp_split[4]))
            sd_l.append(abs(float(temp_split[5])))
            sd_r.append(float(temp_split[6]))
    
    
    with open(input_log, "r", encoding = "utf-8") as in_log:
        input_log_lines = in_log.readlines()
    
    for line in input_log_lines:
        if("matrix_length" in line):
            matrix_length = float(line[(line.find(':')+1):len(line)])
        if("matrix_height" in line):
            matrix_height = float(line[(line.find(':')+1):len(line)])
    
    #convert to stress and strain
    #Stress = Force / Area
    #Force is average of abs(reaction forces)
    #Area is based on Thickness and Width
    Stress = []
    Area = matrix_height #*1 #since we are 2D
    for i in range(len(rf_l)):
        avg_force = (abs(rf_l[i]) + abs(rf_r[i]))/2
        temp = avg_force/Area
        Stress.append(temp)
    
    #Strain = Relative Deformation / Initial length
    #rel def is average of abs(strain)
    
    Strain = []
    for i in range(len(sd_l)):
        avg_strain = (abs(sd_l[i]) + abs(sd_r[i]))/2
        temp = avg_strain/matrix_length
        Strain.append(temp)
    
    
    slope = GetLinearElastic(Stress, Strain, proportion_data = proportion_data)
    #We can get where the line intersects the stress strain by
    #seeing if the equation of the line (point slope for to start)
    #has values that correspond with Strain and Stress
    
    
    ####
    x_int_list = [0.0001, 0.0002, 0.0005]
    if(bad_sim):
        fail_time = -1
    GetVariousElasticFeatures(slope = slope, x_int_list = x_int_list,
                              Stress = Stress, Strain = Strain,
                              file_name = "ElasticFeatures" + file_aug + "-" + job_number + ".txt",
                              fail_time = fail_time)
    ####
    
    

    mymax_y = max(Stress)
    for i in range(len(Stress)):
        if(Stress[i] == mymax_y):
            mymax_x = Strain[i]
    
    axis_font = {'size':'18'}
    tick_size = 14
    legend_font_size = 14
    if(plot_tf):
        if(not(bad_sim)):
            plt.figure()
            plt.rcParams["figure.figsize"] = (8,6)
            plt.plot(Strain, Stress, color = "black", label = "Average", linewidth = 3)
            #plt.plot(sd_r, rf_r, color = "blue", label = "Right", linewidth = 3)
            #plt.title("Stress Strain Plot")
            plt.xlabel("Strain", **axis_font)
            plt.ylabel("Stress", **axis_font)
            plt.axline([0.0001,0], slope = slope, color = "lightblue", label = "0.01%")
            plt.axline([0.0002,0], slope = slope, color = "blue", label = "0.02%")
            plt.axline([0.0005,0], linestyle = "dashed",  slope = slope, color = "darkblue", label = "0.05%")
            plt.legend(prop = {'size': legend_font_size})
            plt.scatter(mymax_x, mymax_y, s = 4*plt.rcParams['lines.markersize']**2 , marker = "x", c = "green")
            if(save_tf):
                plt.savefig("StressStrainPlot" + file_aug + "-" + job_number + ".png", dpi = 300, bbox_inches = "tight")
        else:
            plt.figure()
            plt.axes().set_facecolor("gray")
            plt.plot(Strain, Stress, color = "black", label = "Average")
            #plt.title("Stress Strain Plot")
            plt.xlabel("Strain")
            plt.ylabel("Stress")
            plt.legend()
            plt.axline([0,0], [max(Strain), max(Stress)], color = "red")
            plt.axline([0,max(Stress)], [max(Strain), 0], color = "red")
            if(save_tf):
                plt.savefig("StressStrainPlot" + file_aug + "-" + job_number + ".png", dpi = 300, bbox_inches = "tight")
    return([slope, [mymax_x, mymax_y]])

#myreturn = StressStrainPlots(energies_csv, fail_time)

# current_path = r"C:\Users\jason\OneDrive\Documents\SDSU\Grad\AFRL-Research\Data\YNB-001\A70\Sys-lvl-rpt-0001.csv"
# IL_path = r"C:\Users\jason\OneDrive\Documents\SDSU\Grad\AFRL-Research\Data\YNB-001\A70\InputLog-0001.txt"

# temp_time = GetFailureTime(current_path, plot_tf = True, save_tf = False)
# temp_returns = StressStrainPlots(current_path, input_log = IL_path,
#                                   fail_time = temp_time, proportion_data=0.2, save_tf = False)


#%%

current_path = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008"
os.chdir(current_path)
os.listdir()
sub1 = ["A"]
myslopes_maxs = []
for i in range(len(sub1)):
    os.chdir(current_path + "/" + sub1[i])
    sub2 = os.listdir()
    for j in range(len(sub2)):
        if(sub2[j].find(".csv") > 1):
            job_number = sub2[j][(sub2[j].rfind("-"))+1:sub2[j].rfind(".")]
            temp_time = GetFailureTime(sub2[j], plot_tf = True, file_aug = sub1[i], save_tf = True)
            temp_returns = StressStrainPlots(sub2[j], input_log ="InputLog-"+job_number+".txt",
                                             fail_time = temp_time, file_aug=sub1[i],
                                             proportion_data=0.1, save_tf = True, plot_tf = True)
            myslopes_maxs.append(temp_returns)

directory_list = [r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A"]

output_location = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008"

MergeElasticProperties(directory_list = directory_list, output_location = output_location)



#%%

current_path = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001"
os.chdir(current_path)
os.listdir()
sub1 = ["A70", "B75", "C80", "D85", "E90"]
myslopes_maxs = []
for i in range(len(sub1)):
    os.chdir(current_path + "/" + sub1[i])
    sub2 = os.listdir()
    for j in range(len(sub2)):
        if(sub2[j].find(".csv") > 1):
            job_number = sub2[j][(sub2[j].rfind("-"))+1:sub2[j].rfind(".")]
            temp_time = GetFailureTime(sub2[j], plot_tf = False, file_aug = sub1[i], save_tf = False)
            temp_returns = StressStrainPlots(sub2[j], input_log ="InputLog-"+job_number+".txt",
                                             fail_time = temp_time, file_aug=sub1[i],
                                             proportion_data=0.1, save_tf = False, plot_tf = False)
            myslopes_maxs.append(temp_returns)

directory_list = [r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\A70",
                   r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\B75",
                   r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\C80",
                   r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\D85",
                   r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001\E90"]

output_location = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-001"

MergeElasticProperties(directory_list = directory_list, output_location = output_location)



#%%
current_path = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002"
os.chdir(current_path)
os.listdir()
sub1 = ["A70", "B75", "C80", "D85", "E90"]
myslopes_maxs = []
for i in range(len(sub1)):
    os.chdir(current_path + "/" + sub1[i])
    sub2 = os.listdir()
    for j in range(len(sub2)):
        if(sub2[j].find(".csv") > 1):
            job_number = sub2[j][(sub2[j].rfind("-"))+1:sub2[j].rfind(".")]
            temp_time = GetFailureTime(sub2[j], plot_tf = False, file_aug = sub1[i], save_tf = False)
            temp_returns = StressStrainPlots(sub2[j], input_log ="InputLog-"+job_number+".txt",
                                             fail_time = temp_time, file_aug=sub1[i],
                                             proportion_data=0.2, save_tf = False, plot_tf = False)
            myslopes_maxs.append(temp_returns)



directory_list = [r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002\A70",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002\B75",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002\C80",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002\D85",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002\E90"]

output_location = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-002"

MergeElasticProperties(directory_list = directory_list, output_location = output_location)



#%%
current_path = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003"
os.chdir(current_path)
os.listdir()
sub1 = ["A70", "B75", "C80", "D85", "E90"]
myslopes_maxs = []
for i in range(len(sub1)):
    os.chdir(current_path + "/" + sub1[i])
    sub2 = os.listdir()
    for j in range(len(sub2)):
        if(sub2[j].find(".csv") > 1):
            job_number = sub2[j][(sub2[j].rfind("-"))+1:sub2[j].rfind(".")]
            temp_time = GetFailureTime(sub2[j], plot_tf = True, file_aug = sub1[i], save_tf = True)
            temp_returns = StressStrainPlots(sub2[j], input_log ="InputLog-"+job_number+".txt",
                                             fail_time = temp_time, file_aug=sub1[i],
                                             proportion_data=0.2, save_tf = True, plot_tf = True)
            myslopes_maxs.append(temp_returns)



directory_list = [r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003\A70",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003\B75",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003\C80",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003\D85",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003\E90"]

output_location = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-003"

MergeElasticProperties(directory_list = directory_list, output_location = output_location)

#%%
current_path = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-009"
os.chdir(current_path)
os.listdir()
sub1 = ["first", "second"]
myslopes_maxs = []
for i in range(len(sub1)):
    os.chdir(current_path + "/" + sub1[i])
    sub2 = os.listdir()
    for j in range(len(sub2)):
        if(sub2[j].find(".csv") > 1):
            job_number = sub2[j][(sub2[j].rfind("-"))+1:sub2[j].rfind(".")]
            temp_time = GetFailureTime(sub2[j], plot_tf = True, file_aug = sub1[i], save_tf = True)
            temp_returns = StressStrainPlots(sub2[j], input_log ="InputLog-"+job_number+".txt",
                                             fail_time = temp_time, file_aug=sub1[i],
                                             proportion_data=0.2, save_tf = True, plot_tf = True)
            myslopes_maxs.append(temp_returns)

directory_list = [r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-009\first",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-009\second",
                 ]

output_location = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-009"

MergeElasticProperties(directory_list = directory_list, output_location = output_location)

#%%
current_path = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008"
os.chdir(current_path)
os.listdir()
sub1 = ["A", "B", "C", "D", "E"]
myslopes_maxs = []
for i in range(len(sub1)):
    os.chdir(current_path + "/" + sub1[i])
    sub2 = os.listdir()
    for j in range(len(sub2)):
        if(sub2[j].find(".csv") > 1):
            job_number = sub2[j][(sub2[j].rfind("-"))+1:sub2[j].rfind(".")]
            temp_time = GetFailureTime(sub2[j], plot_tf = True, file_aug = sub1[i], save_tf = True)
            temp_returns = StressStrainPlots(sub2[j], input_log ="InputLog-"+job_number+".txt",
                                             fail_time = temp_time, file_aug=sub1[i],
                                             proportion_data=0.2, save_tf = True, plot_tf = True)
            myslopes_maxs.append(temp_returns)

directory_list = [r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\A",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\B",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\C",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\D",
                  r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008\E",
                  ]

output_location = r"C:\Users\jason\Documents\Grad\AFRL Research\Data\YNB-008"

MergeElasticProperties(directory_list = directory_list, output_location = output_location)

