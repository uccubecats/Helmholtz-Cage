"""
Objects and functions for calibrating the Helmholtz Cage.

Copyright 2024 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import os

import scipy

from utilities.files import read_from_csv, write_to_csv


class LineEqn(object):
    """
    An object to hold a linear equation.
    """
    
    def __init__(self, slope, intercept, r_value):
    
        # Store main parameters of equations
        self.slope = float(slope)
        self.intercept = float(intercept)
        self.r_value = float(r_value)
        
        # Calculate x-intercept from equation
        self.zero = -1*self.intercept/self.slope
        
    def __str__(self):
        return "y = {}*x + {} | r-value: {}".format(self.slope, self.intercept,
                                                    self.r_value)
    
    def solve_for_x(self, y):
        """
        Solve the linear equation for x.
        """
        return (y - self.intercept)/self.slope
        
    def solve_for_y(self, x):
        """
        solve the linear equation for y.
        """
        return self.slope*x - self.intercept


class Calibration(object):
    """
    Helmholtz Cage calibration object.
    """
    
    def __init__(self, file_dir, file_name):
        
        # Filename and directory
        self.file_name = file_name
        self.file_dir = file_dir
        
        # Initialize calibration variables
        self.calibration_log_file = ""
        self.x_equations = {}
        self.y_equations = {}
        self.z_equations = {}
        self.Rx = -1.0
        self.Ry = -1.0
        self.Rz = -1.0
    
    def from_data(self, data):
        """
        Given a calibration data set, get relevant calibration data from
        each single-axis coil pair using linear regressions.
        
        TODO: Test
        """
        
        x_points = []
        y_points = []
        z_points = []
        
        # Determine which axis calibration data points belong to
        for i in range(0,len(data.time)):
            if data.x_req[i] == 0.0 and data.y_req[i] == 0.0 and data.z_req[i] == 0.0:
                pass
            elif data.x_req[i] != 0.0:
                x_points.append(i)
            elif data.y_req[i] != 0.0:
                y_points.append(i)
            elif data.z_req[i] != 0.0:
                z_points.append(i)
        
        # Package each axis points into new data object
        x_data = data.retrieve_data_subset(x_points)
        y_data = data.retrieve_data_subset(y_points)
        z_data = data.retrieve_data_subset(z_points)
        
        # Determine equations for each axis as well as influence on other axes
        xx_equation = self.perform_linear_regression(x_data.Vx, x_data.Bx)
        xy_equation = self.perform_linear_regression(x_data.Vx, x_data.By)
        xz_equation = self.perform_linear_regression(x_data.Vx, x_data.Bz)
        yx_equation = self.perform_linear_regression(y_data.Vy, y_data.Bx)
        yy_equation = self.perform_linear_regression(y_data.Vy, y_data.By)
        yz_equation = self.perform_linear_regression(y_data.Vy, y_data.Bz)
        zx_equation = self.perform_linear_regression(z_data.Vz, z_data.Bx)
        zy_equation = self.perform_linear_regression(z_data.Vz, z_data.By)
        zz_equation = self.perform_linear_regression(z_data.Vz, z_data.Bz)
        
        # package Equations
        self.x_equations = {"x": xx_equation,
                            "y": xy_equation,
                            "z": xz_equation}
        self.y_equations = {"x": yx_equation,
                            "y": yy_equation,
                            "z": yz_equation}
        self.z_equations = {"x": zx_equation,
                            "y": zy_equation,
                            "z": zz_equation}
        
        # Determine resistance
        x_iv = self.perform_linear_regression(x_data.Ix, x_data.Vx)
        y_iv = self.perform_linear_regression(y_data.Iy, y_data.Vy)
        z_iv = self.perform_linear_regression(z_data.Iz, z_data.Vz)
        self.Rx = x_iv.slope
        self.Ry = y_iv.slope
        self.Rz = z_iv.slope
        
    def perform_linear_regression(self, X, Y):
        """
        Determine a linear regression of a data set, including a slope,
        x- and y-intercepts, and r-value.
        """
        
        # Perform linear regression
        result = scipy.stats.linregress(X, Y)
        
        # Package result into equation object
        equation = LineEqn(result.slope, result.intercept, result.rvalue)
              
        return equation
        
    def write_to_file(self):
        """
        Write calibration data to a csv file.
        
        TODO: Test
        """
        
        # Create lables
        labels = [["coil",
                   "measured axis",
                   "slope",
                   "intercept",
                   "zero",
                   "r_value",
                   "resistance"]]
        
        # Package equations for each axis
        x_rows = self.package_axis_equations("x", self.x_equations)
        y_rows = self.package_axis_equations("y", self.y_equations)
        z_rows = self.package_axis_equations("z", self.z_equations)
        
        # Package coil resistance data
        x_rows[0].append(self.Rx)
        y_rows[1].append(self.Ry)
        z_rows[2].append(self.Rz)
                
        # Pull contents together
        content = labels + x_rows + y_rows + z_rows
        
        # Write to csv file
        write_to_csv(self.file_dir, self.file_name, content, 'w')     
        
    def package_axis_equations(self, axis, equations):
        """
        Package important parameters of each equation for a certain axis
        coil pair.
        """
        
        content = []
        for key,value in equations.items():
            content.append([axis,
                            key,
                            value.slope,
                            value.intercept,
                            value.zero,
                            value.r_value])
                            
        return content
    
    def load_from_file(self):
        """
        Load an existing cage calibration from a file of the correct
        format.
        """
        
        success = True #TODO: catch failures
        
        # Read in values from file
        content = read_from_csv(self.file_dir, self.file_name)
        
        # Parse data into equation holding objects
        xx_equation = LineEqn(content[1][2], content[1][3], content[1][5])
        xy_equation = LineEqn(content[2][2], content[2][3], content[2][5])
        xz_equation = LineEqn(content[3][2], content[3][3], content[3][5])
        yx_equation = LineEqn(content[4][2], content[4][3], content[4][5])
        yy_equation = LineEqn(content[5][2], content[5][3], content[5][5])
        yz_equation = LineEqn(content[6][2], content[6][3], content[6][5])
        zx_equation = LineEqn(content[7][2], content[7][3], content[7][5])
        zy_equation = LineEqn(content[8][2], content[8][3], content[8][5])
        zz_equation = LineEqn(content[9][2], content[9][3], content[9][5])
        #TODO: Handle failure to find some of these values?
        
        # Store equations
        self.x_equations = {"x": xx_equation,
                            "y": xy_equation,
                            "z": xz_equation}
        self.y_equations = {"x": yx_equation,
                            "y": yy_equation,
                            "z": yz_equation}
        self.z_equations = {"x": zx_equation,
                            "y": zy_equation,
                            "z": zz_equation}
        
        # Store resistance values
        self.Rx = content[1][6]
        self.Ry = content[5][6]
        self.Rz = content[9][6]
        
        return success
