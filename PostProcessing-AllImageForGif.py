# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 18:24:41 2022

@author: jason
"""

from abaqus import backwardCompatibility
backwardCompatibility.setValues(reportDeprecated=False)
# ######################################################################

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()

import math
import os
import shutil



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

def GetFailureTime(energies_csv, plot_tf = None):
    job_number = energies_csv[(energies_csv.rfind("-")+1):(len(energies_csv)-4)]
    if(plot_tf is None):
        plot_tf = False
    energies = open(energies_csv, "r")
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
    
    
    temp = MyNumDeriv(x= time, y = IoT, plot_tf = plot_tf, job_number = job_number)
    indices = temp[0]
    burn_time = temp[1]
    if(indices == -999):
        FT = -999
        if(plot_tf):
            plt.figure()
            plt.rcParams["figure.figsize"] = (8,6)
            plt.plot(time, IoT, label = "Internal", color = "blue")
            plt.plot(time, KoT, label= "Kinetic", color = "red")
            plt.axvline(x = burn_time, label = "Burn-in", color = "purple")
            plt.axline([0,0], [time[len(time)-1], 1] , color = "orange", linewidth = 2)
            plt.axline([0,1], [time[len(time)-1], 0], color = "orange", linewidth = 2)
            plt.xlabel("Time")
            plt.ylabel("Energies per Total")
            plt.title("Relative Energies over Time :{}".format(str(job_number)))
            plt.legend()
    else:
        if(not len(indices) == 0):
            FT = time[indices[0]]
        else:
            FT = -1
        if(plot_tf):
            plt.figure()
            plt.rcParams["figure.figsize"] = (8,6)
            plt.plot(time, IoT, label = "Internal", color = "blue")
            plt.plot(time, KoT, label= "Kinetic", color = "red")
            plt.axvline(x = FT, label = "Failure Time", color = "green", linewidth = 0.5)
            plt.fill_between(x = [-0.05, burn_time], y1 = [1.5,1.5], y2 = [-0.5, -0.5], facecolor = "gray")
            plt.xlim(left = -0.02)
            plt.ylim(bottom = -0.05, top = 1.05)
            plt.axvline(x = burn_time, label = "Burn-in", color = "purple", linewidth = 0.5)
            plt.xlabel("Time")
            plt.ylabel("Energies per Total")
            plt.title("Relative Energies over Time :{}".format(str(job_number)))
            plt.legend()
    return(FT)

def GetImage(job_name, fail_time):
    if (job_name[job_name.find("."):len(job_name)] != ".odb"):
        file_name = job_name + ".odb"
    
    
    #need a way to get:
        #the last frame
        #Location of failure
    
    job_number = int(job_name[(job_name.find("-") + 1):len(job_name)])
    o1 = session.openOdb(name = file_name)
    
    ###
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    frame_times = []
    for frame_i in o1.steps['Step-1'].frames:
        temp = frame_i.frameValue
        frame_times.append(temp)
        
    mymin = 100
    frame_number = -999
    for i in range(len(frame_times)):
        temp = (fail_time - frame_times[i])**2
        if(temp < mymin):
            mymin= temp
            frame_number = i
    ###
    if(fail_time == -999):
        frame_number = 0
    
    
    
    
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=NONE)
    session.viewports['Viewport: 1'].enableMultipleColors()
    session.viewports['Viewport: 1'].setColor(initialColor='#BDBD')
    cmap=session.viewports['Viewport: 1'].colorMappings['Material']
    session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
    session.viewports['Viewport: 1'].disableMultipleColors()
    session.viewports['Viewport: 1'].view.fitView()
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=frame_number)
    session.printOptions.setValues(reduceColors=False)
    session.graphicsOptions.setValues(antiAlias=OFF)
    session.pngOptions.setValues(imageSize=(1920, 1080))
    session.printOptions.setValues(vpDecorations=OFF)

    
    # vps = session.viewports[session.currentViewportName]
    # session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=1001)
    # session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    # session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    #     DEFORMED, ))
    # session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    #     CONTOURS_ON_DEF, ))
    # session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    #     visibleEdges=FEATURE)
    # currentframe = vps.odbDisplay.fieldFrame[1]
    # session.viewports['Viewport: 1'].view.fitView()
    # session.viewports['Viewport: 1'].view.setValues(nearPlane=1.68774, 
    # farPlane=2.58782, width=0.595126, height=0.249484, viewOffsetX=0.000483455, 
    # viewOffsetY=0.000482296) #taken from the GUI
    # session.viewports['Viewport: 1'].view.setValues(nearPlane=1.68845, 
    # farPlane=2.58739, width=0.595376, height=0.249589, viewOffsetX=0.000483658, 
    # viewOffsetY=0.037109) #taken from the GUI
    # session.viewports['Viewport: 1'].odbDisplay.setFrame(step = 0, frame = currentframe-1)
    
    #Printing to png
    session.printToFile(fileName='Job-{:04d}-ImageofFailure'.format(job_number), format=PNG,
        canvasObjects=(session.viewports['Viewport: 1'], ))




#good_runs = list(range(18))
#good_runs.remove(9)
#for i in range(len(good_runs)):
#        good_runs.remove(i)


#fail_times = []
#for i in good_runs:
#    energies_csv = r"/p/home/jrhasse/Sys-lvl-rpt-{:04d}.csv".format(i)
#    fail_time = GetFailureTime(energies_csv)
#    fail_times.append(fail_time)

#fail_time = GetFailureTime(r"/p/home/jrhasse/Sys-lvl-rpt-0000.csv")

#which_rejected = []
#counter = 0
#for i in good_runs:
#    if(fail_times[counter] == -999):
#        which_rejected.append(i)
#    counter = counter + 1

#counter = 0
#for i in good_runs:
#    GetImage(job_name = "Job-{:04d}".format(i), fail_time = fail_times[counter])
#    counter = counter + 1
#GetImage(job_name = "Job-0000", fail_time = fail_time)


def GetImagesForGIF(job_name, folder):
    dir_name = folder + "/" + job_name + "-Images" 
    try:
        os.mkdir(dir_name)
    except OSError as error:
        print(error)

    if(job_name[job_name.find("."):len(job_name)] != ".odb"):
        file_name = job_name + ".odb"
    job_number = int(job_name[(job_name.find("-") + 1):len(job_name)])
    o1 = session.openOdb(name = folder+"/"+file_name)

    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=NONE)
    session.viewports['Viewport: 1'].enableMultipleColors()
    session.viewports['Viewport: 1'].setColor(initialColor='#BDBD')
    cmap=session.viewports['Viewport: 1'].colorMappings['Material']
    session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
    session.viewports['Viewport: 1'].disableMultipleColors()
    session.viewports['Viewport: 1'].view.fitView()
    #session.viewports['Viewport: 1'].view.setValues(nearPlane=1.68401,
    #                                               farPlane=2.58463, width=0.604639, height=0.252731)
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=0)
    session.printOptions.setValues(reduceColors=False)
    session.graphicsOptions.setValues(antiAlias=OFF)
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(DEFORMED, ))
    session.pngOptions.setValues(imageSize=(4096, 4096))
    session.printOptions.setValues(vpDecorations=OFF)
    
    for i in range(102):
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step = 0, frame = i)
        session.printToFile(fileName=dir_name + '/' + job_name+ 'Img-{:04d}'.format(i), format=PNG,
            canvasObjects=(session.viewports['Viewport: 1'], ))

# folder ="/p/home/jrhasse/NB-001/A70/ODB"
# #GetImagesForGIF(job_name = "Job-0064", folder = folder)
# #GetImagesForGIF(job_name = "Job-0077", folder = folder)
# for i in range(0,5):
#     if(os.path.isfile(folder + "/Job-{:04d}".format(i)+".odb")):
#         GetImagesForGIF(job_name = "Job-{:04d}".format(i), folder = folder)
        

#%%

def GetHigherResolutionStart(folder, sub_folder_list):
    dir_name = folder + "/Images/"
    try:
        os.mkdir(dir_name)
    except OSError as error:
        print(error)
    
    for i in range(len(sub_folder_list)):
        temp_fold = folder + "/" +sub_folder_list[i] + "/ODB/"
        os.chdir(temp_fold)
        poss_files = os.listdir(temp_fold)
        my_odb_names = []
        for j in range(len(poss_files)):
            if(poss_files[j].find(".odb") > 1):
                my_odb_names.append(poss_files[j])
        
        for j in range(len(my_odb_names)):
            job_name = my_odb_names[j]
            job_name = job_name[:job_name.find('.')]
        
            file_name = job_name + ".odb"
            job_number = int(job_name[(job_name.find("-") + 1):len(job_name)])
            o1 = session.openOdb(name = folder + "/" + sub_folder_list[i] + "/ODB/" + file_name)
    
            session.viewports['Viewport: 1'].setValues(displayedObject=o1)
            session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
                visibleEdges=NONE)
            session.viewports['Viewport: 1'].enableMultipleColors()
            session.viewports['Viewport: 1'].setColor(initialColor='#BDBD')
            cmap=session.viewports['Viewport: 1'].colorMappings['Material']
            session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
            session.viewports['Viewport: 1'].disableMultipleColors()
            session.viewports['Viewport: 1'].view.fitView()
            #session.viewports['Viewport: 1'].view.setValues(nearPlane=1.68401,
            #                                               farPlane=2.58463, width=0.604639, height=0.252731)
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=0)
            session.printOptions.setValues(reduceColors=False)
            session.graphicsOptions.setValues(antiAlias=OFF)
            session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(DEFORMED, ))
            session.pngOptions.setValues(imageSize=(4096, 4096))
            session.printOptions.setValues(vpDecorations=OFF)
        
            session.viewports['Viewport: 1'].odbDisplay.setFrame(step = 0, frame = 0)
            session.printToFile(fileName = dir_name + "/" + sub_folder_list[i] + job_name + "-HQ", format=PNG,
                                canvasObjects=(session.viewports['Viewport: 1'], ))


sub_folder_list = ["A70", "B75", "C80", "D85", "E90"]
folder = "/p/home/jrhasse/NB-001"

GetHigherResolutionStart(folder = folder, sub_folder_list = sub_folder_list)
    
        


