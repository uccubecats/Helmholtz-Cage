"""
Functions for using template files with the Helmholtz Cage.

Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import os

from utilities import read_csv


def retrieve_template(self, main_dir, filename):
    """
    Convert data from a template file into a dict.
    
    TODO: Test
    """

    time = []
    x_val = []
    y_val = []
    z_val = []

    # Read in data from csv data
    template_dir = os.path.join(main_dir, "templates")
    content = read_csv(temp_dir, filename)
        
    # Parse data into lists
    i = 0
    for row in content:
        if i==0:
            pass
        else:
            if i==1:
                field_or_voltage == str(row[0])
            time.append(row[1])
            x_val.append(row[2])
            y_val.append(row[3])
            z_val.append(row[4])
            
        i += 1
    
    # Validate values
    #TODO
    
    # Store values in dict
    template = {
        "time": time,
        "type": field_or_voltage,
        "x_val": x_val,
        "y_val": y_val,
        "z_val": z_val
    }
    
    return template
