#!/usr/bin/env python

"""
A group of functions for calibrating the Helmholtz Cage
https://pythonprogramming.net/tkinter-popup-message-window/

Copyright 2018-2019 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.
"""


import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from scipy import stats


# Global constants
MEDIUM_FONT= ("Verdana", 9)
LARGE_FONT = ("Verdana", 12)
REGRESS_REJECTED = False

def calibration_results_popup(x_data, y_data, z_data):
    """
    Perform linear regressions on the data and populate a calibration results
    popup frame. 
    """
    # Ensure the "Regression Rejected" flag variable is reset
    global REGRESS_REJECTED 
    REGRESS_REJECTED = False
    
    # Create popup window
    popup = tk.Tk()
    popup.wm_title("Calibration Results")
        
    # Perform X-Coil linear regression
    x_equations = perform_linear_regression(x_data)
    
    # Create X-Coil regression analysis frame
    x_regression_frame = tk.Frame(popup, bg="lightgray", highlightbackground="silver",
                                    highlightthickness=2)
    create_axis_regression_display(x_regression_frame, "X", x_equations)
    x_regression_frame.grid(row=1, column=1, sticky="nsew")
    
    # Perform Y-Coil linear regression
    y_equations = perform_linear_regression(y_data)
    
    # Create Y-Coil regression analysis frame
    y_regression_frame = tk.Frame(popup, bg="lightgray", highlightbackground="silver",
                                    highlightthickness=2)
    create_axis_regression_display(y_regression_frame, "Y", y_equations)
    y_regression_frame.grid(row=1, column=2, sticky="nsew")
    
    # Perform Z-Coil linear regression
    z_equations = perform_linear_regression(z_data)
    
    # Create Z-Coil regression analysis frame
    z_regression_frame = tk.Frame(popup, bg="lightgray", highlightbackground="silver",
                                    highlightthickness=2)
    create_axis_regression_display(z_regression_frame, "Z", z_equations)
    z_regression_frame.grid(row=1, column=3, sticky="nsew")
    
    # Display X-Coil data
    x_data_frame = tk.Frame(x_regression_frame, bg="lightgray")
    x_data_frame.grid(row=5, column=0, sticky="nsew", columnspan=3)
    x_fig = create_calibration_subplots(x_data, 'r', x_equations[0], x_equations[1])
    canvas = FigureCanvasTkAgg(x_fig, master=x_data_frame)
    canvas.get_tk_widget().grid()
    canvas.draw()
    
    # Create Y-Coil data
    y_data_frame = tk.Frame(y_regression_frame, bg="lightgray")
    y_data_frame.grid(row=5, column=0, sticky="nsew", columnspan=3)
    y_fig = create_calibration_subplots(y_data, 'g', y_equations[3], y_equations[4])
    canvas2 = FigureCanvasTkAgg(y_fig, master=y_data_frame)
    canvas2.get_tk_widget().grid()
    canvas2.draw()
    
    # Create Z-Coil data
    z_data_frame = tk.Frame(z_regression_frame, bg="lightgray")
    z_data_frame.grid(row=5, column=0, sticky="nsew", columnspan=3)
    z_fig = create_calibration_subplots(z_data, 'b', z_equations[6], z_equations[7])
    canvas3 = FigureCanvasTkAgg(z_fig, master=z_data_frame)
    canvas3.get_tk_widget().grid(row=2, column=3)
    canvas3.draw()
    
    # Needs to be a nested function in order to be read by buttons
    def reject_regression():
        global REGRESS_REJECTED
        REGRESS_REJECTED = True
        popup.quit()
    
    # Create Exit Options Frame
    exit_option_frame = tk.Frame(popup, bg="lightgray", highlightbackground="silver",
                                  highlightthickness=2)
    exit_option_frame.grid(row=2, column=1, sticky="nsew", columnspan=3)
    accept_act = tk.Button(exit_option_frame, text='Accept', command=popup.quit)
    accept_act.grid(row=0, column=0, sticky="se")
    cancel_act = tk.Button(exit_option_frame, text='Reject', command=lambda: reject_regression())
    cancel_act.grid(row=0, column=1, sticky="se")
    
    # Start Popup
    popup.mainloop()
    
    # Handle results accepted vs results rejected
    popup.destroy()
    if REGRESS_REJECTED:
        return None, None, None
    else:
        return x_equations, y_equations, z_equations
        

