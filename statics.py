from numpy import array
from numpy import linalg

from math import sin
from math import cos
from math import radians

from random import Random

from pprint import pprint

from json import load

def get_unknown_list(points):
    unknown_list = list()
    
    for coord in points.keys():
        
        point = points[coord]
        forces = point["forces"]
        
        for force_name in point["forces"].keys():
            
            force = forces[force_name]
            
            if not force["is_known"] and not force["is_internal"]:
                
                unknown_list.append(force_name)    
    
    return unknown_list

def get_internal_list(points):
    internal_list = list()
    
    for coord in points.keys():
        
        point = points[coord]
        forces = point["forces"]
        
        for force_name in point["forces"].keys():
            
            force = forces[force_name]
            
            if not force["is_known"] and force["is_internal"]:
                if force_name not in internal_list:
                    internal_list.append(force_name)    
    
    return internal_list

def get_system():
    points = dict()
    filename = input("Enter file name for system analysis: ")

    with open(filename) as file:
        points = load(file)
                    
    return points

def set_up_external_system(points, golden_point, unknown_list):
    
    forces_x = [0] * 3
    forces_y = [0] * 3
    moments_z = [0] * 3
    
    constants = [0] * 3
    
    for point in points.values():

        coord = point["coords"]
        forces = point["forces"]

        for force_name in point["forces"].keys():

            force = forces[force_name]
            
            lev_x = coord[0] - golden_point[0]
            lev_y = coord[1] - golden_point[1]
            
            if force["is_known"] and not force["is_internal"]:
                
                force_x_comp = force["magnitude"] * force["unit_vector"][0]
                force_y_comp = force["magnitude"] * force["unit_vector"][1]
                
                # forces
                constants[0] -= force_x_comp
                constants[1] -= force_y_comp
                
                # moment
                constants[2] -= (lev_x * force_y_comp) - (lev_y * force_x_comp)

            elif not force["is_known"] and not force["is_internal"]:
                
                index = unknown_list.index(force_name)
                
                # forces
                forces_x[index] = force["unit_vector"][0]
                forces_y[index] = force["unit_vector"][1]
                
                # moment
                moments_z[index] = (lev_x * force["unit_vector"][1]) - (lev_y * force["unit_vector"][0])
    
    processed = {"forces_x": forces_x, 
                 "forces_y": forces_y, 
                 "moments_z": moments_z, 
                 "constants": constants}
    
    return processed

def start():
    points = get_system()
    
    # scan for number of unknowns
    unknown_list = get_unknown_list(points)
    internal_list = get_internal_list(points)
    
    print("Internal forces:")
    print(internal_list)
    
    golden_cap = 30
    rng = Random()
    golden_point = [rng.random() * golden_cap] * 2
    # unused
    # num_unknowns = len(unknown_list)
    
    print("External forces:")
    print(unknown_list)
    
    external = set_up_external_system(points, golden_point, unknown_list)
    
    aug_external = array([external["forces_x"], external["forces_y"], external["moments_z"]])
    b = array(external["constants"])
            
    # debug
    # print("Augmented matrix: ")
    # print(augmented)
    
    # print("Solution vector: ")
    # print(b)
    
    solved_external = linalg.solve(aug_external, b)
    
    print("Processed solution for external forces: ")
    
    # prints and updates magnitudes
    for i in range(len(unknown_list)):
        print(unknown_list[i] + ": " + str(solved_external[i]))
        for point in points.values():
            for force_name in point["forces"].keys():
                if force_name in unknown_list:
                    point["forces"][force_name]["magnitude"] = solved_external[unknown_list.index(force_name)]
                    point["forces"][force_name]["is_known"] = True
    
    # pprint(points)
    
    reiteration_needed = True
    
    while reiteration_needed:
        
        reiteration_needed = False
        
        for point in points.values():
            
            forces = point["forces"]
            
            force_names_x = [force_name for force_name in forces.keys()
                                        if forces[force_name]["unit_vector"][0] != 0]
            unknown_x_names = [force_name for force_name in force_names_x
                                           if not forces[force_name]["is_known"]]
            known_x_names = [force_name for force_name in force_names_x
                                           if forces[force_name]["is_known"]]
            
            if (len(unknown_x_names)) == 1:
                
                reiteration_needed = True
                const_x = 0
                
                for force_name in known_x_names:
                    const_x -= forces[force_name]["magnitude"] * forces[force_name]["unit_vector"][0]
                
                solved = const_x / forces[unknown_x_names[0]]["unit_vector"][0]
                
                forces[unknown_x_names[0]]["magnitude"] = solved
                forces[unknown_x_names[0]]["is_known"] = True
                
                print("Solving: F_x | " 
                      + unknown_x_names[0] + " * " 
                      + str(forces[unknown_x_names[0]]["unit_vector"][1]) 
                      + " = " + str(const_x)
                      + " | Internal force " + unknown_x_names[0] + ": " + str(solved))
                
                for point in points.values():
                    if unknown_x_names[0] in point["forces"].keys():
                        point["forces"][unknown_x_names[0]]["magnitude"] = solved
                        point["forces"][unknown_x_names[0]]["is_known"] = True
                        
            force_names_y = [force_name for force_name in forces.keys()
                                        if forces[force_name]["unit_vector"][1] != 0]
            unknown_y_names = [force_name for force_name in force_names_y
                                           if not forces[force_name]["is_known"]]
            known_y_names = [force_name for force_name in force_names_y
                                           if forces[force_name]["is_known"]]
            
            if (len(unknown_y_names)) == 1:
                
                reiteration_needed = True
                const_y = 0
                
                for force_name in known_y_names:
                    const_y -= forces[force_name]["magnitude"] * forces[force_name]["unit_vector"][1]
                
                solved = const_y / forces[unknown_y_names[0]]["unit_vector"][1]
                
                forces[unknown_y_names[0]]["magnitude"] = solved
                forces[unknown_y_names[0]]["is_known"] = True
                
                print("Solving: F_y | " 
                      + unknown_y_names[0] + " * " 
                      + str(forces[unknown_y_names[0]]["unit_vector"][1]) 
                      + " = " + str(const_y) 
                      + " | Internal force " + unknown_y_names[0] + ": " + str(solved))
                
                for point in points.values():
                    if unknown_y_names[0] in point["forces"].keys():
                        point["forces"][unknown_y_names[0]]["magnitude"] = solved
                        point["forces"][unknown_y_names[0]]["is_known"] = True
    
    pprint(points)
            
start()