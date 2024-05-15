# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 15:18:38 2022

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

#%%%
my_system_vars = ["Internal energy: ALLIE for Whole Model",
               "Kinetic energy: ALLKE for Whole Model",
               "Reaction force: RF1 PI: rootAssembly Node 1 in NSET BDNRFLEFT",
               "Reaction force: RF1 PI: rootAssembly Node 2 in NSET BDNRFRIGHT",
               "Spatial displacement: U1 PI: rootAssembly Node 1 in NSET BDNRFLEFT",
               "Spatial displacement: U1 PI: rootAssembly Node 2 in NSET BDNRFRIGHT"]

def system_csvs(sys_name):
    sys_rpt = open(sys_name, "r")
    sys_lines = sys_rpt.readlines()
    #Get Header
    counter = 0
    i = -1
    indices = []
    while counter < 2:
        i = i + 1
        if(sys_lines[i] == "\n"):
            counter = counter + 1
            indices.append(i)
    sys_header = sys_lines[(indices[0]+1):indices[1]]
    
    
    header_store = []
    for i in range(len(sys_header)):
        temp = list(sys_header[i])
        for j in range(int(math.floor((len(temp)-10)/19))+1):
            index = 10 + j*19 - 1
            temp[index] = "!"
        temp = "".join(temp)
        temp = str(temp)
        temp = temp.split("!")
        header_store.append(temp)
    
    final_header = []
    for i in range(len(header_store)):
        if(i == 0):
            for j in range(len(header_store[i])):
                final_header.append(str(header_store[i][j]).strip())
        else:
            for j in range(len(header_store[i])):
                final_header[j] = final_header[j] + header_store[i][j].strip()
    final_header.remove('')
    #to remove the first empty column
    sys_header_final = ",".join(final_header) + "\n"
    sys_rpt.close()
    
    
    #Get data
    counter = 0
    starting = -1
    ending = -1
    for i in range(len(sys_lines)):
        if(sys_lines[i] == "\n"):
            counter = counter + 1 
            if(counter == 2):
                starting = i
            elif(counter == 3):
                ending = i
    if(ending  == -1):
        ending = len(sys_lines)
    sys_data = sys_lines[(starting+1):ending]
    for i in range(len(sys_data)):
        sys_data[i] = sys_data[i].strip()
        temp = sys_data[i].split()
        sys_data[i] = ",".join(temp) + "\n"
    
    sys_file = open(sys_name[0:sys_name.find(".")] + ".csv", "w")
    sys_file.write(sys_header_final)
    sys_file.writelines(sys_data)
    sys_file.close()
    sys_rpt.close()


def element_csvs(ele_name):
    #Now for element level csvs
    ele_rpt = open(ele_name, "r")
    ele_lines = ele_rpt.readlines()
    ele_rpt.close()
    
    frame_index = []
    for i in range(len(ele_lines)):
        if("Frame" in ele_lines[i]):
            frame_index.append(i)
    frame_index.append(len(ele_lines[i]))
    
    
    newdir = ele_name[0:ele_name.find(".")]
    if os.path.isdir(newdir):
        shutil.rmtree(newdir)
    os.makedirs(newdir)
    for i in range(len(frame_index)-1):
        newdir2 = "frame-" + str(i)
        os.makedirs(newdir+"/"+newdir2)
        frame_lines = ele_lines[frame_index[i]:frame_index[i+1]]
        part_index = []
        for j in range(len(frame_lines)):
            if("part:" in frame_lines[j]):
                part_index.append(j)
        part_index.append(len(frame_lines))
        for j in range(len(part_index)-1):
            part_lines = frame_lines[part_index[j]:part_index[j+1]]
            data_start = -1
            counter = 0
            while data_start < 0 and (counter < len(part_lines)-2):
                if("---------" in part_lines[counter]):
                    data_start = counter
                counter = counter + 1
            part_header = part_lines[data_start - 2].strip().split("  ")
            part_header = list(filter(None, part_header))
            part_header = ",".join(part_header) + "\n"
            #now for the data
            part_data = part_lines[(data_start + 1):len(part_lines)]
            for k in range(len(part_data)):
                part_data[k] = part_data[k].strip().split()
                part_data[k] = ",".join(part_data[k]) + "\n"
            csv_name = part_lines[data_start-4][part_lines[data_start - 4].find(":")+1:len(part_lines[data_start - 4])].strip()
            csv_name = csv_name + ".csv"
            ele_file = open(newdir+ "/"+ newdir2 + "/" + csv_name, "w")
            ele_file.write(part_header)
            ele_file.writelines(part_data)
            ele_file.close()


def ConvertODBtoCSV(job_name, system_vars = None):
    if(system_vars is None):
        system_vars = my_system_vars
    
    if (job_name[job_name.find("."):len(job_name)] != ".odb"):
        file_name = job_name + ".odb"
    
    job_number = job_name[(job_name.find("-") + 1):len(job_name)]
    o1 = session.openOdb(name = file_name)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    odb = session.odbs[file_name]
    xyData1 = []
    for i in range(len(system_vars)):
        var_name = system_vars[i]
        session.XYDataFromHistory(name = var_name, odb = odb,
                                  outputVariableName = system_vars[i], steps = ("Step-1", ),
                                  __linkedVpName__='Viewport: 1')
        xyData1.append(session.xyDataObjects[var_name])
    xyData2 = tuple(xyData1)
    session.xyReportOptions.setValues(layout = SINGLE_TABLE)
    sys_name = "Sys-lvl-rpt-" + str(job_number) + ".rpt"
    session.writeXYReport(fileName = sys_name, appendMode=OFF,
                          xyData = xyData2)
    
    #Now for the element-wise info
    session.fieldReportOptions.setValues(printTotal=OFF, printMinMax=OFF, 
                                         reportFormat=NORMAL_ANNOTATED)
    ele_name = "Ele-lvl-rpt-" + job_number + ".rpt"
    session.writeFieldReport(fileName= ele_name, append=OFF, 
                             sortItem='Element Label', odb=odb, step=0, frame=1, 
                             outputPosition=ELEMENT_CENTROID,
                             variable=(('PEEQ', INTEGRATION_POINT),
                                       ('S', INTEGRATION_POINT,
                                        ((INVARIANT, 'Mises'), 
                                        (INVARIANT, 'Max. Principal'),
                                        (INVARIANT, 'Mid. Principal'),
                                        (INVARIANT, 'Min. Principal'), )), ),
                             stepFrame=ALL)
    
    #now convert these into csv
    system_csvs(sys_name)
    element_csvs(ele_name)

#ConvertODBtoCSV(job_name="Job-392",system_vars = my_system_vars)
#%%
for i in range(40,60):
    ConvertODBtoCSV(job_name = "../ZThird40/Job-{:04d}".format(i))

#the ".." goes back one folder of the default directory.
#the "{:04d}" converts the i to four numbers padded by 0s in the front. ex 40 -> 0040