def create_axis_regression_display(regression_display, axis, equations):
    """
    Populate the linear regression data subframes.
    """
    # Create Frame Title
    title = "{}-Axis Coil Regression".format(axis)
    regression_label = tk.Label(regression_display, text=title, font=LARGE_FONT, 
                            bg="lightgray")
    regression_label.grid(row=0, column=0, columnspan=3, pady=5, sticky='nsew')
    
    # Top Labels
    equation_label = tk.Label(regression_display, text="Equation", 
                              font=MEDIUM_FONT, bg="lightgray")
    equation_label.grid(row=1, column=1)
    
    R_label = tk.Label(regression_display, text="R-squared", 
                       font=MEDIUM_FONT, bg="lightgray")
    R_label.grid(row=1, column=2)
    
    # X-Axis Information
    x_equation_label = tk.Label(regression_display, text=" X: ", 
                                font=MEDIUM_FONT, bg="lightgray")
    x_equation_label.grid(row=2, column=0)
    
    x_equation_entry = tk.Entry(regression_display, width=28)
    x_equation_entry.grid(row=2, column=1)
    x_equation_entry.insert(tk.END, "B = %.7f*V + (%.7f)" % (equations[0], equations[1]))
    
    xR_value_entry = tk.Entry(regression_display, width=10)
    xR_value_entry.grid(row=2, column=2)
    xR_value_entry.insert(tk.END, "%.7f" % equations[2])
    
    # Y-Axis Information
    y_equation_label = tk.Label(regression_display, text=" Y: ",
                                font=MEDIUM_FONT, bg="lightgray")
    y_equation_label.grid(row=3, column=0)
    
    y_equation_entry = tk.Entry(regression_display, width=28)
    y_equation_entry.grid(row=3, column=1)
    y_equation_entry.insert(tk.END, "B = %.7f*V + (%.7f)" % (equations[3], equations[4]))
    
    yR_value_entry = tk.Entry(regression_display, width=10)
    yR_value_entry.grid(row=3, column=2)
    yR_value_entry.insert(tk.END, "%.7f" % equations[5])
    
    # Z-Axis Information
    z_equation_label = tk.Label(regression_display, text=" Z: ", 
                                font=MEDIUM_FONT, bg="lightgray")
    z_equation_label.grid(row=4, column=0)
    
    z_equation_entry = tk.Entry(regression_display, width=28)
    z_equation_entry.grid(row=4, column=1)
    z_equation_entry.insert(tk.END, "B = %.7f*V + (%.7f)" % (equations[6], equations[7]))
    
    zR_value_entry = tk.Entry(regression_display, width=10)
    zR_value_entry.grid(row=4, column=2)    
    zR_value_entry.insert(tk.END, "%.7f" % equations[8])
    
def create_calibration_subplots(data, color, slope, intercept):
    """
    Create matplotlib Figures to display the linear regression results
    """
    
    # Trend line generation (may replace with equation that detemines data range)
    x = np.linspace(0.0,8.0,num=100)
    y = slope*x + intercept

    # Create a matplotlib figure
    fig = Figure(figsize=(4,4), dpi=100, facecolor='lightgray')
    a = fig.add_subplot(111)
    
    # Add data to figure
    a.plot(data[0], data[2], 'ro', label='X')
    a.plot(data[0], data[3], 'go', label='Y')
    a.plot(data[0], data[4], 'bo', label='Z')
    a.plot(x, y, color, label="Fit Line")
    
    return fig
    
def parse_data(data, cutoff_x, cutoff_y):
    """
    Parse the calibration data into separate lists that can be plotted
    """
    
    # Slice the data based on cutoffs
    x_coil_series = [data.x_out[:cutoff_x],
                     data.x_req[:cutoff_x],
                     data.x_mag_field_actual[:cutoff_x],
                     data.y_mag_field_actual[:cutoff_x],
                     data.z_mag_field_actual[:cutoff_x]]
                     
    y_coil_series = [data.y_out[cutoff_x+1:cutoff_y], 
                     data.y_req[cutoff_x+1:cutoff_y],
                     data.x_mag_field_actual[cutoff_x+1:cutoff_y],
                     data.y_mag_field_actual[cutoff_x+1:cutoff_y],
                     data.z_mag_field_actual[cutoff_x+1:cutoff_y]]
                     
    z_coil_series = [data.z_out[cutoff_y+1:], 
                     data.z_req[cutoff_y+1:],
                     data.x_mag_field_actual[cutoff_y+1:],
                     data.y_mag_field_actual[cutoff_y+1:],
                     data.z_mag_field_actual[cutoff_y+1:]]
                     
    return [x_coil_series, y_coil_series, z_coil_series];
    
def perform_linear_regression(data):
    """
    Determine a linear regression of all three magnetic axes for an individual 
    Helmholtz Coil.
    """
    lin_equations = []
    
    # Run through each axis and store the relevant equation information
    for i in range(0,3):
        slope, intercept, r_value, p_value, std_err = stats.linregress(data[0], data[2+i])
        lin_equations.append(slope)
        lin_equations.append(intercept)
        lin_equations.append(r_value)
        
    return lin_equations
