"""
Objects and functions for calibrating the Helmholtz Cage.

Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import os

from scipy import stats

from utilities import read_from_csv, write_to_csv


class Calibration(object):
    """
    Helmholtz Cage calibration object.
    """
    
    def __init__(self, main_dir, filename):
        
        # Filename and directory
        self.filename = filename
        self.calibration_dir = os.path.join(main_dir, "calibrations")
        
        # Initialize calibration variables
        self.calibration_log_file = ""
        self.x_slope = 0.0
        self.x_intercept = 0.0
        self.x_zero = 0.0
        self.x_r = 0.0
        self.x_resist = 0.0
        self.y_slope = 0.0
        self.y_intercept = 0.0
        self.y_zero = 0.0
        self.y_r = 0.0
        self.y_resist = 0.0
        self.z_slope = 0.0
        self.z_intercept = 0.0
        self.z_zero = 0.0
        self.z_r = 0.0
        self.z_resist = 0.0
        
    def calibrate_from_data(self, data):
        """
        Given a calibration data set, get relevant calibration data from
        each single-axid coil pair using linear regressions.
        
        TODO: Test
        """
        
        # Split data between each axis
        # NOTE: TODO description of cutoffs    
        Vx_series = [data.Vx_out[:data.xy_cutoff]]
        Vy_series = [data.Vy_out[data.xy_cutoff+1:data.yz_cutoff]]
        Vz_series = [data.Vz_out[data.yz_cutoff+1:]]
        Bx_series = [data.Bx_act[:data.xy_cutoff]]
        By_series = [data.By_act[data.xy_cutoff+1:data.yz_cutoff]]
        Bz_series = [data.Bz_act[data_yz_cutoff+1]]
        
        # Perform linear regressions
        x_values = self.perform_linear_regression(Vx_series, Bx_series)
        y_values = self.perform_linear_regression(Vy_series, By_series)
        z_values = self.perform_linear_regression(Vz_series, Bz_series)
        
        # Estimate resistance
        #TODO
        
        # Store values
        self.x_slope = x_values[0]
        self.x_intercept = x_values[1]
        self.x_zero = x_values[2]
        self.x_r = x_values[3]
        self.y_slope = y_values[0]
        self.y_intercept = y_values[1]
        self.y_zero = y_values[2]
        self.y_r = y_values[3]
        self.z_slope = z_values[0]
        self.z_intercept = z_values[1]
        self.z_zero = z_values[2]
        self.z_r = z_values[3]
        
    def perform_linear_regression(self, X, Y):
        """
        Determine a linear regression of a data set, including a slope,
        x- and y-intercepts, and r-value.
        
        TODO: Test
        """
    
        # Perform linear regression
        slope, intercept, r, p, std_err = stats.linregress(X, Y)
        
        # Find the zero field voltage
        zero = -1*intercept/slope
        
        # Return values
        values = [slope, intercept, zero, r]
            
        return values
        
    def write_calibration_file(self):
        """
        Write calibration data to a csv file.
        
        TODO: Test
        """
        
        content = []
        row1 = ["axis",
                "slope",
                "intercept",
                "zero",
                "r_value", 
                "resistance"]
                
        # Fill data for each row
        row2 = ["x",
                self.x_slope,
                self.x_intercept,
                self.x_zero,
                self.x_r,
                self.x_resist]
        row3 = ["y",
                self.y_slope,
                self.y_intercept,
                self.y_zero,
                self.y_r,
                self.y_resist]
        row4 = ["z",
                self.z_slope,
                self.z_intercept,
                self.z_zero,
                self.z_r,
                self.z_resist]
                
        # Put into content list
        content = [row1, row2, row3, row4]
        
        # Write to csv file        
        write_to_csv(self.calibration_dir, self.filename, content, 'w')        
    
    def load_calibration_file(self):
        """
        Load an existing cage calibration from a file of the correct
        format.
        
        TODO: Test
        """
        
        # Read in values from file
        content = read_from_csv(self.calibration_dir, self.filename)
        
        # Parse data into class variables
        for row in content:
            if str(row[0])=="x":
                self.x_slope = float(row[1])
                self.x_intercept = float(row[2])
                self.x_zero = float(row[3])
                self.x_r = float(row[4])
                self.x_resist = float(row[5])
            if str(row[0])=="y":
                self.y_slope = float(row[1])
                self.y_intercept = float(row[2])
                self.y_zero = float(row[3])
                self.y_r = float(row[4])
                self.y_resist = float(row[5])
            if str(row[0])=="z":
                self.z_slope = float(row[1])
                self.z_intercept = float(row[2])
                self.z_zero = float(row[3])
                self.z_r = float(row[4])
                self.z_resist = float(row[5])
            else:
                pass
