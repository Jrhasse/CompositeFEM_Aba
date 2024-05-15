# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 12:14:18 2022
Last Modified on Tue Jan 9 2024

@author: jason
"""
#This script was made within the Spyder IDE
#%%
###################################
# Geometry Parameters input Below #
###################################
#Initial parameters that were setup to assist with debugging when building the script. 
#flake_thickness = 0.0025 #2.5 nanometers
#aspect_ratio = 75 #ratio between flake thickness and flake length
#flake_length calculated in the function
#n_flake_x = 3 # how many flakes there will be horizontally
#n_flake_y = 3 # how many flakes there will be vertically
#const_dist_flake_y = 0.0 #units = flake thicknesses, vertical seperation
#dist_flake_y = flake_thickness * const_dist_flake_y  #y distance for pattern translation
#Should only be set to 0 for now
#flake_concentration_x = 0.8 #80%
#bricklike pattern 
#n_until_shift = 1 #number of flakes until a partial slide between two rows
#Mesh sizing
#mesh_size = 0.0004

#%%

#Function used to generate the input log file in the master function
def InputLog(local_vars):
    import os
    counter = 0
    wd = os.getcwd()
    in_log_file = "InputLog-{:04d}.txt".format(counter)
    in_log_path = wd + "/" + in_log_file
    while(os.path.exists(in_log_path)):
        counter = counter + 1
        in_log_file = "InputLog-{:04d}.txt".format(counter)
        in_log_path = wd + "/" + in_log_file
    
    local_vars_names = list(local_vars)
    f = open(in_log_path, 'w')
    for i in range(len(local_vars_names)):
        value = local_vars[local_vars_names[i]]
        mystring = "{}: {}\n".format(local_vars_names[i], value) 
        f.write(mystring)
    f.close()
    print("a file called: " + in_log_path + " was created")
    return([in_log_path, counter])
#%%
###################################
# Material properties input below #
###################################
#Matrix will always be defined first
names_vec = ["Matrix_1", "Flake_1"]
density_vec = [1.9e-15, 2.0e-13]
elastic_mod_vec = [910.0, 330000.0]
elastic_pois_vec = [0.4, 0.23]

#matrix plastic properties
yield_stress = [31.53, 32.03, 33.03, 35.0, 41.0, 47.0, 53.0, 59.0, 63.0]
plastic_strain = [0, 0.013541946, 0.041168369, 0.093287009, 0.235909095, 0.359129641, 0.467418343, 0.563858637, 0.622690337]
plastic_properties_mat = []
if(len(yield_stress) == len(plastic_strain)):
   for i in range(len(yield_stress)):
       temp = [yield_stress[i], plastic_strain[i]]
       plastic_properties_mat.append(temp)
#flake plastic properties
yield_stress = [20000, 20000] # yield_stress = [20000, 22000]
plastic_strain = [0.0, 0.035] # plastic_strain = [0.0, 0.035]
plastic_properties_flake = []
if(len(yield_stress) == len(plastic_strain)):
   for i in range(len(yield_stress)):
       temp = [yield_stress[i], plastic_strain[i]]
       plastic_properties_flake.append(temp)
       
plastic_properties_df = [plastic_properties_mat, plastic_properties_flake]
del yield_stress, plastic_strain, plastic_properties_flake, plastic_properties_mat

#ductile properties (only matrix has it defined)
fracture_strain = [0.05, 0.05, 0.05, 0.05]
stress_triaxiality = [-10000, 10000, -10000, 10000]
strain_rate = [1e-10, 1e-10, 10000000000, 10000000000]
ductile_properties_df = []
for i in range(len(fracture_strain)):
    temp = [fracture_strain[i], stress_triaxiality[i], strain_rate[i]]
    ductile_properties_df.append(temp)
del fracture_strain, stress_triaxiality, strain_rate, temp
#%%
#End of input parameters
##########################################################################

# #%%
# ## IMPORTING BACKWARDS COMPATIBILITY FOR COMMAND SETBYMERGE() ##
from abaqus import backwardCompatibility
backwardCompatibility.setValues(reportDeprecated=False)
# ########################################################################

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
#%%
########################################################################################################################
# Using a Loop to get instance list values based on n_flake_x and n_flake_y values:
def GetLinPatList(n_flake_x, n_flake_y):
    import numpy as np
    out_list = []
    n_flake_x = n_flake_x + 1 
    x_seq = list(np.repeat(range(1,(n_flake_x+1)), n_flake_y))
    y_seq = list(range(1,(n_flake_y + 1))) * n_flake_x
    for i in range(len(x_seq)):
        iter_name = ('TempFlake-1-lin-{}-{}').format(x_seq[i], y_seq[i])
        out_list.append(iter_name)
    out_list[0] = "TempFlake-1"
    return(out_list)

# lin_pat_list = GetLinPatList() #Dont need any input, default values set
#%%

########################################################################################################################
# Translation sequence for random horizontal staggering of flakes
#i.e. the brick pattern
# def GetBrickShiftList(n_flake_x, n_flake_y, n_until_shift,
#                 flake_length, length_of_shift):
#     """
#     Author: Jason Hasse
    
#     Parameters
#     ----------
#     n_flake_y : int, required
#         Number of flakes in the y direction. The default is n_flake_y.
#     n_flake_x : int, required
#         Number of flakes in the x direction. The default is n_flake_x.
#     n_until_shift : int, required
#         Number of rows until we shift. i.e. n_until_shift = 3 -> 3 rows at the
#         same offset, then the 4th will be shifted. The default is n_until_shift.
#     flake_length : float, required
#         How long each flake is. The default is flake_length.
#     length_of_shift : float, required
#         How far each shift will be. Should be some fraction (or irrational < 1)
#         of the flake_length. The default is length_of_shift.
        
#     It is best to call it with no input parameters since the defaults are already placed

#     Returns 
#     -------
#     A list object containing how far each row should be shifted

#     """
#     shift_vec = [] #initialize storage
#     total_shift = 0 #to track previous shifts
#     counter = 0 #to know when to shift again
#     for i in range(n_flake_y):
#         if(counter < n_until_shift): #until we get to our n_until_shift...
#             counter = counter + 1 #keep adding 1 to our counter
#         else: #once we get to n_until_shift ...
#             counter = 1 #reset counter to 1 (for consistent steps between)
#             total_shift = total_shift + length_of_shift #and move it over
#         if(total_shift >= flake_length): #if the shift would be longer than our flake...
#             total_shift = total_shift - flake_length #make the shift smaller
#         shift_vec.append(total_shift) #add the shift to our storage vector
#     return(shift_vec)

# brick_shift_list = GetBrickShiftList()
# #%%
# #Now actually perform the shift
# for i in range(n_flake_y):
#     rowi = lin_pat_list[i::n_flake_y]
#     a.translate(instanceList = rowi, vector = ((-1 * brick_shift_list[i]), 0, 0))

# #%%
# #Use the random shifts defined in the beginning parameters to shift the parts again
# for i in range(len(random_shifts)):
#     a.translate(instanceList = [lin_pat_list[i], ], vector = (random_shifts[i],0,0))


#%%
# a = mdb.models[model_name].rootAssembly
def DeleteFlakes(model_name, lin_pat_list, a,
                 matrix_length, flake_length):

    new_lin_pat_list = lin_pat_list
    to_delete_list = []
    for i in lin_pat_list:
        pos = a.instances[i].getTranslation()
        if(pos[0] <= 0 or pos[0] >= (matrix_length - flake_length)):
            to_delete_list.append(i)
    #All parts off the matrix are identified
    for j in to_delete_list:
        del a.features[j]
        new_lin_pat_list.remove(j)
    return_list = [new_lin_pat_list, to_delete_list]
    return(return_list)
        
# temp = DeleteFlakes()
# lin_pat_list = temp[0]
# deleted_list = temp[1]
# del temp

#%%
# my_mdb = mdb.models[model_name] 

def GetExtremeFlakeCoords(flake_list, my_mdb):
    import numpy as np
    Coords = []
    for j in flake_list:
        temp = my_mdb.rootAssembly.instances[j].getTranslation()
        Coords.append(temp)
    all_y_vals = []
    for j in range(len(Coords)):
        temp = Coords[j][1] 
        all_y_vals.append(temp)
    y_vals = np.unique(all_y_vals)
    
    left_most_x = [1000000] * len(y_vals)
    right_most_x = [-1000000] * len(y_vals)
    for j in range(len(y_vals)):
        for jj in range(len(Coords)):
            if(Coords[jj][1] == y_vals[j]):
                if(Coords[jj][0] > right_most_x[j]):
                    right_most_x[j] = Coords[jj][0]
                if(Coords[jj][0] < left_most_x[j]):
                    left_most_x[j] = Coords[jj][0]
    return_list = [y_vals, left_most_x, right_most_x]
    return(return_list)
    

