#!/usr/bin/env python

"""
  Main GUI code for the UC Helmholtz Cage

  Copyright 2018-2022 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import tkinter as tk


# Global constants
MAX_FIELD_VALUE = 20
MAX_VOLTAGE_VALUE = 20
UPDATE_PLOT_TIME = 1  # secs
UPDATE_LOG_TIME = 5  # secs
UPDATE_CALIBRATE_TIME = 5  # secs
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 9)


class ConfigurationPage(tk.Frame):
    """
    
    """
    
    def __init__(self, controller):
        
        # Create popup window
        popup = tk.Tk()
        popup.wm_title("Configuration Options")
        
        # Add controller to access parent CageApp class
        self.controller = controller
        
        # Create container for all the subframes on the GUI
        container = tk.Frame(popup, bg='silver')
        container.grid(sticky='nsew')
        
        # Create subframes for main frame
        self.port_frame = tk.Frame(container,
                                   bg='lightgray',
                                   height=50,
                                   highlightbackground='silver',
                                   highlightcolor='silver',
                                   highlightthickness=2)
        
        # Position subframes
        self.port_frame.grid(row=1, sticky='nsew')
        
        # Fill in the subframes (function calls)
        self.fill_port_frame()
        
        # Start Popup
        popup.mainloop()
        
    def fill_port_frame(self):
        """
        Fill in the connections subframe.
        """
        
        # Create Tk entry variable
        self.x_ps_port_name = tk.StringVar()
        self.y_ps_port_name = tk.StringVar()
        self.z_ps_port_name = tk.StringVar()
        self.mag_port_name = tk.StringVar()
        
        # Create labels
        self.port_title = tk.Label(self.port_frame,
                                   text="Instrument Ports",
                                   font=LARGE_FONT,
                                   bg='lightgray')
                                   
        self.x_ps_port_label = tk.Label(self.port_frame,
                                        text="X Power Supply",
                                        bg='lightgray',
                                        width=14)
                                        
        self.y_ps_port_label = tk.Label(self.port_frame,
                                        text="Y Power Supply",
                                        bg='lightgray',
                                        width=14)
        
        self.z_ps_port_label = tk.Label(self.port_frame,
                                        text="Z Power Supply",
                                        bg='lightgray',
                                        width=14)
        
        self.mag_port_label = tk.Label(self.port_frame,
                                       text="Magnetometer",
                                       bg='lightgray',
                                       width=14)
        
        # Create value entries
        self.x_ps_port_entry = tk.Entry(self.port_frame,
                                        textvariable=self.x_ps_port_name,
                                        width=22)
        
        self.y_ps_port_entry = tk.Entry(self.port_frame,
                                        textvariable=self.y_ps_port_name,
                                        width=22)
        
        self.z_ps_port_entry = tk.Entry(self.port_frame,
                                        textvariable=self.z_ps_port_name,
                                        width=22)
        
        self.mag_port_entry = tk.Entry(self.port_frame,
                                        textvariable=self.mag_port_name,
                                        width=22)
        
        # Postiton widgets                                
        self.port_title.grid(row=0, column=0, columnspan=2, pady=5, sticky='nsew')
        self.x_ps_port_label.grid(row=1, column=0)
        self.x_ps_port_entry.grid(row=1, column=1)
        self.y_ps_port_label.grid(row=2, column=0)
        self.y_ps_port_entry.grid(row=2, column=1)
        self.z_ps_port_label.grid(row=3, column=0)
        self.z_ps_port_entry.grid(row=3, column=1)
        self.mag_port_label.grid(row=4, column=0)
        self.mag_port_entry.grid(row=4, column=1)
