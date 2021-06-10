"""
Functions for using template files with the Helmholtz Cage.

Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import os

from utilities import read_from_csv


def retrieve_template(file_dir, file_name):
    """
    Convert data from a template file into a dict.
    """

    time = []
    x_val = []
    y_val = []
    z_val = []

    # Read in data from csv data
    content = read_from_csv(file_dir, file_name)
    
    # Parse data into lists
    i = 0
    for row in content:
        if i==0:
            pass
        else:
            if i==1:
                field_or_voltage = str(row[0])
            time.append(float(row[1]))
            x_val.append(float(row[2]))
            y_val.append(float(row[3]))
            z_val.append(float(row[4]))
            
        i += 1

    # Store values in dict
    template = {
        "time": time,
        "type": field_or_voltage,
        "x_val": x_val,
        "y_val": y_val,
        "z_val": z_val
    }
    
    return template
    
def check_template_values(temp_data, limits):
    """
    Check the values from a template file to ensure they are outside
    the systems limits.
    """
    
    is_okay = True
    
    # Get data lists out of dict
    time = temp_data["time"]
    x_val = temp_data["x_val"]
    y_val = temp_data["y_val"]
    z_val = temp_data["z_val"]
    
    # Check values in lists
    if len(time) == len(x_val) == len(y_val) == len(z_val):
        
        # Check run type
        if temp_data["type"] == "field":
            max_val = limits[0]
        elif temp_data["type"] == "voltage":
            max_val = limits[1]
        else:
            is_okay = False
            print("ERROR: Run type is not 'field' or 'voltage'.")
            return is_okay
        
        for i in range(0, len(time)):
            
            # Check that time values are ordered
            if not time[i] > time[i-1] and not i==0:
                is_okay = False
                print("ERROR: Time values are not in ascending order.")
                break
                
            # Check that the values are below system limits
            if (x_val[i] > max_val):
                print("ERROR: {} is above limit".format(x_val[i]))
                print("Check: 'X' value in row {}".format(i))
                is_okay = False
            if (y_val[i] > max_val):
                print("ERROR: {} is above limit".format(y_val[i]))
                print("Check: 'Y' value in row {}".format(i))
                is_okay = False
            if (z_val[i] > max_val):
                print("ERROR: {} is above limit".format(z_val[i]))
                print("Check 'Z' value in row {}".format(i))
                is_okay = False
    else:
        print ("ERROR: The number of values on each axis is not all equal.")
        is_okay = False
    
    return is_okay
