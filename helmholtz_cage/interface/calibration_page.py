#!/usr/bin/env python3

"""
  Calibration GUI source code
  
  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


# Global constants
MAX_FIELD = 1.5 # Gauss
MAX_VOLTAGE = 18 # Volts
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 9)


class CalibrationPage(tk.Frame):
    """
    A Tkinter Frame object class which displays the results of a
    calibration run to the user and allows for accept/reject of the
    results
    """
    
    def __init__(self, controller, calibration, data):
        
        # Create popup window
        self.popup = tk.Tk()
        self.popup.wm_title("Calibration Results")
        
        # Add controller to access parent CageApp class
        self.controller = controller
        
        # Setup main container frame
        self.container = tk.Frame(self.popup)
        self.container.pack()
        
        # Extract relevant calibration and run data
        x_equations = calibration.x_equations
        y_equations = calibration.y_equations
        z_equations = calibration.z_equations
        x_data = self.extract_axis_data_points("x", data)
        y_data = self.extract_axis_data_points("y", data)
        z_data = self.extract_axis_data_points("z", data)
        
        # Create subframes
        self.x_data_frame = tk.Frame(self.container,
                                     bg="lightgray", 
                                     highlightbackground="silver",
                                     highlightcolor="silver",
                                     highlightthickness=2)
        
        self.y_data_frame = tk.Frame(self.container,
                                     bg="lightgray", 
                                     highlightbackground="silver",
                                     highlightcolor="silver",
                                     highlightthickness=2)
        
        self.z_data_frame = tk.Frame(self.container,
                                     bg="lightgray", 
                                     highlightbackground="silver",
                                     highlightcolor="silver",
                                     highlightthickness=2)
        
        self.exit_options_frame = tk.Frame(self.container,
                                           bg="lightgray",
                                           highlightbackground="silver",
                                           highlightcolor="silver",
                                           highlightthickness=2)
        
        # Position subframes
        self.x_data_frame.grid(row=1, column=0, sticky="nsew")
        self.y_data_frame.grid(row=1, column=1, sticky="nsew")
        self.z_data_frame.grid(row=1, column=2, sticky="nsew")
        self.exit_options_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
        
        # Fill subframes using method calls
        self.fill_axis_data_display(self.x_data_frame, "x", x_equations, x_data)
        self.fill_axis_data_display(self.y_data_frame, "y", y_equations, y_data)
        self.fill_axis_data_display(self.z_data_frame, "z", z_equations, z_data)
        self.fill_exit_options_frame()
    
    def extract_axis_data_points(self, axis, data):
        """
        Extract the relevant calibration data points for a particular
        axis.
        """
        
        V = []
        Bx = []
        By = []
        Bz = []
        
        # Determine which axis calibration data points belong to
        for i in range(0,len(data.time)):
            if axis == "x" and data.x_req[i] != 0.0:
                V.append(data.Vx[i])
                Bx.append(data.Bx[i])
                By.append(data.By[i])
                Bz.append(data.Bz[i])
            elif axis == "y" and data.y_req[i] != 0.0:
                V.append(data.Vy[i])
                Bx.append(data.Bx[i])
                By.append(data.By[i])
                Bz.append(data.Bz[i])
            elif axis == "z" and data.z_req[i] != 0.0:
                V.append(data.Vz[i])
                Bx.append(data.Bx[i])
                By.append(data.By[i])
                Bz.append(data.Bz[i])
        
        return [V, Bx, By, Bz]
    
    def fill_axis_data_display(self, axis_frame, axis, equations, data):
        """
        Fill in an individual axis data frame.
        """
        
        # Create labels
        title = "{}-Axis Regression".format(axis.upper())
        title_label = tk.Label(axis_frame, 
                               text=title,
                               font=LARGE_FONT,
                               bg="lightgray")
        
        equation_label = tk.Label(axis_frame,
                                  text="Equations",
                                  bg="lightgray")
        
        R_label = tk.Label(axis_frame,
                           text="R-Value",
                           bg="lightgray")
                           
        fake_lable = tk.Label(axis_frame,
                              text="",
                              bg="lightgray")
        
        # Create calibration equation entries
        x_equation_entry = tk.Entry(axis_frame,
                                    width=30,
                                    state=tk.NORMAL)
        
        y_equation_entry = tk.Entry(axis_frame,
                                    width=30,
                                    state=tk.NORMAL)
        
        z_equation_entry = tk.Entry(axis_frame,
                                    width=30,
                                    state=tk.NORMAL)
        
        xR_entry = tk.Entry(axis_frame,
                            width=10,
                            state=tk.NORMAL)
        
        yR_entry = tk.Entry(axis_frame,
                            width=10,
                            state=tk.NORMAL)
        
        zR_entry = tk.Entry(axis_frame,
                            width=10,
                            state=tk.NORMAL)
                            
        # Create plot holding subframe
        data_frame = tk.Frame(axis_frame)
        
        # Position widgets and subframes
        title_label.grid(row=0, column=0, columnspan=2, pady=5, sticky="nsew")
        equation_label.grid(row=1, column=0, columnspan=1, sticky="nsew")
        R_label.grid(row=1, column=1, sticky="nsew")
        x_equation_entry.grid(row=2, column=0, columnspan=1, sticky="nsew")
        xR_entry.grid(row=2, column=1, sticky="nsew")
        y_equation_entry.grid(row=3, column=0, columnspan=1, sticky="nsew")
        yR_entry.grid(row=3, column=1, sticky="nsew")
        z_equation_entry.grid(row=4, column=0, columnspan=1, sticky="nsew")
        zR_entry.grid(row=4, column=1, sticky="nsew")
        data_frame.grid(row=7, column=0, columnspan=2, sticky="nsew")
        
        # Fill calibration equation entries
        x_equation, xR_value = self.format_equation_string(axis, "x", equations)
        x_equation_entry.insert(0, x_equation)
        x_equation_entry.configure(state="readonly")
        xR_entry.insert(0, xR_value)
        xR_entry.configure(state="readonly")
        
        y_equation, yR_value = self.format_equation_string(axis, "y", equations)
        y_equation_entry.insert(0, y_equation)
        y_equation_entry.configure(state="readonly")
        yR_entry.insert(0, yR_value)
        yR_entry.configure(state="readonly")
        
        z_equation, zR_value = self.format_equation_string(axis, "z", equations)
        z_equation_entry.insert(0, z_equation)
        z_equation_entry.configure(state="readonly")
        zR_entry.insert(0, zR_value)
        zR_entry.configure(state="readonly")
        
        # Fill data plot frame
        fig = self.create_axis_data_plot(axis, data, equations)
        canvas = FigureCanvasTkAgg(fig, master=data_frame)
        canvas.get_tk_widget().grid()
        canvas.draw()
        
        return axis_frame
    
    def format_equation_string(self, ctrl_axis, meas_axis, equations):
        """
        For the given calibration function, format the B-V equation and 
        R-value for display in GUI.
        """
        
        # Retrieve relevant equation.
        equation = equations[meas_axis]
        
        # Format equation coefficients and R-value as strings
        slope_str = "%.6f" % (equation.slope)
        intercept_str = "%.6f" % (equation.intercept)
        r_value_str = "%.6f" % (equation.r_value)
        
        # Place equation components into formated string
        equation_str = "B{} = {}*V{} + {}".format(meas_axis,
                                                  slope_str,
                                                  ctrl_axis,
                                                  intercept_str)
        
        return equation_str, r_value_str
        
    def create_axis_data_plot(self, axis, data, equations):
        """
        Create a plot displaying the calibarion equations for the given 
        axis.
        
        TODO: Plot raw data along side calibration functions
        """
        
        # Specify data for display of calibration functions
        x = [0, MAX_VOLTAGE]
        yx = [equations["x"].intercept,
              equations["x"].slope*MAX_VOLTAGE + equations["x"].intercept]
        yy = [equations["y"].intercept,
              equations["y"].slope*MAX_VOLTAGE + equations["y"].intercept]
        yz = [equations["z"].intercept,
              equations["z"].slope*MAX_VOLTAGE + equations["z"].intercept]
        
        # Create plot
        fig = Figure(figsize = (4,4), facecolor="lightgray")
        ax = fig.add_subplot(111)
        
        # Put data into plot
        ax.scatter(data[0], data[1], c="r")
        ax.scatter(data[0], data[2], c="g")
        ax.scatter(data[0], data[3], c="b")
        ax.plot(x, yx, "r", label="Bx")
        ax.plot(x, yy, "g", label="By")
        ax.plot(x, yz, "b", label="Bz")
        
        # Configure plot display options
        ax.set_xlim(-1*MAX_VOLTAGE, MAX_VOLTAGE)
        ax.set_ylim(-1*MAX_FIELD, MAX_FIELD)
        ax.set_title("B vs V{}".format(axis))
        ax.legend()
        
        return fig

    def fill_exit_options_frame(self):
        """
        Fill the calibration exit options (whether to accept or reject
        calibration).
        """
        
        # Create labels
        options_label = tk.Label(self.exit_options_frame,
                                width=20,
                                text="Accept Calibration?",
                                bg="lightgray")
        
        # Create 'margins' (to position exit option widgets)
        margin_label = tk.Label(self.exit_options_frame,
                                text=" ",
                                width=50,
                                bg="lightgray")
                                
        margin_label_2 = tk.Label(self.exit_options_frame,
                                  text=" ",
                                  width=50,
                                  bg="lightgray")
        
        # Create buttons
        accept_button = tk.Button(self.exit_options_frame,
                                  text="Accept",
                                  width=10,
                                  command=lambda: self.accept_calibration())
        
        reject_button = tk.Button(self.exit_options_frame,
                                  text="Reject",
                                  width=10,
                                  command=lambda: self.reject_calibration())
                                  
        # Position widgets
        margin_label.grid(row=0, column=0, sticky="nw")
        options_label.grid(row=0, column=1, sticky="nsew")
        accept_button.grid(row=0, column=2, sticky="nsew")
        reject_button.grid(row=0, column=3, sticky="nsew")
        margin_label_2.grid(row=0, column=4, sticky="ne")
    
    def accept_calibration(self):
        """
        A method to configure the cage to accept the displayed
        calibration.
        """
        
        self.controller.handle_calibration_output(True)
        self.popup.destroy()
    
    def reject_calibration(self):
        """
        A method to configure the cage to reject the displayed
        calibration.
        """
        
        self.controller.handle_calibration_output(False)
        self.popup.destroy()
