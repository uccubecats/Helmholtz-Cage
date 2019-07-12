#!/usr/bin/env python

"""
Main GUI script for the UC Helmholtz Cage

Copyright 2018-2019 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.

Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import csv
import datetime
import glob
import logging
import os
from os import listdir
from os.path import isfile, join
import threading
from tkinter import filedialog
import tkinter as tk
import traceback

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from instruments import *
from session import *


# Setup logging
logging.getLogger("visa").setLevel(logging.WARNING)
logger = logging.getLogger("main.py")
logging.basicConfig(filename='helmholtz-gui.log', level=logging.DEBUG)

# Global constants
MAX_FIELD_VALUE = 20
MAX_VOLTAGE_VALUE = 20
UPDATE_PLOT_TIME = 1  # secs
UPDATE_LOG_TIME = 5  # secs
UPDATE_CALIBRATE_TIME = 5  # secs
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 9)


class Data:
    """
    An object class for storing data from an open file.
    """
    
    def __init__(self):

        # Plot data
        self.plots_created = False # flag variable so plots are only created once
        self.plot_titles = "" # flag variable so titles are only added the first time data is logged

        # Button data
        self.cage_on = False
        self.cage_calibrating = False
        self.cage_in_dynamic = False

        # Template data
        self.template_file = "none found"
        self.template_voltages_x = []
        self.template_voltages_y = []
        self.template_voltages_z = []

        # Calibration data (used when creation a new calibration file from template file)
        self.calibrating_now = False
        self.stop_calibration = False
        self.calibration_log_filename = ""
        self.calibration_file = "none found"
        self.calibration_time = []# not needed for anything but good to keep track of
        self.calibration_voltages_x = [] # Voltages used to get a magnetic field
        self.calibration_voltages_y = []
        self.calibration_voltages_z = []
        self.calibration_mag_field_x = [] # Magnetic fields obtained by the (x,y,z) voltages
        self.calibration_mag_field_y = []
        self.calibration_mag_field_z = []
        self.current_value = 0

        # Session logging data
        self.session_log_filename = ""
        self.start_time = None
        self.time = []
        self.x_req, self.y_req, self.z_req = [], [], []
        self.x_out, self.y_out, self.z_out = [], [], []
        self.x_mag_field_actual = []
        self.y_mag_field_actual = []
        self.z_mag_field_actual = []
        self.x_mag_field_requested = []
        self.y_mag_field_requested = []
        self.z_mag_field_requested = []

        self.active_x_voltage_requested = 0
        self.active_y_voltage_requested = 0
        self.active_z_voltage_requested = 0
        self.active_x_mag_field_requested = 0
        self.active_y_mag_field_requested = 0
        self.active_z_mag_field_requested = 0


class CageApp(tk.Tk):
    """
    An object class for main Helmholtz Cage application.
    """
    
    def __init__(self, *args, **kwargs):
        
        # Initialize frame
        tk.Tk.__init__(self, *args, **kwargs)

        # Add title info
        self.title = "Helmholtz Cage"
        tk.Tk.wm_title(self, self.title)
        # tk.Tk.iconbitmap(self, default="icon.ico") #*** add ico file for cage

        # Expand frame to window
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Frames are laid ontop of each other, startPage shown first
        self.frames = {}
        for Frame in (MainPage, HelpPage):
            frame = Frame(container, self)
            self.frames[Frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        self.show_frame(MainPage)

    def show_frame(self, cont):
        """
        Function to switch frames.
        """
        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tk.Frame):
    """
    An object class for main frame of the Helmholtz Cage application.
    """
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)

        # Controller allows MainPage to access things from CageApp class
        self.controller = controller

        # Create container for all the subframes on the GUI
        container = tk.Frame(self, bg="silver")
        container.grid(sticky="nsew")

        # Create subframes for main frame
        self.title_frame = tk.Frame(container, bg="lightgray", 
                                    height=50,
                                    highlightbackground="silver",
                                    highlightthickness=2)
        self.connections_frame = tk.Frame(container, bg="lightgray",
                                          height=50,
                                          highlightbackground="silver",
                                          highlightthickness=2)
        self.calibrate_frame = tk.Frame(container, bg="lightgray",
                                        height=50,
                                        highlightbackground="silver",
                                        highlightthickness=2)
        self.static_buttons_frame = tk.Frame(container, bg="lightgray",
                                             height=50,
                                             highlightbackground="silver",
                                             highlightthickness=2)
        self.dynamic_buttons_frame = tk.Frame(container, bg="lightgray",
                                              height=50,
                                              highlightbackground="silver",
                                              highlightthickness=2)
        self.main_buttons_frame = tk.Frame(container, bg="lightgray",
                                           height=50,
                                           highlightbackground="silver",
                                           highlightthickness=2)
        self.help_frame = tk.Frame(container, bg="lightgray",
                                   height=50,
                                   highlightbackground="silver",
                                   highlightthickness=2)
        self.plots_frame = tk.Frame(container, bg="lightgray",
                                    width=500,
                                    highlightbackground="silver",
                                    highlightthickness=4)

        # Position subframes
        self.title_frame.grid(row=0, sticky="ew")
        self.connections_frame.grid(row=1, sticky="nsew")
        self.calibrate_frame.grid(row=2, sticky="nsew")
        self.static_buttons_frame.grid(row=3, sticky="nsew")
        self.dynamic_buttons_frame.grid(row=4, sticky="nsew")
        self.main_buttons_frame.grid(row=5, sticky="nsew")
        self.help_frame.grid(row=6, sticky="nsew")
        self.plots_frame.grid(row=0, column=1, sticky="nsew", rowspan=7)

        # Set weight for expansion
        [container.rowconfigure(r, weight=1) for r in range(1, 5)]
        container.columnconfigure(1, weight=1)

        # Initialize class attributes
        self.connections_label = None
        self.unit_label = None
        self.status_label = None
        self.x_ps_status = None
        self.x_ps_label = None
        self.x_ps_status_entry = None
        self.y_ps_status = None
        self.y_ps_label = None
        self.y_ps_status_entry = None
        self.z_ps_status = None
        self.z_ps_label = None
        self.z_ps_status_entry = None
        self.mag_status = None
        self.mag_label = None
        self.mag_status_entry = None
        self.refresh_connections_button = None
        self.label_title = None
        self.calibration_label = None
        self.template_file_label = None
        self.template_file_status_text = None
        self.template_file_entry = None
        self.change_template_file_button = None
        self.calibration_file_label = None
        self.calibration_file_status_text = None
        self.calibration_file_entry = None
        self.change_calibration_file_button = None
        self.calibrate_button = None
        self.static_or_dynamic = None
        self.select_static = None
        self.field_or_voltage = None
        self.select_field = None
        self.select_voltage = None
        self.x_field_label = None
        self.x_field = None
        self.x_field_entry = None
        self.x_voltage_label = None
        self.x_voltage = None
        self.x_voltage_entry = None
        self.y_field_label = None
        self.y_field = None
        self.y_field_entry = None
        self.y_voltage_label = None
        self.y_voltage = None
        self.y_voltage_entry = None
        self.z_field_label = None
        self.z_field = None
        self.z_field_entry = None
        self.z_voltage_label = None
        self.z_voltage = None
        self.z_voltage_entry = None
        self.select_dynamic = None
        self.open_dynamic_csv_button = None
        self.start_button = None
        self.stop_button = None
        self.fig = None
        self.power_supplies_plot = None
        self.mag_field_plot = None
        self.power_supplies_plot = None
        self.canvas = None

        # Fill in the subframes (function calls)
        #self.fill_title_frame()
        self.fill_calibrate_frame()
        self.fill_connections_frame()
        self.fill_static_buttons_frame(parent)
        self.fill_dynamic_buttons_frame()
        self.fill_main_buttons_frame()
        self.fill_help_frame()
        self.fill_plot_frame()

    def fill_title_frame(self):
        """
        Fill in the title subframe.
        """
        self.label_title = tk.Label(self.title_frame, text="Helmholtz Cage",
                                    font=LARGE_FONT)
        self.label_title.grid(row=0, column=0)

    def fill_connections_frame(self):
        """
        Fill in connections subframe.
        """
        
        # Title bars
        self.connections_label = tk.Label(self.connections_frame,
                                          text="Connections", font=LARGE_FONT,
                                          bg="lightgray")
        self.connections_label.grid(row=0, column=0, columnspan=2,
                                    pady=5, sticky='nsew')
                                    
        self.unit_label = tk.Label(self.connections_frame,
                                   text="Unit", font=MEDIUM_FONT, 
                                   bg="lightgray")
        self.unit_label.grid(row=1, column=0)
        
        self.status_label = tk.Label(self.connections_frame,
                                     text="Status", font=MEDIUM_FONT,
                                     bg="lightgray")
        self.status_label.grid(row=1, column=1)
        
        # X-Axis power supply
        self.x_ps_status = tk.StringVar()
        self.x_ps_label = tk.Label(self.connections_frame,
                                   text="X Power Supply",
                                   bg="lightgray",
                                   width=14)
        self.x_ps_label.grid(row=2, column=0)
        
        self.x_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.x_ps_status,
                                          width=22)
        self.x_ps_status_entry.insert(0, "Disconnected")
        self.x_ps_status_entry.configure(state="readonly")
        self.x_ps_status_entry.grid(row=2, column=1)

        # Y-Axis power supply
        self.y_ps_status = tk.StringVar()
        self.y_ps_label = tk.Label(self.connections_frame,
                                   text="Y Power Supply",
                                   bg="lightgray",
                                   width=14).grid(row=3, column=0)
        
        self.y_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.y_ps_status,
                                          width=22)
        self.y_ps_status_entry.insert(0, "Disconnected")
        self.y_ps_status_entry.configure(state="readonly")
        self.y_ps_status_entry.grid(row=3, column=1)

        # Z-Axis power supply
        self.z_ps_status = tk.StringVar()
        self.z_ps_label = tk.Label(self.connections_frame,
                                   text="Z Power Supply", 
                                   bg="lightgray",
                                   width=14).grid(row=4, column=0)
                                   
        self.z_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.z_ps_status,
                                          width=22)
        self.z_ps_status_entry.insert(0, "Disconnected")
        self.z_ps_status_entry.configure(state="readonly")
        self.z_ps_status_entry.grid(row=4, column=1)

        # Truth Magnetometer
        self.mag_status = tk.StringVar()
        self.mag_label = tk.Label(self.connections_frame,
                                  text="Magnetometer",
                                  bg="lightgray",
                                  width=14).grid(row=5, column=0)
                                  
        self.mag_status_entry = tk.Entry(self.connections_frame,
                                         textvariable=self.mag_status,
                                         width=22)
        self.mag_status_entry.insert(0, "Disconnected")
        self.mag_status_entry.configure(state="readonly")
        self.mag_status_entry.grid(row=5, column=1)

        # Refresh connections button
        self.refresh_connections_button = \
            tk.Button(self.connections_frame,
                      text="Check Connections",
                      command=lambda: self.refresh_connections())
        self.refresh_connections_button.grid(row=6, column=0, columnspan=2)

    def fill_calibrate_frame(self):
        """
        Fill in calibration subframe.
        """
        
        # Relevant functions
        #self.find_template_file() <--FIXME
        #self.find_calibration_file() <--FIXME
        
        # Title bar
        self.calibration_label = \
            tk.Label(self.calibrate_frame, text="Calibration", font=LARGE_FONT,
                     bg="lightgray")
        self.calibration_label.grid(row=0, column=0, columnspan=3,
                                    pady=5, sticky='nsew')

        # Template File
        self.template_file_label = \
            tk.Label(self.calibrate_frame, text="Template file:",
                     bg="lightgray", width=12)
        self.template_file_label.grid(row=1, column=0)

        self.template_file_status_text = tk.StringVar()
        self.template_file_entry = \
            tk.Entry(self.calibrate_frame,
                     textvariable=self.template_file_status_text,
                     width=10)
        self.template_file_entry.insert(0, data.template_file)
        self.template_file_entry.configure(state="readonly")
        self.template_file_entry.grid(row=1, column=1)
        
        self.change_template_file_button = \
            tk.Button(self.calibrate_frame, text='select new',
                      command=lambda: self.change_template_file(),
                      width=10)
        self.change_template_file_button.grid(row=1, column=2, sticky='nsew')

        # Calibration File 
        self.calibration_file_label = \
            tk.Label(self.calibrate_frame, text="Calibration file:",
                     bg="lightgray", width=12)
        self.calibration_file_label.grid(row=2, column=0)
        
        self.calibration_file_status_text = tk.StringVar()
        self.calibration_file_entry = \
            tk.Entry(self.calibrate_frame,
                     textvariable=self.calibration_file_status_text,
                     width=10)
        self.calibration_file_entry.insert(0, data.calibration_file)
        self.calibration_file_entry.configure(state="readonly")
        self.calibration_file_entry.grid(row=2, column=1)
        
        self.change_calibration_file_button = \
            tk.Button(self.calibrate_frame, text='select new',
                      command=lambda: self.change_calibration_file(),
                      width=10)
        self.change_calibration_file_button.grid(row=2, column=2, sticky='nsew')
        
        # Create calibration file button
        self.calibrate_button = \
            tk.Button(self.calibrate_frame,
                      text='Create Calibration File with Template File',
                      command=lambda: self.calibrate_cage())
        self.calibrate_button.grid(row=3, column=0, columnspan=3, sticky='nsew')

        # Handle exceptions <--FIXME
        #if data.template_file is not "none found":
            #try:
                #self.load_template_file()
            #except Exception as err:
                #print("Couldn't load template file | {}".format(err))
        #if data.calibration_file is not "none found":
            #try:
                #self.load_calibration_file()
            #except Exception as err:
                #print("Couldn't load calibration file | {}".format(err))

    def fill_static_buttons_frame(self, parent):
        """
        Fill in static-test subframe.
        """

        # Validate entry data type (must be float)
        vcmd_field = (parent.register(self.validate_field),
                      '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd_voltage = (parent.register(self.validate_voltage),
                        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # Title Bar (with "radiobutton")
        self.static_or_dynamic = tk.StringVar()
        self.select_static = \
            tk.Radiobutton(self.static_buttons_frame,
                           text="Static Test: ",
                           variable=self.static_or_dynamic,
                           value="static", font=LARGE_FONT,
                           bg="lightgray", highlightthickness=0)
        self.select_static.grid(row=0, column=0, columnspan=4,
                                pady=5, sticky='nsew')

        # Field strength or voltage set bar
        # TODO: update field text to find max field for max voltage
        self.field_or_voltage = tk.StringVar()
        
        field_text = "Enter Magnetic Field \n (Gauss)" \
            .format(MAX_FIELD_VALUE)
        self.select_field = \
            tk.Radiobutton(self.static_buttons_frame,
                           text=field_text, variable=self.field_or_voltage,
                           value="field", command=self.update_typable_entries,
                           bg="lightgray", highlightthickness=0,
                           width=15)
        self.select_field.grid(row=1, column=0, columnspan=2, sticky='nsew')

        voltage_text = "Enter Voltage \n(Max {} volts)"\
                       .format(MAX_VOLTAGE_VALUE)
        self.select_voltage = \
            tk.Radiobutton(self.static_buttons_frame,
                           text=voltage_text, variable=self.field_or_voltage,
                           value="voltage", command=self.update_typable_entries,
                           bg="lightgray", highlightthickness=0,
                           width=15)
        self.select_voltage.grid(row=1, column=2, columnspan=2, sticky='nsew')

        # X-Axis label/inputs
        self.x_field_label = \
            tk.Label(self.static_buttons_frame,
                     text="x:", font=LARGE_FONT,bg="lightgray").grid(row=2,
                        column=0, sticky='ns')
        self.x_field = tk.StringVar()
        self.x_field_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_field,
                     textvariable=self.x_field, width=10)
        self.x_field_entry.grid(row=2, column=1)

        self.x_voltage_label = \
            tk.Label(self.static_buttons_frame,
                     text="x:", font=LARGE_FONT, bg="lightgray").grid(row=2,
                     column=2)
        self.x_voltage = tk.StringVar()
        self.x_voltage_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_voltage,
                     textvariable=self.x_voltage, width=10)
        self.x_voltage_entry.grid(row=2, column=3)
        
        # Y-Axis label/inputs
        self.y_field_label = \
            tk.Label(self.static_buttons_frame,
                     text="y:", font=LARGE_FONT, bg="lightgray").grid(row=3,
                        column=0)
        self.y_field = tk.StringVar()
        self.y_field_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_field,
                     textvariable=self.y_field, width=10)
        self.y_field_entry.grid(row=3, column=1)

        self.y_voltage_label = \
            tk.Label(self.static_buttons_frame,
                     text="y:", font=LARGE_FONT, bg="lightgray").grid(row=3,
                        column=2)
        self.y_voltage = tk.StringVar()
        self.y_voltage_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_voltage,
                     textvariable=self.y_voltage, width=10)
        self.y_voltage_entry.grid(row=3, column=3)
        
        # Z-Axis label/inputs
        self.z_field_label = \
            tk.Label(self.static_buttons_frame,
                     text="z:", font=LARGE_FONT, bg="lightgray").grid(row=4,
                        column=0)
        self.z_field = tk.StringVar()
        self.z_field_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_field,
                     textvariable=self.z_field, width=10)
        self.z_field_entry.grid(row=4, column=1)

        self.z_voltage_label = \
            tk.Label(self.static_buttons_frame,
                     text="z:", font=LARGE_FONT, bg="lightgray").grid(row=4,
                        column=2)
        self.z_voltage = tk.StringVar()
        self.z_voltage_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_voltage,
                     textvariable=self.z_voltage, width=10)
        self.z_voltage_entry.grid(row=4, column=3)

    def fill_dynamic_buttons_frame(self):
        """
        Fill in dynamic-test subframe.
        """
        
        # Title bar (with "radiobutton")
        self.select_dynamic = tk.Radiobutton(self.dynamic_buttons_frame,
                                             text="Dynamic Test: ",
                                             variable=self.static_or_dynamic,
                                             value="dynamic", font=LARGE_FONT,
                                             bg="lightgray",
                                             highlightthickness=0,
                                             width=15)
        self.select_dynamic.grid(row=0, column=0, columnspan=4,
                                 pady=5, sticky='nsew')
        
        # Load dynamic test button
        self.open_dynamic_csv_button = \
            tk.Button(self.dynamic_buttons_frame,
                      text='Load Dynamic Field CSV File',
                      command=lambda: open_csv(app))
        self.open_dynamic_csv_button.grid(row=1, column=0, sticky='nsew')
        
        self.blank_label = \
            tk.Label(self.dynamic_buttons_frame, text=" ", bg="lightgray",
                     width=12).grid(row=1, column=1)

    def fill_main_buttons_frame(self):
        """
        Fill in main functions subframe.
        """
        
        # Start cage button
        self.start_button = \
            tk.Button(self.main_buttons_frame,
                      text='Start Cage', command=lambda: self.start_cage())
        self.start_button.grid(row=0, column=0, sticky='nsew')
        
        # Stop cage button
        self.stop_button = \
            tk.Button(self.main_buttons_frame,
                      text='Stop Cage', state=tk.DISABLED,
                      command=lambda: self.stop_cage())
        self.stop_button.grid(row=0, column=1, sticky='nsew')

    def fill_help_frame(self):
        """
        Fill in help menu frame (TODO).
        """
        pass

    def fill_plot_frame(self):
        """
        Fill in the main plot subframe.
        """
        print("Filling plot frame...")
        
        # Create figure and initialize plots
        if not data.plots_created:
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = \
                plt.subplots(nrows=2, facecolor='lightgray')
            self.power_supplies_plot = plt.subplot(211) # Power supplies plot
            self.mag_field_plot = plt.subplot(212) # Magnetic field plot

        # Separated for easy recreation when making new plots after hitting stop
        self.update_plot_info()

        # Add to frame
        if not data.plots_created:
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            self.canvas.draw
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                             expand=True)
        data.plots_created = True
        self.canvas.draw()

    def refresh_connections(self):
        """ 
        Refresh the connections to the connected instruments (power supplies,
        magnetometer, etc.). Hooked up to the "Check Connenctions" button.
        """
        
        main_page = self.controller.frames[MainPage]

        # Allow the entry fields to be changed
        main_page.x_ps_status_entry.configure(state=tk.NORMAL)
        main_page.y_ps_status_entry.configure(state=tk.NORMAL)
        main_page.z_ps_status_entry.configure(state=tk.NORMAL)
        main_page.mag_status_entry.configure(state=tk.NORMAL)

        # Must be done in try/except to set text back to readonly
        try:
            instruments.make_connections()
        except Exception as err:
            print("Could not connect instruments | {}".format(err))

        # For applicable connections, delete the entry and update it
        if not (instruments.x == "No connection"):
            main_page.x_ps_status_entry.delete(0, tk.END)
            main_page.x_ps_status_entry.insert(tk.END, "Connected")

        if not (instruments.y == "No connection"):
            main_page.y_ps_status_entry.delete(0, tk.END)
            main_page.y_ps_status_entry.insert(tk.END, "Connected")

        if not (instruments.z == "No connection"):
            main_page.z_ps_status_entry.delete(0, tk.END)
            main_page.z_ps_status_entry.insert(tk.END, "Connected")

        if not (instruments.mag == "No connection"):
            main_page.mag_status_entry.delete(0, tk.END)
            main_page.mag_status_entry.insert(tk.END, "Connected")

        # FIXME: Set the entry fields back to read only
        main_page.x_ps_status_entry.configure(state="readonly")
        main_page.y_ps_status_entry.configure(state="readonly")
        main_page.z_ps_status_entry.configure(state="readonly")
        main_page.mag_status_entry.configure(state="readonly")

    def start_cage(self):
        """
        Start the Helmholtz Cage. Can also be used to update the cage 
        print("starting the cage"). Hooked up to the "Start Cage" button.
        """
        
        # Get test options
        main_page = self.controller.frames[MainPage]
        static_or_dynamic = main_page.static_or_dynamic.get()
        field_or_voltage = main_page.field_or_voltage.get()

        # Startup static test
        if static_or_dynamic == "static":
            if field_or_voltage == "voltage":
                print("attempting to send specified voltages...")

                if main_page.x_voltage.get() == "":
                    main_page.x_voltage.set(0)
                if main_page.y_voltage.get() == "":
                    main_page.y_voltage.set(0)
                if main_page.z_voltage.get() == "":
                    main_page.z_voltage.set(0)

                data.active_x_voltage_requested = float(
                    main_page.x_voltage.get())
                data.active_y_voltage_requested = float(
                    main_page.y_voltage.get())
                data.active_z_voltage_requested = float(
                    main_page.z_voltage.get())
                instruments.send_voltage(data.active_x_voltage_requested,
                                         data.active_y_voltage_requested,
                                         data.active_z_voltage_requested)

            if field_or_voltage == "field":
                print("attempting to send specified magnetic field...")
                try:
                    data.active_x_mag_field_requested = \
                        float(main_page.x_field.get())
                except Exception as error:
                    data.active_x_mag_field_requested = 0.0
                    logger.info("could not get req. x field | {}".format(error))
                    logger.info("setting req. x field to zero")
                try:
                    data.active_y_mag_field_requested = \
                        float(main_page.y_field.get())
                except Exception as error:
                    data.active_y_mag_field_requested = 0.0
                    logger.info("could not get req. y field | {}".format(error))
                    logger.info("setting req. y field to zero")
                try:
                    data.active_z_mag_field_requested = \
                        float(main_page.z_field.get())
                except Exception as error:
                    data.active_z_mag_field_requested = 0.0
                    logger.info("could not get req. z field | {}".format(error))
                    logger.info("setting req. z field to zero")

                instruments.send_field(data.active_x_mag_field_requested,
                                       data.active_y_mag_field_requested,
                                       data.active_z_mag_field_requested,
                                       data)
        
        # Ensure connections are updated and then start tracking plots
        if not hasattr(instruments, "connections_checked"):
            print("Check connections before starting")
        else:
            if main_page.start_button["text"] == 'Start Cage':
                instruments.log_data = "ON"
                print("found Start Cage text on start button")

                main_page.power_supplies_plot.cla()
                main_page.mag_field_plot.cla()

                data.plot_titles = "None"
                main_page.update_plot_info()

                (data.time, data.x_out, data.y_out, data.z_out,
                 data.x_req, data.y_req, data.z_req,
                 data.x_mag_field_actual, data.y_mag_field_actual,
                 data.z_mag_field_actual, data.x_mag_field_requested,
                 data.y_mag_field_requested, data.z_mag_field_requested) = \
                    [], [], [], [], [], [], [], [], [], [], [], [], []

                data.start_time = datetime.datetime.now()

                # Start recording data if logging hasn't already started
                log_session_data()

                self.start_cage_update_buttons()

    def start_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has started.
        """
        
        main_page = self.controller.frames[MainPage]
        
        # Change buttons to update and stop
        main_page.start_button.config(text="Update Cage Values")
        main_page.stop_button.config(state=tk.NORMAL)
        
        # Disable invalid button choices during test
        main_page.refresh_connections_button.config(state=tk.DISABLED)
        main_page.change_template_file_button.config(state=tk.DISABLED)
        main_page.change_calibration_file_button.config(state=tk.DISABLED)
        main_page.calibrate_button.config(state=tk.DISABLED)
        main_page.open_dynamic_csv_button.config(state=tk.DISABLED)

    def stop_cage(self):
        """
        Stop the current run of the cage. Hooked up to the "Stop Cage"
        button.
        """
        
        logger.info("stopping cage")
        # main_page = self.controller.frames[MainPage]
        instruments.send_voltage(0, 0, 0)
        instruments.log_data = "OFF"  # this will make logging data stop
        
        # if cage is started again in current session, new log file is created
        data.session_log_filename = ""
        data.time = []
        data.x_req = []
        data.y_req = []
        data.z_req = []
        data.x_out = []
        data.y_out = []
        data.z_out = []
        data.x_mag_field_actual = []
        data.y_mag_field_actual = []
        data.z_mag_field_actual = []
        data.x_mag_field_requested = []
        data.y_mag_field_requested = []
        data.z_mag_field_requested = []

        data.calibrating_now = False
        data.stop_calibration = False

        self.stop_cage_update_buttons()

    def stop_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has been stopped.
        """
        
        main_page = self.controller.frames[MainPage]

        # Change main buttons back to original options
        main_page.start_button.configure(text="Start Cage")
        main_page.stop_button.configure(state="disabled")
        
        # Reenable buttons
        main_page.refresh_connections_button.config(state=tk.NORMAL)
        main_page.change_template_file_button.config(state=tk.NORMAL)
        main_page.change_calibration_file_button.config(state=tk.NORMAL)
        main_page.calibrate_button.config(state=tk.NORMAL)
        main_page.open_dynamic_csv_button.config(state=tk.NORMAL)

    def update_plot_info(self):
        """
        Update the data subplots.
        """
        
        print("Updating plot info...")

        # Initialize lists for each variable that can be plotted
        x_mag_field_actual = data.x_mag_field_actual
        y_mag_field_actual = data.y_mag_field_actual
        z_mag_field_actual = data.z_mag_field_actual

        x_mag_field_requested = []
        y_mag_field_requested = []
        z_mag_field_requested = []

        # Logic to make check lists are of equal length in order to be plotted
        max_entries = len(data.time)
        print("Max entries is {}".format(max_entries))
        print("Length of 'x_mag_field_requested': {}".format(len(data.x_mag_field_requested)))
        if max_entries == 0:
            max_entries = 1

        if len(data.time) != max_entries:
            data.time = [0] * max_entries
        if len(data.x_out) != max_entries:
            data.x_out = [0]*max_entries
        if len(data.y_out) != max_entries:
            data.y_out = [0]*max_entries
        if len(data.z_out) != max_entries:
            data.z_out = [0]*max_entries
        if len(data.x_req) != max_entries:
            data.x_req = [0]*max_entries
        if len(data.y_req) != max_entries:
            data.y_req = [0]*max_entries
        if len(data.z_req) != max_entries:
            data.z_req = [0]*max_entries
        if len(data.x_mag_field_actual) != max_entries:
            data.x_mag_field_actual = [0]*max_entries
        if len(data.y_mag_field_actual) != max_entries:
            data.y_mag_field_actual = [0]*max_entries
        if len(data.z_mag_field_actual) != max_entries:
            data.z_mag_field_actual = [0]*max_entries
        if len(data.x_mag_field_requested) != max_entries:
            data.x_mag_field_requested = [0]*max_entries
        if len(data.y_mag_field_requested) != max_entries:
            data.y_mag_field_requested = [0]*max_entries
        if len(data.z_mag_field_requested) != max_entries:
            data.z_mag_field_requested = [0]*max_entries

        # Get axis limits
        power_supplies_list = (data.x_out + data.y_out + data.z_out +
                               data.x_req + data.y_req + data.z_req)
        power_supplies_master_list = [float(x) for x in power_supplies_list]
        print("power_supplies_master_list = {}".format(power_supplies_master_list))
        max_y_plot_one = 1.2*max(power_supplies_master_list)
        if max_y_plot_one < 1:
            max_y_plot_one = 1

        min_y_plot_one = min(power_supplies_master_list)

        mag_field_master_list = (data.x_mag_field_actual +
                                 data.y_mag_field_actual +
                                 data.z_mag_field_actual +
                                 data.x_mag_field_requested +
                                 data.y_mag_field_requested +
                                 data.z_mag_field_requested)

        max_y_plot_two = 1.2*max(mag_field_master_list)
        if max_y_plot_two < 1:
            max_y_plot_two = 1

        min_y_plot_two = min(mag_field_master_list)

        # Plot
        self.power_supplies_plot.plot(data.time, data.x_out, 'r', label='x_ps_output')
        self.power_supplies_plot.plot(data.time, data.x_req, 'r--', label='x_ps_requested')
        self.power_supplies_plot.plot(data.time, data.y_out, 'g', label='y_ps_output')
        self.power_supplies_plot.plot(data.time, data.y_req, 'g--', label='y_ps_requested')
        self.power_supplies_plot.plot(data.time, data.z_out, 'b', label='z_ps_output')
        self.power_supplies_plot.plot(data.time, data.z_req, 'b--', label='z_ps_requested')

        self.plot_1_axes = self.power_supplies_plot.axes
        self.plot_1_axes.set_ylim(min_y_plot_one, max_y_plot_one)

        self.mag_field_plot.plot(data.time, data.x_mag_field_actual, 'r', label='x_mag_field_actual')
        self.mag_field_plot.plot(data.time, data.x_mag_field_requested, 'r--', label='x_mag_field_requested')
        self.mag_field_plot.plot(data.time, data.y_mag_field_actual, 'g', label='y_mag_field_actual')
        self.mag_field_plot.plot(data.time, data.y_mag_field_requested, 'g--', label='y_mag_field_requested')
        self.mag_field_plot.plot(data.time, data.z_mag_field_actual, 'b', label='z_mag_field_actual')
        self.mag_field_plot.plot(data.time, data.z_mag_field_requested, 'b--', label='z_mag_field_requested')

        self.plot_2_axes = self.mag_field_plot.axes
        self.plot_2_axes.set_ylim(min_y_plot_two, max_y_plot_two)

        self.power_supplies_plot.get_shared_x_axes().join(self.power_supplies_plot, self.mag_field_plot)
        self.power_supplies_plot.set_xticklabels([])
        self.power_supplies_plot.set_facecolor("whitesmoke")
        self.mag_field_plot.set_facecolor("whitesmoke")

        self.power_supplies_plot.set_title("Voltage")
        self.power_supplies_plot.set_ylabel("Volts")

        self.mag_field_plot.set_title("Magnetic Field")
        self.mag_field_plot.set_xlabel("Seconds")
        self.mag_field_plot.set_ylabel("Gauss")

        # Create plot titles (only needs to be run once)
        if data.plot_titles == "None": # only need to do this once for the plots
            self.power_supplies_plot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.00),
                                            ncol=3, fancybox=True, prop={'size': 7})
            self.mag_field_plot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0),
                                       ncol=3, fancybox=True, prop={'size': 7})
            data.plot_titles = "Exist"

    def update_typable_entries(self):
        """
        Determine, based on the selected radiobutton in the static test 
        bar, if column should be enabled/disabled.
        """
        
        field_or_voltage = self.field_or_voltage.get()
        if field_or_voltage == "voltage":
            self.x_voltage_entry.configure(state=tk.NORMAL)
            self.y_voltage_entry.configure(state=tk.NORMAL)
            self.z_voltage_entry.configure(state=tk.NORMAL)

            self.x_field_entry.delete(0, 'end')
            self.y_field_entry.delete(0, 'end')
            self.z_field_entry.delete(0, 'end')

            self.x_field_entry.configure(state=tk.DISABLED)
            self.y_field_entry.configure(state=tk.DISABLED)
            self.z_field_entry.configure(state=tk.DISABLED)
            
        elif field_or_voltage == "field":
            self.x_field_entry.configure(state=tk.NORMAL)
            self.y_field_entry.configure(state=tk.NORMAL)
            self.z_field_entry.configure(state=tk.NORMAL)

            self.x_voltage_entry.delete(0, 'end')
            self.y_voltage_entry.delete(0, 'end')
            self.z_voltage_entry.delete(0, 'end')

            self.x_voltage_entry.configure(state=tk.DISABLED)
            self.y_voltage_entry.configure(state=tk.DISABLED)
            self.z_voltage_entry.configure(state=tk.DISABLED)

        def validate_field(self, action, index, value_if_allowed,
                           prior_value, text, validation_type, trigger_type,
                           widget_name):
            """
            Check that constant value entry can be interpreted as a float.
            """
            
            if (action == '1'):
                if text in '0123456789.-+':
                    try:
                        value = float(value_if_allowed)
                        if value <= MAX_FIELD_VALUE:
                            return True
                        else:
                            return False

                    except ValueError:
                        return False
                else:
                    return False
            else:
                return True

    def update_typable_entries(self):
        """
        Determine, based on the selected radiobutton in the static test 
        bar, if column should be enabled/disabled.
        """
        
        field_or_voltage = self.field_or_voltage.get()
        if field_or_voltage == "voltage":
            self.x_voltage_entry.configure(state=tk.NORMAL)
            self.y_voltage_entry.configure(state=tk.NORMAL)
            self.z_voltage_entry.configure(state=tk.NORMAL)

            self.x_field_entry.delete(0, 'end')
            self.y_field_entry.delete(0, 'end')
            self.z_field_entry.delete(0, 'end')

            self.x_field_entry.configure(state=tk.DISABLED)
            self.y_field_entry.configure(state=tk.DISABLED)
            self.z_field_entry.configure(state=tk.DISABLED)

        if field_or_voltage == "field":
            self.x_field_entry.configure(state=tk.NORMAL)
            self.y_field_entry.configure(state=tk.NORMAL)
            self.z_field_entry.configure(state=tk.NORMAL)

            self.x_voltage_entry.delete(0, 'end')
            self.y_voltage_entry.delete(0, 'end')
            self.z_voltage_entry.delete(0, 'end')

            self.x_voltage_entry.configure(state=tk.DISABLED)
            self.y_voltage_entry.configure(state=tk.DISABLED)
            self.z_voltage_entry.configure(state=tk.DISABLED)

    def validate_field(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type,
                       widget_name):
        """
        Check that constant value entry can be interpreted as a float.
        """
        
        if (action == '1'):
            if text in '0123456789.-+':
                try:
                    value = float(value_if_allowed)
                    if value <= MAX_FIELD_VALUE:
                        return True
                    else:
                        return False

                except ValueError:
                    return False
            else:
                return False
        else:
            return True

    def validate_voltage(self, action, index, value_if_allowed,
                         prior_value, text, validation_type, trigger_type,
                         widget_name):
        """
        Check that constant value entry can be interpreted as a float.
        """
                             
        if (action == '1'):
            if text in '0123456789.-+':
                try:
                    value = float(value_if_allowed)
                    if value <= MAX_VOLTAGE_VALUE:
                        return True
                    else:
                        return False

                except ValueError:

                    return False
            else:
                return False
        else:
            return True

    def find_template_file(self):
        """
        Locate the user specifed template file.
        """
        
        path = os.getcwd()
        only_files = [f for f in listdir(path) if isfile(join(path, f))]
        only_csv_files = [f for f in only_files if f.endswith(".csv")]
        template_files = [f for f in only_csv_files if "TEMPLATE" in f.upper()]
        if len(template_files) > 0:
            data.template_file = template_files[0]  # use the first found file
            logger.info("Found {} template files, loading: {}".format(
                len(template_files), data.template_file))
            self.load_template_file()
        else:
            logger.info("No template file found in current working directory")

    def find_calibration_file(self):
        """
        Locate the user specified calibration file.
        """
        
        os.chdir("..")
        root = os.getcwd()
        path = os.path.join(root, "calibrations")
        os.chdir(path)
        calibration_files = glob.glob("*CalibrationData*.csv")
        if len(calibration_files) > 0:
            data.calibration_file = calibration_files[0]  # use the first
            logger.info("Found {} calibration files, loading: {}".format(
                len(calibration_files), data.calibration_file))
            self.load_calibration_file()
        else:
            logger.info("No calibration file found in current working dir")
        os.chdir(root)

    def load_template_file(self):
        """
        Load the user specifed template file.
        """
        
        logger.info("Loading template file [{}]...".format(data.template_file))
        
        with open(data.template_file) as file:
            
            # Get the data from the template file
            template_voltages_x = []
            template_voltages_y = []
            template_voltages_z = []
            file_info = csv.reader(file, delimiter=',')
            next(file_info, None)  # skip the 1st line, these are headers
            for row in file_info:
                template_voltages_x.append(float(row[0]))
                template_voltages_y.append(float(row[1]))
                template_voltages_z.append(float(row[2]))
        
        # Check the template file values
        out = self.check_template_values(template_voltages_x,
                                         template_voltages_y,
                                         template_voltages_z)
		
		# If the values are okay, write to Data
		if out:
			data.template_voltages_x = template_voltages_x
            data.template_voltages_y = template_voltages_y
            data.template_voltages_z = template_voltages_z
                
			logger.info("loaded {} x, {} y, {} z voltages"
						.format(len(data.template_voltages_x),
								len(data.template_voltages_y),
								len(data.template_voltages_z)))
			logger.info("x template voltages: {}".format(data.template_voltages_x))
			logger.info("y template voltages: {}".format(data.template_voltages_y))
			logger.info("z template voltages: {}".format(data.template_voltages_z))
			logger.info("...completed loading template file")
			
		# Otherwise return an error
		else:
			logger.info("template file values are not achievable on the system")

    def check_template_values(self, x_values, y_values, z_values):
        """
        Check the values from a template file to ensure they are outside
        the systems limits.
        """
        
        #Check voltages that will be sent to allow calibration
        if len(x_values) == len(y_values) == len(z_values):

            for value in range(0, len(x_values)):
				x = x_values[value]
                y = y_values[value]
                z = z_values[value]

				# Check that none of the requested voltage exceed max or are less than zero
                if (x > MAX_VOLTAGE_VALUE) or (x < 0):
                    logger.info("ERROR: cannot calibrate, x voltage of "
                                "{} is above the max {} volts, or "
                                "negative".format(x, MAX_VOLTAGE_VALUE))
                    return False
                if (y > MAX_VOLTAGE_VALUE) or (y < 0):
                    logger.info("ERROR: cannot calibrate, y voltage of "
                                "{} is above the max {} volts, or "
                                "negative".format(y, MAX_VOLTAGE_VALUE))
                    return False
                if (z > MAX_VOLTAGE_VALUE) or (z < 0):
                    logger.info("ERROR: cannot calibrate, z voltage of "
                                "{} is above the max {} volts, or "
                                "negative".format(z, MAX_VOLTAGE_VALUE))
                    return False
		else:
			logger.info("The amount of X Y Z voltages are not all "
                        "equal.")
			instruments.log_data = "OFF"  # stops the logging process
			data.calibration_log_filename = ""
			return False
		
		# All values are okay
		return True

    def load_calibration_file(self):
        """
        Load the user specifed calibration file.
        """
        
        logger.info("Loading calibration file [{}]".format(data.calibration_file))
        with open(data.calibration_file) as file:
            
            # If the file is opened, reinitialize the data class
            data.calibration_voltages_x = []
            data.calibration_voltages_y = []
            data.calibration_voltages_z = []
            data.calibration_mag_field_x = []
            data.calibration_mag_field_y = []
            data.calibration_mag_field_z = []

            file_info = csv.reader(file, delimiter=',')
            next(file_info, None)  # skip the 1st line, these are headers
            for row in file_info:
                if len(row) > 0:  # skip blank rows
                    # data format: time, x_req, y_req, z_req,
                    # x_out, y_out, z_out, x_mag, y_mag, z_mag
                    logger.debug("row: {}".format(row))
                    data.calibration_time.append(row[0])
                    # since column 2 3 4 are requested voltages, they don't
                    # matter for calibration
                    data.calibration_voltages_x.append(row[4])
                    data.calibration_voltages_y.append(row[5])
                    data.calibration_voltages_z.append(row[6])
                    data.calibration_mag_field_x.append(row[7])
                    data.calibration_mag_field_y.append(row[8])
                    data.calibration_mag_field_z.append(row[9])

            logger.info("loaded {} calibration voltages/fields"
                        .format(len(data.calibration_voltages_x)))
            logger.info("x calibration voltages: {}"
                        .format(data.calibration_voltages_x))
            logger.info("y calibration voltages: {}"
                        .format(data.calibration_voltages_y))
            logger.info("z calibration voltages: {}"
                        .format(data.calibration_voltages_z))
            logger.info("x calibration fields: {}"
                        .format(data.calibration_mag_field_x))
            logger.info("y calibration fields: {}"
                        .format(data.calibration_mag_field_y))
            logger.info("z calibration fields: {}"
                        .format(data.calibration_mag_field_z))
            logger.info("...completed loading template file")

    def change_template_file(self):
        """
        Change the current template file.
        """
        
        main_page = self.controller.frames[MainPage]
        data.template_file = filedialog.askopenfilename(
            filetypes=(("Calibration template file", "*.csv"),
                       ("All files", "*.*")))
        new_filename = os.path.basename(data.template_file)
        main_page.load_template_file()
        main_page.template_file_entry.configure(state=tk.NORMAL)
        main_page.template_file_entry.delete(0, 'end')
        main_page.template_file_entry.insert(0, new_filename)
        main_page.template_file_entry.configure(state="readonly")

    def change_calibration_file(self):
        """
        Change the current calibration file.
        """
        
        main_page = self.controller.frames[MainPage]
        data.calibration_file = filedialog.askopenfilename(
            filetypes=(("Calibration file", "*.csv"),
                       ("All files", "*.*")))
        new_filename = os.path.basename(data.calibration_file)
        main_page.load_calibration_file()
        main_page.calibration_file_entry.configure(state=tk.NORMAL)
        main_page.calibration_file_entry.delete(0, 'end')
        main_page.calibration_file_entry.insert(0, new_filename)
        main_page.calibration_file_entry.configure(state="readonly")

    def calibrate_cage(self):
        """
        Calibrate the Helmholtz Cage, by mapping coil voltages to the 
        magnetic feild strength they create (for each axis individually).
        
        Should be run every time the cage is started up, due to natural 
        varience in the Earth's magnetic feild.
        
        TODO: still a WIP
        """
        
        main_page = self.controller.frames[MainPage]
        data.stop_calibration = False

        # Ensure that all instruments are properly connected
        if not hasattr(instruments, "connections_checked"):
            logger.info("Check connections before starting")
        else:

            # Connections are checked, start calibration if allowed
            if not data.calibrating_now:
                
                # Clear plots if information is on them
                main_page.power_supplies_plot.cla()
                main_page.mag_field_plot.cla()
                data.plot_titles = "None"

                # Reset information logged into the data class
                (data.time, data.x_out, data.y_out, data.z_out,
                 data.x_req, data.y_req, data.z_req,
                 data.x_mag_field_actual, data.y_mag_field_actual,
                 data.z_mag_field_actual, data.x_mag_field_requested,
                 data.y_mag_field_requested, data.z_mag_field_requested) \
                    = [], [], [], [], [], [], [], [], [], [], [], [], []

                if not data.stop_calibration:
                    data.start_time = datetime.datetime.now()
                    self.calibrate_cage_update_buttons()
            else:
                if not data.stop_calibration:
                    main_page.update_plot_info()
        
        # Begin the calibration
        data.calibrating_now = True
        
        # Run through calibration values
        for value in range(0, len(data.template_voltages_x)):
            instruments.send_voltage(data.template_voltages_x[value],
                                     data.template_voltages_y[value],
                                     data.template_voltages_z[value])
            sleep(0.01)
            
            # Read and save returned values
            (x_act, y_act, z_act) = instruments.get_requested_voltage()
            (x_mag_field_act, y_mag_field_act, z_mag_field_act) \
                = instruments.get_magnetometer_field()
            data.x_out.append(x_act)
            data.y_out.append(y_act)
            data.z_out.append(z_act)
            data.x_mag_field_actual.append(x_mag_field_act)
            data.y_mag_field_actual.append(y_mag_field_act)
            data.x_mag_field_actual.append(z_mag_field_act)
        instruments.send_voltage(0.0, 0.0, 0.0)
        
        # TODO: Curve fitting
        
        # End calibration
        data.calibrating_now = False
        data.stop_calibration = True
        data.current_value = 0
        logger.info("Stopping calibration")
        self.calibrate_cage_update_buttons()

    def calibrate_cage_update_buttons(self):
        """
        Update the buttons while the cage is calibrating and afterwards
        """
        
        main_page = self.controller.frames[MainPage]

        # Disable buttons for invalid options during calibration
        if not data.calibrating_now:
            main_page.start_button.config(text="allow calibration to complete")
            main_page.start_button.config(state=tk.DISABLED)

            main_page.refresh_connections_button.config(state=tk.DISABLED)
            main_page.change_template_file_button.config(state=tk.DISABLED)
            main_page.change_calibration_file_button.config(state=tk.DISABLED)
            main_page.calibrate_button.config(state=tk.DISABLED)
            main_page.open_dynamic_csv_button.config(state=tk.DISABLED)
        
        # Reenable buttons
        if not data.calibrating_now and data.stop_calibration \
                and (data.current_value == 0):
            main_page.start_button.config(text="Start Cage")
            main_page.start_button.config(state=tk.NORMAL)
            main_page.refresh_connections_button.config(state=tk.NORMAL)
            main_page.change_template_file_button.config(state=tk.NORMAL)
            main_page.change_calibration_file_button.config(state=tk.NORMAL)
            main_page.calibrate_button.config(state=tk.NORMAL)
            main_page.open_dynamic_csv_button.config(state=tk.NORMAL)


class HelpPage(tk.Frame):
        """
        An object class for a Help menu (TODO).
        """
        
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            
            # Main container to hold all subframes
            container = tk.Frame(self, bg="silver")
            container.grid(sticky="nsew")


if __name__ == "__main__":
    try:
        instruments = Instruments()
        data = Data()
        app = CageApp()
        app.minsize(width=250, height=600)
        app.mainloop()
        
    except Exception:
        traceback.print_exc()
