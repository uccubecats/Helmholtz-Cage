#!/usr/bin/env python3

"""
  Objects and functions for storing and logging Helmholtz Cage data. 
  
  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import datetime
import os

from tabulate import tabulate

from utilities.files import write_to_csv


class Data(object):
    """
    A class to store data and log data from from the Helmholtz Cage 
    during run.
    """
    
    def __init__(self, main_dir):
        
        # Get session log file directory
        self.session_dir = os.path.join(main_dir, "sessions")
        
        # Plot data
        self.plots_created = False # flag variable so plots are only created once
        self.plot_titles = "" # flag variable so titles are only added the first time data is logged
        
        # Template data
        self.template_file = None
        
        # Calibration data
        self.calibration_file = None
        self.xy_cutoff = None
        self.yz_cutoff = None
        
        # Session logging data
        self.start_time = None
        self.time = []
        self.Vx = []
        self.Vy = []
        self.Vz = []
        self.Ix = []
        self.Iy = []
        self.Iz = []
        self.Bx = []
        self.By = []
        self.Bz = []
        self.x_req = []
        self.y_req = []
        self.z_req = []
        self.req_type = "" # i.e. field vs. voltage
        
        # Store common elements for display and storage
        self.labels = ["time",
                       "Vx",
                       "Vy",
                       "Vz",
                       "Ix",
                       "Iy",
                       "Iz",
                       "Bx",
                       "By",
                       "Bz",
                       "x_req",
                       "y_req", 
                       "z_req"]
                      
        self.units = ["secs",
                      "volts",
                      "volts",
                      "volts",
                      "amps",
                      "amps",
                      "amps",
                      "gauss",
                      "gauss",
                      "gauss"]
    
    def __str__(self):
        
        # Create table headers
        output = "%==================================%\n" +\
                 "SESSION DATA\n" +\
                 self.start_time.strftime("%B %d, %Y %I:%M:%S %p") + "\n" +\
                 "control type: " + self.req_type + "\n\n"
        
        # Retrieve data
        points = []
        for t in range(0, len(self.time)):
            points.append(self.retrieve_data_point(t))
        
        # Put formatted data into string
        output += tabulate(points, headers=self.labels, floatfmt="0.3f")
        output += "\n%==================================%"
        
        return output
    
    def write_to_file(self):
        """
        Write the current data set to a csv file.
        """
        
        # Add header information
        header = [["request type", self.req_type],
                  ["calibration_file", self.calibration_file],
                  ["template_file", self.template_file]]
        
        # Add request units
        if self.req_type == "voltage":
            req_unit = "volts"
        elif self.req_type == "field":
            req_unit = "gauss"
        units = [self.units + [req_unit, req_unit, req_unit]]
        
        # Add each time point as row in csv
        data = []
        for i in range(0, len(self.time)):
            point = self.retrieve_data_point(i)
            data.append(point)
        
        # Create file name
        start_t_str = self.start_time.strftime("%y%m%d_%H%M%S")
        session_file = "session_{}.csv".format(start_t_str)
        
        # Write data to file
        content = header + [self.labels] + units + data
        write_to_csv(self.session_dir, session_file, content, 'w')
    
    def clear_data(self):
        """
        Delete all data and reset the data object.
        """
        
        self.start_time = None
        self.time = []
        self.Vx = []
        self.Vy = []
        self.Vz = []
        self.Ix = []
        self.Iy = []
        self.Iz = []
        self.Bx = []
        self.By = []
        self.Bz = []
        self.x_req = []
        self.y_req = []
        self.z_req = []
        self.req_type = ""
    
    def retrieve_data_subset(self, indices):
        """
        Given a list of indices, strip them out of the data, and place
        them into a new Data object.
        """
        
        subset = Data("")
        
        # Retrieve all data from indices
        for i in indices:
            subset.time.append(self.time[i])
            subset.Vx.append(self.Vx[i])
            subset.Vy.append(self.Vy[i])
            subset.Vz.append(self.Vz[i])
            subset.Ix.append(self.Ix[i])
            subset.Iy.append(self.Iy[i])
            subset.Iz.append(self.Iz[i])
            subset.Bx.append(self.Bx[i])
            subset.By.append(self.By[i])
            subset.Bz.append(self.Bz[i])
            subset.x_req.append(self.x_req[i])
            subset.y_req.append(self.y_req[i])
            subset.z_req.append(self.z_req[i])
            subset.req_type = self.req_type
            
        return subset
    
    def retrieve_data_point(self, i):
        """
        Retrieve a specific data point based on its index.
        """
        
        point = [self.time[i],
                 self.Vx[i],
                 self.Vy[i],
                 self.Vz[i],
                 self.Ix[i],
                 self.Iy[i],
                 self.Iz[i],
                 self.Bx[i],
                 self.By[i],
                 self.Bz[i],
                 self.x_req[i],
                 self.y_req[i],
                 self.z_req[i]]
        
        return point
