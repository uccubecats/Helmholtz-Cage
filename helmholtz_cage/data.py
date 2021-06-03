"""
Objects and functions for storing and logging Helmholtz Cage data. 

Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import datetime
import os

from utilities import write_to_csv


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
        self.template_file = "none found"

        # Calibration data
        self.calibration_file = "none found"
        self.xy_cutoff = None
        self.yz_cutoff = None

        # Session logging data
        self.session_file = ""
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
        self.req_type = [] # i.e. field vs. volt
        
    def start_new_log_file(self):
        """
        Create and write the first line of a session log file.
        
        TODO: Test
        """
        
        start = ["time",
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
                 "z_req",
                 "req_type"]
        
        # Create filename
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.session_file = "session_{}.csv".format(date)
            
        # Write initial line to file 
        write_to_csv(self.session_dir, self.session_file, start, 'w')
        
    def log_current_data(self):
        """
        Log the current data set to the session log file.
        
        TODO: Test
        """
        
        # Place elements into list
        row = [self.time,
               self.Vx,
               self.Vy,
               self.Vz,
               self.Ix,
               self.Iy,
               self.Iz,
               self.Bx,
               self.By,
               self.Bz,
               self.x_req,
               self.y_req,
               self.z_req,
               self.req_type]
               
        # Write to session log file
        write_to_csv(self.session_dir, self.session_file, row, 'a')