def CreateCutFlakes(my_mdb, deleted_list,
                    lin_pat_list, n_flake_y,
                    cut_flake_tol, flake_thickness,
                    arc_offset, cut_flakes_shifts,
                    dist_flake_x,flake_length,
                    matrix_length, matrix_height):
  
    temp = GetExtremeFlakeCoords(flake_list = lin_pat_list, my_mdb = my_mdb)
    y_vals = temp[0]
    left_most_x = temp[1]
    right_most_x = temp[2]
    print("left most")
    print(len(left_most_x))
    print(left_most_x)
    print("right most")
    print(len(right_most_x))
    print(right_most_x)
    print("n_flake_y")
    print(n_flake_y)
    
    cut_flakes_names = []
    cut_flakes_length = []
    counter = -1
    #leftside
    for i in range(n_flake_y):
        s = my_mdb.ConstrainedSketch(name="__profile__", sheetSize = 1.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        
        counter = counter + 1
        if(left_most_x[i] - (cut_flakes_shifts[counter] + 2*arc_offset[0]) >= cut_flake_tol): #we will make a cut flake here
            temp_trans = (0.0,y_vals[i],0)
            
            bottom_left_point = (0.0,0.0)
            bottom_right_point = (left_most_x[i] - (cut_flakes_shifts[counter] + 2*arc_offset[0]), 0.0)
            top_left_point = (0.0,flake_thickness)
            top_right_point = (left_most_x[i] - (cut_flakes_shifts[counter] + 2*arc_offset[0]),flake_thickness)
            if(bottom_right_point[0] > 0): #Issue with the "right" point being to the left of the left point
                s.Line(point1= bottom_left_point, point2 = top_left_point) #vertical line
                s.Line(point1= bottom_left_point, point2= bottom_right_point) #bottom line
                s.Line(point1= top_left_point, point2= top_right_point) #top line
                s.Arc3Points(point1= bottom_right_point, 
                             point2= top_right_point, #top-right point
                             point3= (bottom_right_point[0] + arc_offset[0],
                                      bottom_right_point[1] + arc_offset[1])) 
                #shifted 1/4 flake_thickness and centered between the two points in the y-axis
                part_name = 'CutFlake_'+str(counter)
                cut_flakes_names.append(part_name)
                cut_flakes_length.append(bottom_right_point[0])
                p = my_mdb.Part(name=part_name,
                                dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
                p = my_mdb.parts[part_name]
                p.BaseShell(sketch = s)
                s.unsetPrimaryObject()
                p = my_mdb.parts[part_name]
                del my_mdb.sketches['__profile__']
                p = my_mdb.parts[part_name]
                f = p.faces
                faces = f.getByBoundingBox(xMin = -flake_length, yMin = -flake_thickness,
                                           xMax = matrix_length + flake_length,
                                           yMax = matrix_height + flake_thickness)
                region = p.Set(faces = faces, name = "Flake")
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#4 ]', ), )
                p.Set(edges=edges, name='Top')
                
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
                p.Set(edges=edges, name='Bottom')
                
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#8 ]', ), )
                p.Set(edges=edges, name='Left')
    
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#2 ]', ), )
                p.Set(edges=edges, name='Right')
                
                p = my_mdb.parts[part_name]
                p.SectionAssignment(region = region, sectionName='Solid_'+ names_vec[1], offset = 0.0, 
                    offsetType = MIDDLE_SURFACE, offsetField = '', thicknessAssignment=FROM_SECTION)
                
                a = my_mdb.rootAssembly
                p = my_mdb.parts[part_name]
                a.Instance(name=part_name, part=p, dependent=ON)
                a.translate(instanceList = [part_name, ], vector = temp_trans)
            
    #rightside
    for i in range(n_flake_y):
        s = my_mdb.ConstrainedSketch(name="__profile__", sheetSize = 1.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        
        counter = counter + 1
        if((right_most_x[i] + flake_length + 2*arc_offset[0]) + cut_flakes_shifts[counter] < matrix_length - cut_flake_tol): #we will make a cut flake here
            temp_trans = (right_most_x[i] + flake_length + cut_flakes_shifts[counter] +2*arc_offset[0] , y_vals[i],0)
            
            bottom_right_point = (matrix_length - temp_trans[0], 0)
            bottom_left_point = (0.0, 0.0)
            top_right_point = (matrix_length - temp_trans[0], flake_thickness)
            top_left_point = (0.0, flake_thickness)
            
            if(bottom_right_point[0] < matrix_length):
                s.Line(point1= bottom_right_point, point2= top_right_point) #vertical line
                s.Line(point1= bottom_right_point, point2= bottom_left_point) #bottom line
                s.Line(point1= top_right_point, point2= top_left_point) #top line
                s.Arc3Points(point1=bottom_left_point, point2= top_left_point, #top left point
                         point3=(bottom_left_point[0] - arc_offset[0],
                                 bottom_left_point[1] + arc_offset[1])) 
            #shifted 1/4 flake_thickness and centered between the two point in the y
                part_name = 'CutFlake_'+str(counter)
                cut_flakes_names.append(part_name)
                cut_flakes_length.append(bottom_right_point[0] - bottom_left_point[0])            
                p = my_mdb.Part(name=part_name,
                            dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
                p = my_mdb.parts[part_name]
                p.BaseShell(sketch = s)
                s.unsetPrimaryObject()
                p = my_mdb.parts[part_name]
                del my_mdb.sketches['__profile__']
                p = my_mdb.parts[part_name]
                f = p.faces
                faces = f.getByBoundingBox(xMin = -flake_length, yMin = -flake_thickness,
                                       xMax = matrix_length + flake_length,
                                       yMax = matrix_height + flake_thickness)
                region = p.Set(faces = faces, name = "Flake")
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#4 ]', ), )
                p.Set(edges=edges, name='Top')
            
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
                p.Set(edges=edges, name='Bottom')
            
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#8 ]', ), )
                p.Set(edges=edges, name='Left')
                p = my_mdb.parts[part_name]
                e = p.edges
                edges = e.getSequenceFromMask(mask=('[#2 ]', ), )
                p.Set(edges=edges, name='Right')
            
                p = my_mdb.parts[part_name]
                p.SectionAssignment(region = region, sectionName='Solid_'+ names_vec[1], offset = 0.0, 
                    offsetType = MIDDLE_SURFACE, offsetField = '', thicknessAssignment=FROM_SECTION)
                    
            a = my_mdb.rootAssembly
            p = my_mdb.parts[part_name]
            a.Instance(name=part_name, part=p, dependent=ON)
            a.translate(instanceList = [part_name, ], vector = temp_trans)
        
    
    out_list = [cut_flakes_names, cut_flakes_length]
            
    return(out_list)#out of all for loops
#%%
# temp = CreateCutFlakes()
# cut_flakes_names = temp[0]
# cut_flakes_length = temp[1]
# del temp



#Next step, cut the matrix
#%%
# my_mdb = mdb.models[model_name] 
# cutting_list = []
# cutting_list_instances = lin_pat_list
# for i in lin_pat_list:
#     temp =  my_mdb.rootAssembly.instances[i]
#     cutting_list.append(temp)
# for i in cut_flakes_names:
#     cutting_list_instances.append(i)
#     temp =  my_mdb.rootAssembly.instances[i]
#     cutting_list.append(temp)
    
    
def CutMatrix(my_mdb, cutting_list,cutting_list_instances,
              names_vec = names_vec):
    a = my_mdb.rootAssembly
    matrix_name = names_vec[0]+"_with_holes"
    a.InstanceFromBooleanCut(name = matrix_name,
                             instanceToBeCut= a.instances['TempMatrix-1'],
                             cuttingInstances= cutting_list,
                             originalInstances= SUPPRESS)
    for i in cutting_list_instances:
        a.features[i].resume()
        
    del a.features['TempMatrix-1']
    
    return(matrix_name+"-1")
#matrix_name = CutMatrix()  

#%%
#my_mdb = mdb.models[model_name]
def GetIndependent(my_mdb, flake_list,matrix_name):
     a = my_mdb.rootAssembly
     all_instances = []
     for i in flake_list:
         all_instances.append(i)
     all_instances.append(matrix_name)
     temp_list = []
     for i in all_instances:
         temp = a.instances[i]
         temp_list.append(temp)
     mytuple = tuple(temp_list)
     a.makeIndependent(instances = mytuple)
#GetIndependent()

#%%
def MasterCreatePartitionV3(flake_list, my_mdb, cut_flakes_length,
                    cut_flakes_names, flake_length,  
                    dist_flake_y, n_flake_y, matrix_height,
                    matrix_length):
    import numpy as np
        #get the coords to pass through
    Coords = []
    for j in flake_list:
        temp = my_mdb.rootAssembly.instances[j].getTranslation()
        Coords.append(temp)
    all_y_vals = []
    for j in range(len(Coords)):
        temp = Coords[j][1] 
        all_y_vals.append(temp)
    y_vals = np.unique(all_y_vals)
        
    flake_list_lengths = []
    for i in range(len(flake_list)):
        if(flake_list[i] in cut_flakes_names):
            index = cut_flakes_names.index(flake_list[i])
            len_x_i = cut_flakes_length[index]
            flake_list_lengths.append(len_x_i)
        else:
            len_x_i = flake_length
            flake_list_lengths.append(len_x_i)
    master_counter_y = 0 #keep track of iterations across each row
    
    master_part_lines = []
    
    def AddLines(part_lines, part_instances, matrix_length,
                 my_mdb = my_mdb,
                 master_counter_y = master_counter_y,
                 master_part_lines = master_part_lines):
        a = my_mdb.rootAssembly
        for i in range(len(part_lines)):
            f1 = a.instances[part_instances[i]].faces
            t = a.MakeSketchTransform(sketchPlane = f1[0],sketchPlaneSide = SIDE1,
                            origin = (0.0, 0.0, 0.0))
            s = my_mdb.ConstrainedSketch(name="__profile__",sheetSize=1.0, transform = t)
            g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
            s.sketchOptions.setValues(decimalPlaces=6)
            s.setPrimaryObject(option = SUPERIMPOSE)
            a.projectReferencesOntoSketch(sketch = s, filter = COPLANAR_EDGES)
            p1 = (part_lines[i][0],part_lines[i][1])
            p2 = (part_lines[i][2],part_lines[i][3])
            if((p1,p2) not in master_part_lines):
                master_part_lines.append((p1,p2))
                if(p1[0] > 0 and p1[0] < matrix_length - 0.00001): #probably wont always work???
                    s.Line(point1 = p1, point2 = p2)
                    my_mask = f1.getMask()
                    picked_faces = f1.getSequenceFromMask(mask = my_mask)
                    a.PartitionFaceBySketch(faces = picked_faces, sketch = s)
                    s.unsetPrimaryObject()
            del my_mdb.sketches['__profile__']
        return(master_part_lines)
    
    def BotPart(matrix_length, flake_list = flake_list, flake_list_lengths = flake_list_lengths,
                Coords = Coords, y_vals = y_vals, flake_thickness = flake_thickness,
                master_counter_y = master_counter_y, master_part_lines = master_part_lines):
        bottom_flakes = []
        x_coords_above = []
        part_lines = []
        part_instances = []
        for i in range(len(Coords)):
            if(Coords[i][1] == y_vals[master_counter_y]):
                bottom_flakes.append(flake_list[i])
            if(Coords[i][1] == y_vals[master_counter_y + 1]):
                temp = Coords[i][0]
                temp2 =  Coords[i][0] + flake_list_lengths[i]
                x_coords_above.append(temp)
                x_coords_above.append(temp2)
        
        #now
        for i in range(len(bottom_flakes)):
            flake_index = flake_list.index(bottom_flakes[i])
            x_i = (Coords[flake_index][0], Coords[flake_index][0]+flake_list_lengths[flake_index])
            for j in range(len(x_coords_above)):
                check1 = (x_i[0] < x_coords_above[j]) and (x_coords_above[j] < x_i[1])
                if(check1):
                    new_part_line = (x_coords_above[j], y_vals[master_counter_y],
                                     x_coords_above[j], y_vals[master_counter_y]+flake_thickness)
                    part_lines.append(new_part_line)
                    part_instances.append(bottom_flakes[i])
        master_part_lines = AddLines(part_lines, part_instances, matrix_length)
        newcounter = master_counter_y + 1
        return_list = [master_part_lines, newcounter]
        return(return_list)
    
    
    def TopPart(matrix_length, flake_list = flake_list, flake_list_lengths = flake_list_lengths,
                Coords = Coords, y_vals = y_vals, flake_thickness = flake_thickness,
                master_counter_y = master_counter_y, master_part_lines = master_part_lines):
        top_flakes = []
        x_coords_below = []
        part_lines = []
        part_instances = []
        for i in range(len(Coords)):
            if(Coords[i][1] == y_vals[master_counter_y]):
                top_flakes.append(flake_list[i])
            if(Coords[i][1] == y_vals[master_counter_y - 1]):
                temp = Coords[i][0]
                temp2 =  Coords[i][0] + flake_list_lengths[i]
                x_coords_below.append(temp)
                x_coords_below.append(temp2)
                
        for i in range(len(top_flakes)):
            flake_index = flake_list.index(top_flakes[i])
            x_i = (Coords[flake_index][0], Coords[flake_index][0]+flake_list_lengths[flake_index])
            for j in range(len(x_coords_below)):
                check1 = (x_i[0] < x_coords_below[j]) and (x_coords_below[j] < x_i[1])
                if(check1):
                    new_part_line = (x_coords_below[j], y_vals[master_counter_y],
                                     x_coords_below[j], y_vals[master_counter_y]+flake_thickness)
                    part_lines.append(new_part_line)
                    part_instances.append(top_flakes[i])
        master_part_lines = AddLines(part_lines, part_instances, matrix_length)
        return(master_part_lines)
        

    def MidPart(matrix_length, flake_list = flake_list, flake_list_lengths = flake_list_lengths,
                Coords = Coords, y_vals = y_vals, flake_thickness = flake_thickness,
                master_counter_y = master_counter_y, n_flake_y = n_flake_y,
                master_part_lines = master_part_lines):
        newcounter = master_counter_y
        for i in range(1, n_flake_y-1):
            master_part_lines = TopPart(matrix_length, master_counter_y = newcounter)
            temp = BotPart(matrix_length, master_counter_y = newcounter)
            master_part_lines = temp[0]
            newcounter = temp[1]
        return_list = [master_part_lines, newcounter]
        return(return_list)
        
        
    if(n_flake_y == 2):
        temp = BotPart(matrix_length)
        master_part_lines = temp[0]
        newcounter = temp[1]
        output = TopPart(matrix_length, master_counter_y = newcounter)
    else:
        temp = BotPart(matrix_length)
        master_part_lines = temp[0]
        newcounter = temp[1]
        temp2 = MidPart(matrix_length, master_counter_y = newcounter)
        master_part_list = temp2[0]
        newcounter2 = temp2[1]
        output = TopPart(matrix_length, master_counter_y = newcounter2)
    return(output)
#line_coords = MasterCreatePartitionV3()

#%%
#my_mdb = mdb.models[model_name]
def CreateMesh(my_mdb, cutting_list_instances, matrix_name,
               matrix_length, mesh_size, matrix_height):
    #for all flakes
    elem_type1 = mesh.ElemType(elemCode = CPE4R, elemLibrary = EXPLICIT,
                               secondOrderAccuracy=OFF, hourglassControl=DEFAULT,
                               distortionControl=DEFAULT)
    elem_type2 = mesh.ElemType(elemCode = CPE3, elemLibrary = EXPLICIT)
    for i in range(len(cutting_list_instances)):
        a = my_mdb.rootAssembly
        instance_i = (a.instances[cutting_list_instances[i]], )
        a.seedPartInstance(regions = instance_i, size = mesh_size, deviationFactor = 0.1,
                           minSizeFactor = 0.1)
        f1 = a.instances[cutting_list_instances[i]].faces
        pickedRegions = f1.getByBoundingBox(xMin=-matrix_length, yMin=-matrix_height,
                                            xMax=2.0*matrix_length, yMax=2.0*matrix_height)
        a.setMeshControls(regions=pickedRegions, elemShape=QUAD)
        a.setElementType(regions = (pickedRegions, ), elemTypes = (elem_type1, elem_type2))
        a.generateMesh(regions = instance_i)
    
    #Now for the Matrix itself
    a = my_mdb.rootAssembly
    instance_i = (a.instances[matrix_name],)
    a.seedPartInstance(regions = instance_i, size = mesh_size, deviationFactor = 0.1,
                        minSizeFactor = 0.1)
    f1 = a.instances[matrix_name].faces
    pickedRegions = f1.getByBoundingBox(xMin=-matrix_length, yMin=-matrix_height,
                                        xMax=2.0*matrix_length, yMax=2.0*matrix_height)
    a.setMeshControls(regions=pickedRegions, elemShape=QUAD)
    a.setElementType(regions = (pickedRegions, ), elemTypes = (elem_type1, elem_type2))
    a.generateMesh(regions = instance_i)

#CreateMesh()


#%%

def DefineBoundaryConditions(my_mdb, matrix_length, matrix_height,
                             flake_list, matrix_name,
                             cut_flakes_length, cut_flakes_names,
                             flake_length, desired_max_strain,
                             n_moving_ends, time_units,
                             datum_shift, mesh_size, n_tp = None):
    if(n_tp is None):
        n_tp = 101
    import numpy as np
        #get the coords to pass through
    Coords = []
    for j in flake_list:
        temp = my_mdb.rootAssembly.instances[j].getTranslation()
        Coords.append(temp)
    all_y_vals = []
    for j in range(len(Coords)):
        temp = Coords[j][1] 
        all_y_vals.append(temp)
    y_vals = np.unique(all_y_vals)
    
    flake_list_lengths = []
    for i in range(len(flake_list)):
        if(flake_list[i] in cut_flakes_names):
            index = cut_flakes_names.index(flake_list[i])
            len_x_i = cut_flakes_length[index]
            flake_list_lengths.append(len_x_i)
        else:
            len_x_i = flake_length
            flake_list_lengths.append(len_x_i)
    
    
    a = my_mdb.rootAssembly
    p1 = a.DatumPointByCoordinate(coords = (-datum_shift, matrix_height/2, 0.0))
    p2 = a.DatumPointByCoordinate(coords = ((matrix_length + datum_shift), matrix_height/2, 0.0))
    r1 = a.ReferencePoint(point = a.datums[p1.id])
    r2 = a.ReferencePoint(point = a.datums[p2.id])
    
    a.Set(referencePoints = (a.referencePoints[r1.id],), name = "BdnRFLeft")
    a.Set(referencePoints = (a.referencePoints[r2.id],), name = "BdnRFRight")
    
    #get left assembly nodes
    nl = a.instances[matrix_name].nodes.getByBoundingBox(xMin = -mesh_size/2,
                                                    yMin = -datum_shift,
                                                    xMax = mesh_size/2,
                                                    yMax = matrix_height + datum_shift)
    
    for i in range(len(flake_list)):
        if(Coords[i][0] == 0):
            n_temp = a.instances[flake_list[i]].nodes
            nodes_temp = n_temp.getByBoundingBox(xMin = -mesh_size/2,
                                                 yMin = -datum_shift,
                                                 xMax = mesh_size/2,
                                                 yMax = matrix_height + datum_shift)
            nl = nl + nodes_temp
    a.Set(nodes = nl, name = "BdnNLeft")
    
    
    
    nr = a.instances[matrix_name].nodes.getByBoundingBox(xMin = matrix_length - mesh_size/2,
                                         yMin = -datum_shift,
                                         xMax = matrix_length + mesh_size/2,
                                         yMax = matrix_height + datum_shift)
    for i in range(len(flake_list)):
        if(Coords[i][0] + flake_list_lengths[i] > matrix_length - datum_shift):
            n_temp = a.instances[flake_list[i]].nodes
            nodes_temp = n_temp.getByBoundingBox(xMin = matrix_length - mesh_size/2,
                                                 yMin = -datum_shift,
                                                 xMax = matrix_length + mesh_size/2,
                                                 yMax = matrix_height + datum_shift)
            nr = nr + nodes_temp
    a.Set(nodes = nr, name = "BdnNRight")
    
    my_mdb.Equation(name = "Eq-Left", terms = ((1.0, "BdnNLeft", 1), (-1.0, "BdnRFLeft",1)))
    my_mdb.Equation(name = "Eq-Right", terms = ((1.0, "BdnNRight", 1), (-1.0, "BdnRFRight",1)))
    cons_vel = (0.5555555)*matrix_length*desired_max_strain*(2/n_moving_ends)
    
    my_mdb.SmoothStepAmplitude(name = "Amp-Smooth1",
                timeSpan = STEP, data = ((0.0,0.0), (0.2, cons_vel), (1, cons_vel)))
    
    my_mdb.ExplicitDynamicsStep(name = "Step-1", previous = "Initial",
                massScaling = ((SEMI_AUTOMATIC, MODEL, AT_BEGINNING, 0.0, time_units,
                                UNIFORM, 0, 0, 0.0, 0.0, 0, None), ),
                improvedDtMethod = ON)
    
    regionl = a.sets["BdnRFLeft"]
    my_mdb.VelocityBC(name = "BC-LeftVel", createStepName = "Step-1", region = regionl, 
                      v1 = -1.0, v2 = UNSET, vr3 = UNSET, amplitude="Amp-Smooth1",
                      localCsys = None, distributionType = UNIFORM, fieldName='')
    regionr = a.sets["BdnRFRight"]
    my_mdb.VelocityBC(name = "BC-RightVel", createStepName = "Step-1", region = regionr, 
                      v1 = 1.0, v2 = UNSET, vr3 = UNSET, amplitude="Amp-Smooth1",
                      localCsys = None, distributionType = UNIFORM, fieldName='')
    
    #ONLY USE THE BELOW FUNCTION IF THE VelocityBC IS USING THE SMOOTHSTEPAMPLITUDE
    def GetEqualStrainTPs_SmoothStep(cons_vel, end_time = None, n_tp = n_tp , t1 = None,
                                    desired_max_strain = desired_max_strain,
                                    matrix_length = matrix_length,
                                    n_moving_ends = n_moving_ends):
        if(t1 is None):
            t1 = 0.2
        if(end_time is None):
            end_time = 1.0
        from scipy.optimize import fsolve
        myseq = []
        for i in range(n_tp + 1):
            temp = end_time * (float(i)/float(n_tp + 1))
            myseq.append(round(temp, 8))
        myseq.append(end_time)
        
        f = lambda t: float(t <= t1)*((n_moving_ends/matrix_length)*cons_vel*((2.5 * t**4)/t1**3 - (3.0 * t**5)/t1**4 + t**6/t1**5) - (t_i/end_time) * desired_max_strain) + \
            float(t > t1)*((n_moving_ends/matrix_length)*cons_vel*(t - 0.5*t1) - (t_i/end_time) * desired_max_strain)
        time_points = []
        for t_i in myseq:
            root = fsolve(f,0.5)
            temp_tp = round(float(root), 6)
            time_points.append(temp_tp)
        
        #temp for debugging
        
        
        #now to change the structure of the list to match what abaqus is expecting
        return_list = []
        for t_i in time_points:
            temp = tuple([t_i,])
            #print(temp)
            return_list.append(temp)
        return_tuple = tuple(return_list)
        
        return(return_tuple)
        
    my_timepoints = GetEqualStrainTPs_SmoothStep(cons_vel = cons_vel, end_time = 2.0)
    print(my_timepoints)
    
    my_mdb.TimePoint(name = "TimePoints-1", points = my_timepoints)

    # my_mdb.TimePoint(name='TimePoints-1', points=((0.0, ), (
    #     0.0846, ), (0.1046, ), (0.1194, ), (0.1318, ), (0.1428, ), (0.153, ), (
    #     0.1626, ), (0.172, ), (0.181, ), (0.19, ), (0.199, ), (0.2, ), (0.2088, ), 
    #     (0.2176, ), (0.2264, ), (0.2352, ), (0.2448, ), (0.2536, ), (0.2624, ), (
    #     0.2712, ), (0.2808, ), (0.2896, ), (0.2984, ), (0.3072, ), (0.3168, ), (
    #     0.3256, ), (0.3344, ), (0.3432, ), (0.3528, ), (0.3616, ), (0.3704, ), (
    #     0.3792, ), (0.3888, ), (0.3976, ), (0.4064, ), (0.4152, ), (0.4248, ), (
    #     0.4336, ), (0.4424, ), (0.4512, ), (0.4608, ), (0.4696, ), (0.4784, ), (
    #     0.4872, ), (0.4968, ), (0.5056, ), (0.5144, ), (0.5232, ), (0.5328, ), (
    #     0.5416, ), (0.5504, ), (0.5592, ), (0.5688, ), (0.5776, ), (0.5864, ), (
    #     0.5952, ), (0.6048, ), (0.6136, ), (0.6224, ), (0.6312, ), (0.6408, ), (
    #     0.6496, ), (0.6584, ), (0.6672, ), (0.6768, ), (0.6856, ), (0.6944, ), (
    #     0.7032, ), (0.7128, ), (0.7216, ), (0.7304, ), (0.7392, ), (0.748, ), (
    #     0.7576, ), (0.7664, ), (0.7752, ), (0.784, ), (0.7936, ), (0.8024, ), (
    #     0.8112, ), (0.82, ), (0.8296, ), (0.8384, ), (0.8472, ), (0.856, ), (
    #     0.8656, ), (0.8744, ), (0.8832, ), (0.892, ), (0.9016, ), (0.9104, ), (
    #     0.9192, ), (0.928, ), (0.9376, ), (0.9464, ), (0.9552, ), (0.964, ), (
    #     0.9736, ), (0.9824, ), (0.9912, ), (1.0, )))
    
    my_mdb.fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'SVAVG', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A', 
        'RF', 'CSTRESS', 'CFORCE', 'EVF', 'COORD'), timePoint='TimePoints-1')
    
    my_mdb.historyOutputRequests['H-Output-1'].setValues(numIntervals=2000)
    
    regionDef = a.sets["BdnRFLeft"]
    my_mdb.HistoryOutputRequest(name='H-Output-2', 
        createStepName='Step-1', variables=('U1', 'RF1'), numIntervals=2000,
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    
    regionDef = a.sets['BdnRFRight']
    my_mdb.HistoryOutputRequest(name='H-Output-3', 
        createStepName='Step-1', variables=('U1', 'RF1'), numIntervals=2000, 
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)





#%%
#Define the interaction terms
#my_mdb = mdb.models[model_name]

def DefineIntProps(my_mdb, cohesive_table, damage_init_table,
                   damage_evolution_table, tangential_table):
    my_mdb.ContactProperty('IntProp-1')
    my_mdb.interactionProperties['IntProp-1'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0,
        table= tangential_table, shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    my_mdb.interactionProperties['IntProp-1'].CohesiveBehavior(
        defaultPenalties=OFF, table= cohesive_table)
    my_mdb.interactionProperties['IntProp-1'].Damage(
        initTable= damage_init_table,
        useEvolution=ON,
        evolutionType=ENERGY,
        evolTable= damage_evolution_table)
    #: The interaction property "IntProp-1" has been created.
    my_mdb.ContactProperty('IntProp-1-NoC')
    my_mdb.interactionProperties['IntProp-1-NoC'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0,
        table=tangential_table, shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    my_mdb.interactionProperties['IntProp-1-NoC'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)
    #: The interaction property "IntProp-1-NoC" has been created.
    ###########
    # my_mdb.ContactProperty('IntProp-1')
    # my_mdb.interactionProperties['IntProp-1'].CohesiveBehavior(
    #     defaultPenalties = OFF, table = cohesive_table)
    # my_mdb.interactionProperties["IntProp-1"].NormalBehavior(
    #     pressureOverclosure = HARD, allowSeparation = ON,
    #     constraintEnforcementMethod=DEFAULT)
    # my_mdb.interactionProperties['IntProp-1'].TangentialBehavior(
    #     formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
    #     pressureDependency=OFF, temperatureDependency=OFF, dependencies=0,
    #     table=tangential_table, shearStressLimit=None, maximumElasticSlip=FRACTION, 
    #     fraction=0.005, elasticSlipStiffness=None)
    # my_mdb.ContactProperty('IntProp-1-NoC')
    # my_mdb.interactionProperties["IntProp-1"].NormalBehavior(
    #     pressureOverclosure = HARD, allowSeparation = ON,
    #     constraintEnforcementMethod=DEFAULT)
    # my_mdb.interactionProperties['IntProp-1'].TangentialBehavior(
    #     formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
    #     pressureDependency=OFF, temperatureDependency=OFF, dependencies=0,
    #     table=tangential_table, shearStressLimit=None, maximumElasticSlip=FRACTION, 
    #     fraction=0.005, elasticSlipStiffness=None)
    

#DefineIntProps()



















#%%
#my_mdb = mdb.models[model_name]
def DefineInteractions(my_mdb, flake_list, matrix_name, cut_flakes_names, cut_flakes_length, 
                       matrix_length, flake_thickness, n_flake_y, flake_length,
                       initial_displacement, matrix_height, arc_offset, input_file_counter):
    
    xtol = 0.0001
    ytol = 0.0001
    import numpy as np
        #get the coords to pass through
    Coords = []
    for j in flake_list:
        temp = my_mdb.rootAssembly.instances[j].getTranslation()
        Coords.append(temp)
    all_y_vals = []
    for j in range(len(Coords)):
        temp = Coords[j][1] 
        all_y_vals.append(temp)
    y_vals = np.unique(all_y_vals)
        
    flake_list_lengths = []
    for i in range(len(flake_list)):
        if(flake_list[i] in cut_flakes_names):
            index = cut_flakes_names.index(flake_list[i])
            len_x_i = cut_flakes_length[index]
            flake_list_lengths.append(len_x_i)
        else:
            len_x_i = flake_length
            flake_list_lengths.append(len_x_i)

    
    name_counter = 0
    master_counter_y = 0
    
    
    
    #Helper Functions
    def IntersectIntervals(bf, af):
        left = max(bf[1], af[1])
        right = min(bf[2], af[2])
        if left >= right:
            flag = 0
        else:
            flag = 1
        flakes_used = [bf[0], af[0]]
        return_list = [flag, flakes_used, left, right]
        return(return_list)
    
    def UnionOverlap(intervals):
        intervals = sorted(intervals)
        return_list = []
        for i in range(len(intervals)-1):
            if(intervals[i][1] >= intervals[i+1][0]):
                new_entry = [intervals[i][0], intervals[i][1]]
            else:
                new_entry = intervals[i]
            return_list.append(new_entry)
        return(return_list)
    
    def CompSectIintervalsV2(intervals_rowi):
        #given a list of intervals, return the complement of their union
        left_max = None
        right_max = None
        for i in range(len(intervals_rowi)):
            if(intervals_rowi[i][0] == 0.0):
                left_max = intervals_rowi[i][1]
            if(intervals_rowi[i][1] == matrix_length):
                right_max = intervals_rowi[i][0]
        #Checking if any of the F-F surfaces go to endpoints of the Assembly
        
        if(left_max is None):
            left_max = 0
        if(right_max is None):
            right_max = matrix_length
        #if the max isnt set, set it to 0 or assembly length
        
        Max_interval = [left_max, right_max]
        storage_compl = []
        cutting_intervals = sorted(intervals_rowi)
        for i in range(len(cutting_intervals)):
            if(cutting_intervals[i][0] > xtol):
                new_entry = [Max_interval[0], cutting_intervals[i][0]]
                Max_interval = [cutting_intervals[i][1], Max_interval[1]]
                storage_compl.append(new_entry)
        if(storage_compl[len(storage_compl)-1][1] < right_max-xtol):
            #new_entry = [cutting_intervals[len(cutting_intervals)-1][1], right_max]
            new_entry = Max_interval
            if(abs(new_entry[1] - new_entry[0]) > xtol):
                storage_compl.append(new_entry)
        return(storage_compl)
    
            
    def BetweenFlakeContact(master_counter_y = master_counter_y, Coords = Coords,
                     flake_list = flake_list, flake_list_lengths = flake_list_lengths,
                     y_vals = y_vals):
        bottom_flakes = [] #[0] names,[1] startingx, [2] endingx
        above_flakes = [] #[0] names, [1] startingx, [2] endingx
        for i in range(len(Coords)):
            if(Coords[i][1] == y_vals[master_counter_y]):
                temp = [flake_list[i], Coords[i][0], Coords[i][0] + flake_list_lengths[i]]
                bottom_flakes.append(temp)
            if(Coords[i][1] == y_vals[master_counter_y + 1]):
                temp = [flake_list[i], Coords[i][0], Coords[i][0] + flake_list_lengths[i]]
                above_flakes.append(temp)
        contact_list = []
        for i in range(len(bottom_flakes)):
            for j in range(len(above_flakes)):
                temp = IntersectIntervals(bottom_flakes[i],above_flakes[j])
                contact_list.append(temp)
        return(contact_list)
        
    
    first_list = []
    first_list_names = []
    second_list = []
    second_list_names = []
    
    overlaps_found = []
    #[]first refers to the row
    #[i][j] refers to row i intersection j
    
    def IterateFlakeInteraction(name_counter, my_mdb = my_mdb, master_counter_y = master_counter_y,
                                n_flake_y = n_flake_y, y_vals = y_vals):
        for i in range(n_flake_y - 1):
            contact_list = BetweenFlakeContact(master_counter_y= master_counter_y)
            overlap_rowi = []
            for j in range(len(contact_list)):
                if(contact_list[j][0]): #if the interval makes sense...
                    bottom_flake = contact_list[j][1][0]
                    above_flake = contact_list[j][1][1]
                    master_name = "FF-IntSurf-" + str(name_counter) + "-" + bottom_flake
                    follower_name = "FF-IntSurf-" + str(name_counter) + "-" + above_flake
                    
                    #used for other functions
                    first_list_names.append(bottom_flake)
                    second_list_names.append(above_flake)
                    overlap_rowi.append([contact_list[j][2], contact_list[j][3]])
                    
                    myxMin = contact_list[j][2]-xtol
                    myyMin = y_vals[master_counter_y] + flake_thickness - ytol
                    myxMax = contact_list[j][3]+xtol
                    myyMax = y_vals[master_counter_y] + flake_thickness+ ytol
                    
                    a = my_mdb.rootAssembly
                    s1 = a.instances[bottom_flake].edges
                    side1Edges1 = s1.getByBoundingBox(xMin = myxMin,
                                                      yMin = myyMin,
                                                      xMax = myxMax,
                                                      yMax = myyMax)
                    #This method isnt going to be 100% effective, could pick up more than we intend
                    #should look at the next closest partition and ensure it also isnt in this bound
                    #but that is also slower...
                    region1 = a.Surface(side1Edges = side1Edges1, name = master_name)
                    first_list.append(region1)
                    
                    s2 = a.instances[above_flake].edges
                    side1Edges2 = s2.getByBoundingBox(xMin = myxMin,
                                                      yMin = myyMin,
                                                      xMax = myxMax,
                                                      yMax = myyMax)
                    region2 = a.Surface(side1Edges = side1Edges2, name = follower_name)
                    second_list.append(region2)
                    #Adding in Nodesets for PostProcessing stuff later
                    nodes1 = a.instances[bottom_flake].nodes.getByBoundingBox(xMin = myxMin,
                                                                              yMin = myyMin,
                                                                              xMax = myxMax,
                                                                              yMax = myyMax)
                    a.Set(nodes = nodes1, name = master_name)
                    nodes2 = a.instances[above_flake].nodes.getByBoundingBox(xMin = myxMin,
                                                                              yMin = myyMin,
                                                                              xMax = myxMax,
                                                                              yMax = myyMax)
                    a.Set(nodes = nodes2, name = follower_name)

                    
                    
                    
                    name_counter = name_counter + 1
            overlaps_found.append(overlap_rowi)
            master_counter_y = master_counter_y + 1
            
        return(name_counter)
    
    name_counter = IterateFlakeInteraction(name_counter)
    
    def WriteFFOverlapTXT():            
        wd = os.getcwd()
        ff_overlap_file = "FlakeFlakeOverlap-{:04d}.txt".format(input_file_counter)
        ff_overlap_path = wd + "/" + ff_overlap_file
        f = open(ff_overlap_path, 'w')
        lengthofoverlaps = []
        for i in range(len(overlaps_found)):
            for j in range(len(overlaps_found[i])):
                pair = overlaps_found[i][j]
                templength = pair[1] - pair[0]
                lengthofoverlaps.append(templength)
        mystring = str(lengthofoverlaps)
        mystring2 = mystring[1:len(mystring)-1]
        mystring2 = mystring2.replace(", ", "\n")
        f.write(mystring2)
        f.close()
        
    WriteFFOverlapTXT()

    def FlakeMatrixOverlapTXT(kept):
        #create file or open if it already exists
        #get the distance of each of the flake matrix interactions 
        #arrange the text to work in the usual csv format
        wd = os.getcwd()
        fm_overlap_file = 'FlakeMatrixOverlap-{:04d}.txt'.format(input_file_counter)
        fm_overlap_path = wd + "/" + fm_overlap_file
        f = open(fm_overlap_path, "a+")
        lengthofoverlaps = []
        for i in range(len(kept)):
            pair = kept[i]
            templength = pair[2] - pair[1]
            lengthofoverlaps.append(templength)
        mystring = str(lengthofoverlaps)
        mystring2 = mystring[1:len(mystring)-1]
        mystring2 = mystring2.replace(", ", "\n")
        f.write(mystring2)
        f.write("\n")
        f.close()
        
        
    
    def IterateFMContact(name_counter):
        #for each row between flakes
        for i in range(n_flake_y - 1):
            #get the complement of overlap, #already done in another function
            #find which flake those complements go to 
                #will have to search above and below the line between rows
            #then create the surfaces
            run_counter = 0
            FM_ints = CompSectIintervalsV2(overlaps_found[i])
            # print("run {}".format(i))
            # print(FM_ints)
            # print(overlaps_found[i])
            # print(y_vals[i+1])
            poss_flakes = []
            poss_xint = []
            for j in range(len(flake_list)):
                if(Coords[j][1] == y_vals[i]):
                    poss_flakes.append(flake_list[j])
                    poss_xint.append([Coords[j][0], Coords[j][0] + flake_list_lengths[j]])
                if(Coords[j][1] == y_vals[i+1]):
                    poss_flakes.append(flake_list[j])
                    poss_xint.append([Coords[j][0], Coords[j][0] + flake_list_lengths[j]])
            
            defined_FM_int = []
            for j in range(len(poss_xint)):
                for k in range(len(FM_ints)):
                    left = max(poss_xint[j][0], FM_ints[k][0])
                    right = min(poss_xint[j][1], FM_ints[k][1])
                    if left >= right:
                        flag = 0
                    else:
                        flag = 1
                    temp = [flag, left, right]
                    defined_FM_int.append(temp)
            
            kept_defined_FM_int = []
            for j in range(len(defined_FM_int)):
                if(defined_FM_int[j][0]):
                    kept_defined_FM_int.append(defined_FM_int[j])
            
            
            defined_flake_names= []
            for j in range(len(kept_defined_FM_int)):
                for k in range(len(poss_flakes)):
                    if(poss_xint[k][0] <= kept_defined_FM_int[j][1] and kept_defined_FM_int[j][2] <= poss_xint[k][1]):
                        defined_flake_names.append(poss_flakes[k])
            
            for j in range(len(kept_defined_FM_int)):
                master_name = "FMC-IntSurf-" + str(name_counter) + "-" + matrix_name + "-run-" + str(run_counter)
                follower_name = "FMC-IntSurf-" + str(name_counter) + "-" + defined_flake_names[j] + "-run-" + str(run_counter)
                first_list_names.append(matrix_name)
                second_list_names.append(defined_flake_names[j])
                
                myxMin = kept_defined_FM_int[j][1] - xtol
                myyMin = y_vals[i+1] - ytol
                myxMax = kept_defined_FM_int[j][2] + xtol
                myyMax = y_vals[i+1] + ytol
                
                a = my_mdb.rootAssembly
                s1 = a.instances[matrix_name].edges
                side1Edges1 = s1.getByBoundingBox(xMin = myxMin,
                                                  yMin = myyMin,
                                                  xMax = myxMax,
                                                  yMax = myyMax)
                region1 = a.Surface(side1Edges = side1Edges1, name = master_name)
                first_list.append(region1)
                
                s2 = a.instances[defined_flake_names[j]].edges
                side1Edges2 = s2.getByBoundingBox(xMin = myxMin,
                                                  yMin = myyMin,
                                                  xMax = myxMax,
                                                  yMax = myyMax)
                region2 = a.Surface(side1Edges = side1Edges2, name = follower_name)
                second_list.append(region2)
                
                #Adding in Nodesets for PostProcessing stuff later
                nodes1 = a.instances[matrix_name].nodes.getByBoundingBox(xMin = myxMin,
                                                                          yMin = myyMin,
                                                                          xMax = myxMax,
                                                                          yMax = myyMax)
                a.Set(nodes = nodes1, name = master_name)
                nodes2 = a.instances[defined_flake_names[j]].nodes.getByBoundingBox(xMin = myxMin,
                                                                          yMin = myyMin,
                                                                          xMax = myxMax,
                                                                          yMax = myyMax)
                a.Set(nodes = nodes2, name = follower_name)
                
                name_counter = name_counter + 1
                run_counter = run_counter + 1
                
            FlakeMatrixOverlapTXT(kept = kept_defined_FM_int)
            #Creates the text file with the flake matrix overlap info
                
        return(name_counter)
    
    name_counter = IterateFMContact(name_counter)
    
    
    def TBMatrixContact(name_counter, my_mdb = my_mdb, master_counter_y = master_counter_y,
                                n_flake_y = n_flake_y, y_vals = y_vals,
                                matrix_name = matrix_name, Coords = Coords,
                                flake_list_lengths = flake_list_lengths):
        last_index = len(y_vals)-1
        bottom_flakes = []
        top_flakes = []
        for i in range(len(Coords)):
            if(Coords[i][1] == y_vals[0]):
                temp = [flake_list[i], Coords[i][0], Coords[i][0] + flake_list_lengths[i]]
                bottom_flakes.append(temp)
            if(Coords[i][1] == y_vals[last_index]):
                temp = [flake_list[i], Coords[i][0], Coords[i][0] + flake_list_lengths[i]]
                top_flakes.append(temp)
        
        for i in range(len(bottom_flakes)):
            flake = bottom_flakes[i][0]
            master_name = "TBM1-IntSurf-" +str(name_counter) + "-" + matrix_name
            follower_name = "TBM1-IntSurf-" +str(name_counter) + "-" + flake
            
            first_list_names.append(matrix_name)
            second_list_names.append(flake)
            
            myxMin = bottom_flakes[i][1] - xtol
            myyMin = y_vals[0] - ytol
            myxMax = bottom_flakes[i][2] + xtol
            myyMax = y_vals[0] + ytol
            
            a = my_mdb.rootAssembly
            s1 = a.instances[matrix_name].edges
            side1Edges1 = s1.getByBoundingBox(xMin = myxMin,
                                              yMin = myyMin,
                                              xMax = myxMax,
                                              yMax = myyMax)
            region1 = a.Surface(side1Edges = side1Edges1, name = master_name)
            first_list.append(region1)
                    
            s2 = a.instances[flake].edges
            side1Edges2 = s2.getByBoundingBox(xMin = myxMin,
                                              yMin = myyMin,
                                              xMax = myxMax,
                                              yMax = myyMax)
            region2 = a.Surface(side1Edges = side1Edges2, name = follower_name)
            second_list.append(region2)
            
            #Adding in Nodesets for PostProcessing stuff later
            nodes1 = a.instances[matrix_name].nodes.getByBoundingBox(xMin = myxMin,
                                                                     yMin = myyMin,
                                                                     xMax = myxMax,
                                                                     yMax = myyMax)
            a.Set(nodes = nodes1, name = master_name)
            nodes2 = a.instances[flake].nodes.getByBoundingBox(xMin = myxMin,
                                                               yMin = myyMin,
                                                               xMax = myxMax,
                                                               yMax = myyMax)
            a.Set(nodes = nodes2, name = follower_name)
            
            name_counter = name_counter + 1
        
        for i in range(len(top_flakes)):
            flake = top_flakes[i][0]
            master_name = "TBM2-IntSurf-" + str(name_counter) + "-" + matrix_name
            follower_name = "TBM2-IntSurf-" + str(name_counter) + "-" + flake
            
            first_list_names.append(matrix_name)
            second_list_names.append(flake)
            
            myxMin = top_flakes[i][1] - xtol
            myyMin = y_vals[last_index] + flake_thickness - ytol
            myxMax = top_flakes[i][2] + xtol
            myyMax = y_vals[last_index] + flake_thickness + ytol
            
            a = my_mdb.rootAssembly
            s1 = a.instances[matrix_name].edges
            side1Edges1 = s1.getByBoundingBox(xMin = myxMin,
                                              yMin = myyMin,
                                              xMax = myxMax,
                                              yMax = myyMax)
            region1 = a.Surface(side1Edges = side1Edges1, name = master_name)
            first_list.append(region1)
                    
            s2 = a.instances[flake].edges
            side1Edges2 = s2.getByBoundingBox(xMin = myxMin,
                                              yMin = myyMin,
                                              xMax = myxMax,
                                              yMax = myyMax)
            region2 = a.Surface(side1Edges = side1Edges2, name = follower_name)
            second_list.append(region2)
            
            #Adding in Nodesets for PostProcessing stuff later
            nodes1 = a.instances[matrix_name].nodes.getByBoundingBox(xMin = myxMin,
                                                                     yMin = myyMin,
                                                                     xMax = myxMax,
                                                                     yMax = myyMax)
            a.Set(nodes = nodes1, name = master_name)
            nodes2 = a.instances[flake].nodes.getByBoundingBox(xMin = myxMin,
                                                               yMin = myyMin,
                                                               xMax = myxMax,
                                                               yMax = myyMax)
            a.Set(nodes = nodes2, name = follower_name)
            
            name_counter = name_counter + 1
        return(name_counter)
    #name_counter = TBMatrixContact(name_counter)
    
    def SideFlakeContact(name_counter, my_mdb = my_mdb, flake_list = flake_list, Coords = Coords,
                         flake_list_lengths = flake_list_lengths, matrix_length = matrix_length,
                         matrix_name = matrix_name, arc_offset = arc_offset):
        
        a = my_mdb.rootAssembly
        for i in range(len(flake_list)):
            if(Coords[i][0] > 0 and Coords[i][0] < matrix_length):
                flake = flake_list[i]
                master_name = "LSM-IntSurf-" + str(name_counter) + "-" + matrix_name
                follower_name = "LSM-IntSurf-" + str(name_counter) + "-" + flake     
                
                first_list_names.append(matrix_name)
                second_list_names.append(flake)
                
                myxMin = Coords[i][0] - arc_offset[0] - xtol
                myyMin = Coords[i][1] - ytol
                myxMax = Coords[i][0] + arc_offset[0] + xtol
                myyMax = Coords[i][1] + flake_thickness+ ytol
                
                s1 = a.instances[matrix_name].edges
                side1Edges1 = s1.getByBoundingBox(xMin = myxMin,
                                                  yMin = myyMin,
                                                  xMax = myxMax,
                                                  yMax = myyMax)
                region1 = a.Surface(side1Edges = side1Edges1, name = master_name)
                first_list.append(region1)
                
                
                s2 = a.instances[flake].edges
                side1Edges2 = s2.getByBoundingBox(xMin = myxMin,
                                                  yMin = myyMin,
                                                  xMax = myxMax,
                                                  yMax = myyMax)
                region2 = a.Surface(side1Edges = side1Edges2, name = follower_name)
                second_list.append(region2)
                
                #Adding in Nodesets for PostProcessing stuff later
                # nodes1 = a.instances[matrix_name].nodes.getByBoundingBox(xMin = myxMin,
                #                                                          yMin = myyMin,
                #                                                          xMax = myxMax,
                #                                                          yMax = myyMax)
                nodes1 = a.surfaces[master_name].nodes
                a.Set(nodes = nodes1, name = master_name)
                # nodes2 = a.instances[flake].nodes.getByBoundingBox(xMin = myxMin,
                #                                                    yMin = myyMin,
                #                                                    xMax = myxMax,
                #                                                    yMax = myyMax)
                nodes2 = a.surfaces[follower_name].nodes
                a.Set(nodes = nodes2, name = follower_name)
                
                name_counter = name_counter + 1
                
            if((Coords[i][0] + flake_list_lengths[i]) > 0 and (Coords[i][0] + flake_list_lengths[i]) < matrix_length - xtol):
                flake = flake_list[i]
                master_name = "RSM-IntSurf-" + str(name_counter) + "-" + matrix_name
                follower_name = "RSM-IntSurf-" + str(name_counter) + "-" + flake          
                
                first_list_names.append(matrix_name)
                second_list_names.append(flake)
                
                myxMin = Coords[i][0] + flake_list_lengths[i] - arc_offset[0] - xtol
                myyMin = Coords[i][1] - ytol
                myxMax = Coords[i][0] + flake_list_lengths[i] + arc_offset[0] + xtol
                myyMax = Coords[i][1] + flake_thickness + ytol
                
                s1 = a.instances[matrix_name].edges
                side1Edges1 = s1.getByBoundingBox(xMin = myxMin,
                                                  yMin = myyMin,
                                                  xMax = myxMax,
                                                  yMax = myyMax)
                region1 = a.Surface(side1Edges = side1Edges1, name = master_name)
                first_list.append(region1)
                
                s2 = a.instances[flake].edges
                side1Edges2 = s2.getByBoundingBox(xMin = myxMin,
                                                  yMin = myyMin,
                                                  xMax = myxMax,
                                                  yMax = myyMax)
                region2 = a.Surface(side1Edges = side1Edges2, name = follower_name)
                second_list.append(region2)
                
                # nodes1 = a.instances[matrix_name].nodes.getByBoundingBox(xMin = myxMin,
                #                                                          yMin = myyMin,
                #                                                          xMax = myxMax,
                #                                                          yMax = myyMax)
                nodes1 = a.surfaces[master_name].nodes
                a.Set(nodes = nodes1, name = master_name)
                # nodes2 = a.instances[flake].nodes.getByBoundingBox(xMin = myxMin,
                #                                                    yMin = myyMin,
                #                                                    xMax = myxMax,
                #                                                    yMax = myyMax)
                #could try something like
                nodes2 = a.surfaces[follower_name].nodes
                a.Set(nodes = nodes2, name = follower_name)
            
                name_counter = name_counter + 1
            
    SideFlakeContact(name_counter)
    
    #Now create the actual interaction
    pairlist = []
    for i in range(len(first_list)):
        temppair = (first_list[i], second_list[i])
        pairlist.append(temppair)
    locked_pairs = tuple(pairlist)
    
    pairlistWcontacttype = []
    for i in range(len(pairlist)):
        temppair = (first_list[i], second_list[i], "IntProp-1")
        pairlistWcontacttype.append(temppair)
    locked_pairsWcontact = tuple(pairlistWcontacttype)
    
    #if we want to define a general explicit contact
    my_mdb.ContactExp(createStepName='Initial', name='All_Interactions')
    my_mdb.interactions["All_Interactions"].includedPairs.setValuesInStep(
    addPairs= locked_pairs, stepName='Initial', useAllstar=OFF)
    my_mdb.interactions["All_Interactions"].contactPropertyAssignments.appendInStep(
    assignments=((GLOBAL, SELF, 'IntProp-1-NoC'), ), stepName='Initial')
    my_mdb.interactions['All_Interactions'].contactPropertyAssignments.appendInStep(
    assignments=locked_pairsWcontact, stepName='Initial')
    ######
    # OR #
    ######
    
    #if we want Surface to Surface Exp
    # for i in range(len(locked_pairs)):
    #     int_name = "Interaction" + str(i)
    #     my_mdb.SurfaceToSurfaceContactExp(name = int_name,
    #                         createStepName = "Initial", master = locked_pairs[i][0],
    #                         slave = locked_pairs[i][1], mechanicalConstraint = KINEMATIC, sliding=FINITE,
    #                         interactionProperty = "IntProp-1", initialClearance=OMIT,
    #                         datumAxis = None, clearanceRegion = None)
    
    
    #End of Funciton
    

    
#DefineInteractions()





 #%%
#This is the master function!
def GenerateGeometry(
        arc_offset = None, aspect_ratio = None,
        const_dist_flake_y = const_dist_flake_y, cut_flake_tol = None,
        dist_flake_x = None, dist_flake_y = None,
        flake_concentration_x = None,
        flake_length = None, flake_thickness = None,
        initial_displacement = None, length_of_shift = None,
        matrix_height = None, matrix_length = None, mesh_size = None,
        n_flake_y = None, n_flake_x = None, n_until_shift = None,
        run_seed = None, density_vec = density_vec,
        ductile_properties_df = ductile_properties_df, elastic_mod_vec = elastic_mod_vec,
        elastic_pois_vec = elastic_pois_vec, names_vec = names_vec,
        plastic_properties_df = plastic_properties_df,
        cohesive_table = None, tangential_table = None,
        damage_init_table = None, damage_evolution_table = None):
    
    import random
    import time
    import math
    if(run_seed is None):
        run_seed = int(time.time()*100)
    random.seed(run_seed)
    if(aspect_ratio is None):
        aspect_ratio = 75
    #These are my fix to get user define-able values while still having defaults.
    if(flake_thickness is None):
        flake_thickness = 0.0025 #2.5 nanometers
    if(flake_length is None):
        flake_length = aspect_ratio * flake_thickness
    if(flake_concentration_x is None):
        flake_concentration_x = 0.8 #80%
    if(dist_flake_y is None):
        dist_flake_y = 0
        #CAUTION, SCRIPT ISNT WELL TESTED FOR ANYTHING BESIDES 0!!!
    if(n_until_shift is None):
        n_until_shift = 1
        #Mostly outdated option, left in just in case removing breaks everything.
    if(n_flake_y is None):
        n_flake_y = 3
    if(n_flake_x is None and matrix_length is None):
        n_flake_x = 3
        matrix_length = (float(n_flake_x) + 1)*flake_length
    if(n_flake_x is None and matrix_length is not None):
        n_flake_x = int(math.floor(matrix_length/flake_length) + 1)
    if(n_flake_x is not None and matrix_length is None):
        matrix_length = (float(n_flake_x) + 1)*flake_length
    if(matrix_height is None):
        matrix_height = (float(n_flake_y)*flake_thickness) + (float(n_flake_y-1)*dist_flake_y)
    if(cut_flake_tol is None):
        cut_flake_tol = flake_length/10
    if(initial_displacement is None):
        initial_displacement = (-flake_length/2, 0, 0)
        #bottom left corner of each flake is (0,0).
    if(length_of_shift is None):
        length_of_shift = flake_length/2
    if(arc_offset is None):
        arc_offset = (flake_thickness/4, flake_thickness/2)
    if(dist_flake_x is None):
        temp_n_flake_x = int(math.floor(matrix_length * (flake_concentration_x) / flake_length))
        print("reasonable number of flakes in a row")
        print(temp_n_flake_x)
        print("space to fill with polymer")
        print(matrix_length * (flake_concentration_x) / flake_length)
        dist_flake_x = matrix_length * (1 - flake_concentration_x) / (temp_n_flake_x)
        print("Dist flake x")
        print(dist_flake_x)
    if(mesh_size is None):
        mesh_size = 0.0004
    if(cohesive_table is None):
        cohesive_table = ((1000000.0, 1000000.0, 1000000.0), )
    if(tangential_table is None):
        tangential_table = ((0.1, ), )
    if(damage_init_table is None):
        damage_init_table = ((100.0, 100.0, 100.0), )
    if(damage_evolution_table is None):
        damage_evolution_table = ((0.001, ), )
    
    
    
    
    
    
    
    
    
    
    
    
    
    InputVars = locals()
    temp = InputLog(InputVars)
    in_log_path = temp[0]
    input_file_counter = temp[1]
    n_models = len(mdb.models.keys())
    model_name = "Model-{}".format(n_models + 1)
    
    
    
    random_shifts = []
    cut_flakes_shifts = [] #if cutflakes are created, it will use these random shifts
    def myrandom(roundby = 6):
        #y = round(random.uniform(-1*dist_flake_x/4, dist_flake_x/4), roundby)
        #y = 0
        y = round(random.expovariate(lambd= 1/dist_flake_x), roundby)
        #note that they use exponential the same as wikipedia. i.e. lambda = 1/beta
        return(y)
        
    for i in range((n_flake_x + 1) * (n_flake_y)):
        temp = myrandom()
        random_shifts.append(temp)
    
    for i in range(2*(n_flake_y + 1)):
        temp = myrandom()
        cut_flakes_shifts.append(temp)
    del temp
    
    
    
    
    #############################################
    #Generate the tempflake and the tempmatrix  #
    #############################################
    #Could wrap this in a function, but I didnt #
    #############################################
    mdb.Model(modelType=STANDARD_EXPLICIT, name=model_name)
    session.viewports['Viewport: 1'].setValues(displayedObject=None)
    mdb.models[model_name].setValues(
        description='Units are force=microNewton; length=micrometer; time=second; mass=kg; pressure=MPa; density=kg/um^3=10E-18 kg/m^3')
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    # INITIALIZING THE THREE MATERIALS: ##################################################
    mdb.models[model_name].Material(name= names_vec[0])
    mdb.models[model_name].materials[names_vec[0]].Density(table=((density_vec[0], ), ))
    mdb.models[model_name].materials[names_vec[0]].Elastic(table=((elastic_mod_vec[0], elastic_pois_vec[0]), ))
    #%%
    mdb.models[model_name].materials[names_vec[0]].Plastic(table=plastic_properties_df[0])
    mdb.models[model_name].materials[names_vec[0]].DuctileDamageInitiation(table=ductile_properties_df)
    mdb.models[model_name].materials[names_vec[0]].ductileDamageInitiation.DamageEvolution(
        type=ENERGY, table=((0.002, ), ))
    #%%
    mdb.models[model_name].Material(name=names_vec[1])
    mdb.models[model_name].materials[names_vec[1]].Density(table=((density_vec[1], ),))
    mdb.models[model_name].materials[names_vec[1]].Elastic(table=((elastic_mod_vec[1], elastic_pois_vec[1]), ))
    mdb.models[model_name].materials[names_vec[1]].Plastic(table=plastic_properties_df[1])
    #%%
    ### INITIALIZING THE SOLID SECTIONS FOR THE THREE MATERIALS:
    mdb.models[model_name].HomogeneousSolidSection(name=('Solid_'+ names_vec[0]),
        material=names_vec[0], thickness=1.0)
    mdb.models[model_name].HomogeneousSolidSection(name=('Solid_'+ names_vec[1]),
        material=names_vec[1], thickness=None)
    #Define the "temp matrix"
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
        engineeringFeatures=OFF)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=ON)
    s = mdb.models[model_name].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(0.0, 0.0), point2=(matrix_length, matrix_height))
    p = mdb.models[model_name].Part(name='TempMatrix', dimensionality=TWO_D_PLANAR,
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts['TempMatrix']
    p.BaseShell(sketch=s) #set the rectangle sketch to this part
    s.unsetPrimaryObject()
    p = mdb.models[model_name].parts['TempMatrix']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    session.viewports['Viewport: 1'].view.fitView()
    p = mdb.models[model_name].parts['TempMatrix']
    f = p.faces
    faces = f.getByBoundingBox(xMin=-matrix_length, yMin=-matrix_height, xMax=2.0*matrix_length, yMax=2.0*matrix_height)
    region = p.Set(faces=faces, name='Matrix')
    p = mdb.models[model_name].parts['TempMatrix']
    p.SectionAssignment(region=region, sectionName=('Solid_'+names_vec[0]), offset=0.0,
        offsetType=MIDDLE_SURFACE, offsetField='',
        thicknessAssignment=FROM_SECTION)
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
        engineeringFeatures=OFF)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=ON)
    #Create the Flake template
    s1 = mdb.models[model_name].ConstrainedSketch(name='__profile__', sheetSize=2.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    bottom_left_point = (0.0,0.0)
    bottom_right_point = (flake_length, 0.0)
    top_left_point = (0.0 , flake_thickness)
    top_right_point = (flake_length, flake_thickness)

    s1.Line(point1 = bottom_left_point,
            point2 = bottom_right_point)
    s1.Line(point1 = top_left_point,
            point2 = top_right_point)
    s1.Arc3Points(point1 = bottom_left_point,
                  point2 = top_left_point,
                  point3 = (bottom_left_point[0] - arc_offset[0],
                            bottom_left_point[1] + arc_offset[1]))
    s1.Arc3Points(point1 = bottom_right_point,
                  point2 = top_right_point,
                  point3 = (bottom_right_point[0] + arc_offset[0],
                            bottom_right_point[1] + arc_offset[1]))

    p = mdb.models[model_name].Part(name='TempFlake', dimensionality=TWO_D_PLANAR,
        type=DEFORMABLE_BODY)
    p = mdb.models[model_name].parts['TempFlake']
    p.BaseShell(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models[model_name].parts['TempFlake']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models[model_name].sketches['__profile__']
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    session.viewports['Viewport: 1'].view.fitView()
    p = mdb.models[model_name].parts['TempFlake']
    f = p.faces
    faces = f.getByBoundingBox(xMin=-flake_length, yMin=-flake_thickness, 
                               xMax=2.0*flake_length, yMax=2.0*flake_thickness)
    region = p.Set(faces=faces, name='Flake')
    p = mdb.models[model_name].parts['TempFlake']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    p = mdb.models[model_name].parts['TempFlake']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#4 ]', ), )
    p.Set(edges=edges, name='Right')
    #: The set 'Top' has been created (1 edge).
    p = mdb.models[model_name].parts['TempFlake']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
    p.Set(edges=edges, name='Left')
    #: The set 'Bottom' has been created (1 edge).
    p = mdb.models[model_name].parts['TempFlake']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#8 ]', ), )
    p.Set(edges=edges, name='Top')
    #: The set 'Left' has been created (1 edge).
    p = mdb.models[model_name].parts['TempFlake']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#2 ]', ), )
    p.Set(edges=edges, name='Bottom')
    #: The set 'Right' has been created (1 edge).
    p = mdb.models[model_name].parts['TempFlake']
    p.SectionAssignment(region=region, sectionName=('Solid_'+names_vec[1]), offset=0.0,
        offsetType=MIDDLE_SURFACE, offsetField='',
        thicknessAssignment=FROM_SECTION)
    a = mdb.models[model_name].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
    a = mdb.models[model_name].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models[model_name].parts['TempMatrix']
    a.Instance(name='TempMatrix-1', part=p, dependent=ON)
    a = mdb.models[model_name].rootAssembly
    p = mdb.models[model_name].parts['TempFlake']
    a.Instance(name='TempFlake-1', part=p, dependent=ON)
    a = mdb.models[model_name].rootAssembly
    a.translate(instanceList=('TempFlake-1', ), vector=initial_displacement)
    a = mdb.models[model_name].rootAssembly
    # Pattern Variables:
    x = (1.0, 0.0, 0.0) # Direction vector for x direction
    y = (0.0, 1.0, 0.0) # Direction vector for y direction
    a.LinearInstancePattern(instanceList=('TempFlake-1', ), direction1=x,
        direction2=y, number1=(n_flake_x + 1), number2=n_flake_y, 
        spacing1=0.0,
        spacing2=(dist_flake_y + flake_thickness) )
    a = mdb.models[model_name].rootAssembly
    

    #This would set the flakes up for better use of nonnegative distributions
    
    
    ###################################################
    # End of Generating the TempFlake and TempMatrix  #
    ###################################################
    my_mdb = mdb.models[model_name]
    
    #Get the Linear Pattern instance list
    lin_pat_list = GetLinPatList(n_flake_x = n_flake_x, n_flake_y = n_flake_y)
    #Get the shifts needed for the "brick-like" shifts
    # brick_shift_list = GetBrickShiftList(n_flake_x = n_flake_x, n_flake_y = n_flake_y, 
    #                     n_until_shift = n_until_shift, flake_length = flake_length, 
    #                     length_of_shift = length_of_shift)
    
    
    
    #Now actually perform the shift
    counter = 0
    print(random_shifts)
    print(" ")
    print(cut_flakes_shifts)
    for i in range(n_flake_y):
        rowi = lin_pat_list[i::n_flake_y]
        a.translate(instanceList = (rowi[0], ), vector = (random_shifts[counter], 0, 0))
        counter = counter + 1
        for j in range(1,len(rowi)):
            prev_flake = rowi[j-1]
            x_coord = a.instances[prev_flake].getTranslation()
            a.translate(instanceList = (rowi[j], ),
                        vector = (random_shifts[counter] + x_coord[0] +
                                  flake_length-initial_displacement[0] + 2*arc_offset[0],
                                  0, 0))
            counter = counter + 1
            
            
            
            
            
        #a.translate(instanceList = rowi, vector = ((-1 * brick_shift_list[i]), 0, 0))
    #Use the random shifts defined in the beginning parameters to shift the parts again
    #for i in range(len(random_shifts)):
        #a.translate(instanceList = [lin_pat_list[i], ], vector = (random_shifts[i],0,0))
    
    
    
    #Remove the flakes that stick past the model
    temp = DeleteFlakes(model_name = model_name, lin_pat_list= lin_pat_list,
                        a=a, matrix_length = matrix_length,
                        flake_length = flake_length)
    #wanted two returns, put them in a list and then deconstruct
    lin_pat_list = temp[0]
    deleted_list = temp[1]
    del temp
    
    #Create "Cutflake parts" and add them to the assembly
    temp = CreateCutFlakes(my_mdb = my_mdb, deleted_list = deleted_list,
                        lin_pat_list = lin_pat_list,
                        n_flake_y = n_flake_y,
                        cut_flake_tol = cut_flake_tol,
                        flake_thickness = flake_thickness,
                        arc_offset = arc_offset,
                        cut_flakes_shifts = cut_flakes_shifts,
                        dist_flake_x = dist_flake_x,
                        flake_length = flake_length,
                        matrix_length = matrix_length,
                        matrix_height = matrix_height)
    #wanted two returns, put them in a list and then deconstruct
    cut_flakes_names = temp[0]
    cut_flakes_length = temp[1]
    del temp
    
    #combine cut_flakes and regular flakes 
    my_mdb = mdb.models[model_name] 
    cutting_list = []
    cutting_list_instances = lin_pat_list
    for i in lin_pat_list:
        temp =  my_mdb.rootAssembly.instances[i]
        cutting_list.append(temp)
    for i in cut_flakes_names:
        cutting_list_instances.append(i)
        temp =  my_mdb.rootAssembly.instances[i]
        cutting_list.append(temp)
    #Now cut the matrix
    matrix_name = CutMatrix(my_mdb = my_mdb, cutting_list = cutting_list,
                            cutting_list_instances = cutting_list_instances)
    
    #Calculate the Actual Concentration
    lin_pat_area = (len(lin_pat_list) - len(cut_flakes_names))*((flake_length + arc_offset[0])*flake_thickness)
    #lin_pat_list contains all flake names, take away the cut flakes...
    cut_flake_area = 0
    for i in range(len(cut_flakes_length)):
        temp_cut_flake_area = cut_flakes_length[i] * flake_thickness
        cut_flake_area = cut_flake_area + temp_cut_flake_area
    tot_flake_area = cut_flake_area + lin_pat_area
    
    actual_concentration = tot_flake_area/(matrix_length * matrix_height)
    f = open(in_log_path, 'a')
    mystring = "actual_concentration: {}".format(actual_concentration)
    f.write(mystring)
    f.close()
    
    #Make instances independent of each other for a future step
    GetIndependent(my_mdb = my_mdb, flake_list = cutting_list_instances,
                        matrix_name = matrix_name)
    
    #Partition the flakes based on contacts
    line_coords = MasterCreatePartitionV3(
        flake_list = cutting_list_instances, my_mdb = my_mdb,
        cut_flakes_length = cut_flakes_length,
        cut_flakes_names = cut_flakes_names,
        flake_length = flake_length,dist_flake_y = dist_flake_y,
        n_flake_y = n_flake_y, matrix_height = matrix_height,
        matrix_length = matrix_length)
    
    
    #Mesh the parts
    CreateMesh(my_mdb = my_mdb, cutting_list_instances = cutting_list_instances,
                    matrix_name = matrix_name,
                    matrix_length = matrix_length,
                    mesh_size = mesh_size,
                    matrix_height = matrix_height)
    
    # #Define the Interaction Properties
    DefineIntProps(my_mdb = my_mdb, cohesive_table = cohesive_table,
                    tangential_table=tangential_table,
                    damage_init_table = damage_init_table,
                    damage_evolution_table = damage_evolution_table)
    
    # #Add the interaction term
    DefineInteractions(my_mdb = my_mdb, flake_list = cutting_list_instances,
                        matrix_name = matrix_name, cut_flakes_names = cut_flakes_names,
                        cut_flakes_length = cut_flakes_length,matrix_length = matrix_length,
                        flake_thickness = flake_thickness, n_flake_y = n_flake_y,
                        flake_length = flake_length,
                        initial_displacement= initial_displacement,
                        matrix_height= matrix_height,
                        arc_offset= arc_offset,
                        input_file_counter = input_file_counter)
    
    
    # # #Add in boundary conditions
    DefineBoundaryConditions(my_mdb = my_mdb, matrix_length = matrix_length,
                              matrix_height = matrix_height, flake_list = cutting_list_instances,
                              matrix_name = matrix_name, cut_flakes_length = cut_flakes_length,
                              cut_flakes_names = cut_flakes_names, flake_length = flake_length,
                              desired_max_strain = 0.005, n_moving_ends = 2, time_units = 2e-06,
                              datum_shift = 0.002, mesh_size = mesh_size)
    
    
    
    # # #Create the "Step-1"
    # # #Done in Boundary conditions step instead
    
    # # #Create the Job
    job_name = "Job-{:04d}".format(input_file_counter)
    
    mdb.Job(name = job_name, model = model_name, description = " ",
            type = ANALYSIS, atTime = None, waitMinutes = 0, waitHours = 0, queue = None,
            memory = 10, memoryUnits = GIGA_BYTES, explicitPrecision=DOUBLE_PLUS_PACK, 
            nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
            resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=4, 
            activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=4)
    mdb.jobs[job_name].writeInput(consistencyChecking = OFF)
    
    
    # a = my_mdb.rootAssembly
    # session.viewports['Viewport: 1'].setValues(displayedObject=a)
    print("Actual Flake Concentration: {}".format(actual_concentration))
    
    
#GenerateGeometry()
print("Call GenerateGeometry() to create the default Part")
#GenerateGeometry()



#%%%
# K_vector = [100000.0, 200000.0, 500000.0, 1000000.0]

# T_vector = [12.9,  20.0, 55.0, 64.0, 25.0] #first 4 from ref1, last from ref 2
# G_vector = [0.008, 0.02, 0.15, 0.2, 10.0]
def MakeTable(K_val, reps):
    first = tuple([K_val] * reps)
    return_vec = (first, )
    return(return_vec)

# #Trying to match the referrences
# for i in range(len(T_vector)):
#     for j in range(len(K_vector)):
#         GenerateGeometry(n_flake_y = 6,
#                 cohesive_table=MakeTable(K_vector[j], 3),
#                 damage_init_table=MakeTable(T_vector[i], 3),
#                 damage_evolution_table=MakeTable(G_vector[i], 1),
#                 run_seed=8675309) 


#%%
# import os
# #my_directory = r"C:\Users\jason\OneDrive\Documents\SDSU\Grad\AFRL-Research\ZFourth40"
# def getRunSeeds(directory):
#     allfiles = os.listdir(directory)
#     txts = []
#     for i in allfiles:
#         if(i[i.find("."):len(i)] == ".txt"):
#             txts.append(i)
    
#     prev_seeds = []

#     for i in range(len(txts)):
#         full = directory + "/" + txts[i]
#         f = open(full, "r")
#         f_lines = f.readlines()
#         f.close()
#         for j in range(len(f_lines)):
#             if("run_seed" in f_lines[j]):
#                 temp = f_lines[j]
#                 temp = temp[temp.find(": ")+1:temp.find("\n")]
#                 temp = float(temp)
#                 prev_seeds.append(temp)
        
#     return(prev_seeds)

#%%
# K_value = 1000000.0
# T_value = 12.9
# G_value = 0.008

# for i in range(20):
#     GenerateGeometry(n_flake_y = 12,
#                      aspect_ratio = 75,
#                      matrix_length = 0.75,
#                      cohesive_table=MakeTable(K_value,3),
#                      damage_init_table = MakeTable(T_value,3),
#                      damage_evolution_table = MakeTable(G_value,1))


#%%
# K_value = 1000000.0
# T_vector = [12.9, 64.0]
# G_vector = [0.008, 0.2]
# flake_cons_vector = [0.70, 0.75, 0.8, 0.85, 0.9]

# for k in range(len(flake_cons_vector)):
#     i = 1
#     #for i in range(len(T_vector)):
#     #    for j in range(1):
#     GenerateGeometry(n_flake_y = 12,
#                      matrix_length = 0.75,
#                      aspect_ratio = 75,
#                      flake_concentration_x = flake_cons_vector[k],
#                      cohesive_table=MakeTable(K_value, 3),
#                      damage_init_table=MakeTable(T_vector[i], 3),
#                      damage_evolution_table=MakeTable(G_vector[i], 1))        





#%%

#my_directory = r"/p/home/jrhasse/"
# prev_seeds = getRunSeeds(directory = my_directory)
# print(prev_seeds)

# prev_seeds.sort()
# print(prev_seeds)

# for i in range(len(T_vector)):
#     for j in range(3):
#         GenerateGeometry(n_flake_y = 12,
#                          cohesive_table=MakeTable(K_value, 3),
#                          damage_init_table=MakeTable(T_vector[i], 3),
#                          damage_evolution_table=MakeTable(G_vector[i], 1),
#                          run_seed = prev_seeds[counter])        
#         counter = counter + 1











#%%
# Inputfilenames = []
# for i in range(len(T_vector)):
#     for j in range(len(K_vector)):
#         temp = [K_vector[j],T_vector[i],G_vector[i]]
#         Inputfilenames.append(temp)


#%%

