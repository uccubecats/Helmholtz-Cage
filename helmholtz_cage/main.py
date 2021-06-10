#!/usr/bin/env python

"""
Main GUI script for the UC Helmholtz Cage

Copyright 2018-2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.

Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import csv
import datetime
import glob
import logging
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import traceback

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from calibration import Calibration
from helmholtz_cage import HelmholtzCage
from template import retrieve_template, check_template_values
#from doc import *


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

def log_session_data():
    """
    Create a session log file.
    """
    main_page = app.frames[MainPage]
    print("instruments.log_data is {}".format(instruments.log_data))

    if instruments.log_data == "ON":
        today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if data.session_log_filename == "":
            data.session_log_filename = "HelmholtzCage_SessionData_{}.csv".\
                format(today)
            logger.info("creating log: {}".format(data.session_log_filename))

            if not os.path.exists("session_files"):
                os.mkdir("session_files")

            with open(os.path.join("session_files", data.session_log_filename),
                      'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['time', 'x_req', 'y_req', 'z_req', 'x_out',
                                 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])

        with open(os.path.join("session_files", data.session_log_filename),
                  'a') as file:
            threading.Timer(UPDATE_PLOT_TIME, log_session_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time)
                       .total_seconds())
            print("logging data at {}".format(str(time)))

            # *** can be used for debugging if requested voltages from template
            # file seem wrong on the output side from the power supply
            # x_req, y_req, z_req = instruments.get_requested_voltage()

            x_out, y_out, z_out = instruments.get_output_voltage()
            # TODO: add below line back in
            x_mag, y_mag, z_mag = instruments.get_magnetometer_field()
            #x_mag, y_mag, z_mag = 100, 100, 100

            if not x_mag:
                try:
                    x_mag = data.x_mag_field_actual[-1]
                except IndexError:
                    x_mag = 0.0
            if not y_mag:
                try:
                    y_mag = data.y_mag_field_actual[-1]
                except IndexError:
                    y_mag = 0.0
            if not z_mag:
                try:
                    z_mag = data.z_mag_field_actual[-1]
                except IndexError:
                    z_mag = 0.0

            writer.writerow([time,
                             data.active_x_voltage_requested,
                             data.active_y_voltage_requested,
                             data.active_z_voltage_requested,
                             x_out, y_out, z_out,
                             x_mag, y_mag, z_mag])

            data.time.append(time)
            data.x_req.append(data.active_x_voltage_requested)
            data.y_req.append(data.active_y_voltage_requested)
            data.z_req.append(data.active_z_voltage_requested)
            data.x_out.append(x_out)
            data.y_out.append(y_out)
            data.z_out.append(z_out)

            data.x_mag_field_actual.append(x_mag)
            data.y_mag_field_actual.append(y_mag)
            data.z_mag_field_actual.append(z_mag)

            data.x_mag_field_requested.append(data.active_x_mag_field_requested)
            data.y_mag_field_requested.append(data.active_y_mag_field_requested)
            data.z_mag_field_requested.append(data.active_z_mag_field_requested)

            main_page.fill_plot_frame()

def log_calibration_data():
    """
    Creates a calibration file from a loaded template file.
    """
    main_page = app.frames[MainPage]

    if instruments.log_data == "ON":
        today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if data.calibration_log_filename == "":
            data.calibration_log_filename = "HelmholtzCage_CalibrationData_{}" \
                                            ".csv".format(today)
            if not os.path.exists("calibration_files"):
                os.mkdir("calibration_files")

            logger.info("creating calibration file: {}"
                        .format(data.calibration_log_filename))

            with open(os.path.join("calibration_files",
                                   data.calibration_log_filename), 'a') as file:

                writer = csv.writer(file, delimiter=',')
                writer.writerow(['time', 'x_req', 'y_req', 'z_req', 'x_out',
                                 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])
                data.start_time = datetime.datetime.now()
                data.current_value = 0

        with open(os.path.join("calibration_files",
                               data.calibration_log_filename), 'a') as file:

            threading.Timer(UPDATE_PLOT_TIME, log_calibration_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time)
                       .total_seconds())

            # Check if it is time to get new values from template yet
            logger.info("time calibrating is: {}".format(time))
            logger.info("data.current_value is {}".format(data.current_value))
            logger.info("update_calibrate_time * data.current_value is: {}".
                        format(data.current_value * update_calibrate_time))
                        
            # Get current calibration voltages for whichever increment
            if time >= (data.current_value*update_calibrate_time):
                try:
                    data.cur_cal_x = float(data.template_voltages_x
                                           [data.current_value])
                    data.cur_cal_y = float(data.template_voltages_y
                                           [data.current_value])
                    data.cur_cal_z = float(data.template_voltages_z
                                           [data.current_value])
                except Exception as err:
                    logger.info("Could not get x,y,z voltages to send, likely "
                                "finished calibrating | {}".format(err))
                    data.cur_cal_x, data.cur_cal_y, data.cur_cal_z = 0, 0, 0
                instruments.send_voltage(data.cur_cal_x, data.cur_cal_y,
                                         data.cur_cal_z)
                data.current_value += 1

            # *** can be used for debugging if requested voltages from template
            # file seem wrong on the output side from the power supply
            # x_req, y_req, z_req = instruments.get_requested_voltage()

            # TODO: verify this gets the correct output voltage
            # get the currently read voltages on the power supply displays
            x_out, y_out, z_out = instruments.get_output_voltage()
            x_mag = 1  # *** this will have to come from magnetometer connection
            y_mag = 2
            z_mag = 3

            # Update values saved to calibration file
            writer.writerow([time, data.cur_cal_x, data.cur_cal_y,
                             data.cur_cal_z, x_out, y_out, z_out,
                             x_mag, y_mag, z_mag])

            # Update lists that will be plotted
            data.time.append(time)
            data.x_req.append(data.cur_cal_x)
            data.y_req.append(data.cur_cal_y)
            data.z_req.append(data.cur_cal_z)
            data.x_out.append(x_out)
            data.y_out.append(y_out)
            data.z_out.append(z_out)

        # Update plot if calibration is still going on
        if not data.stop_calibration:
            main_page.fill_plot_frame()

        # Stop calibration if all template voltages have been used
        if data.current_value == len(data.template_voltages_x):
            instruments.log_data = "OFF"
            logger.info("calibration file {} created - load it in before "
                        "doing a dynamic test or requesting based on "
                        "magnetic field".format(data.calibration_log_filename))
            # Allows for a new calibration file to be created again? TODO: test
            data.calibration_log_filename = ""
            data.stop_calibration = True
            logger.info("data.calibrating_now: {} | data.stop_calibration: {}"
                        .format(data.calibrating_now, data.stop_calibration))
            logger.info("in log calibration: data.stop_calibration is {}"
                        .format(data.stop_calibration))
            data.current_value = 0
            logger.info("stopping calibration")
            main_page.calibrate_cage_update_buttons()

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

        # Fill in the subframes (function calls)
        self.fill_calibrate_frame()
        self.fill_connections_frame()
        self.fill_static_buttons_frame(parent)
        self.fill_dynamic_buttons_frame()
        self.fill_main_buttons_frame()
        self.fill_help_frame()
        self.fill_plot_frame()

    def fill_connections_frame(self):
        """
        Fill in the connections subframe.
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
        Fill in the calibration subframe.
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
        #self.template_file_entry.insert(0, cage.data.template_file)
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
        #self.calibration_file_entry.insert(0, cage.data.calibration_file)
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

    def fill_static_buttons_frame(self, parent):
        """
        Fill in the static-test subframe.
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
        Fill in the dynamic-test subframe.
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
        Fill in the main functions subframe.
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
        Fill in the help menu frame (TODO).
        """
        pass

    def fill_plot_frame(self):
        """
        Fill in the main plot subframe.
        """
        print("Filling plot frame...")
        
        # Create figure and initialize plots
        if not cage.data.plots_created:
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = \
                plt.subplots(nrows=2, facecolor='lightgray')
            self.power_supplies_plot = plt.subplot(211) # Power supplies plot
            self.mag_field_plot = plt.subplot(212) # Magnetic field plot

        # Separated for easy recreation when making new plots after hitting stop
        self.update_plot_info()

        # Add to frame
        if not cage.data.plots_created:
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            self.canvas.draw
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                             expand=True)
        cage.data.plots_created = True
        self.canvas.draw()

    def refresh_connections(self):
        """ 
        Refresh the connections to the connected instruments (Hooked up 
        to the "Check Connenctions" button).
        
        TODO: Test
        """

        # Allow the entry fields to be changed
        main_page = self.controller.frames[MainPage]
        main_page.x_ps_status_entry.configure(state=tk.NORMAL)
        main_page.y_ps_status_entry.configure(state=tk.NORMAL)
        main_page.z_ps_status_entry.configure(state=tk.NORMAL)
        main_page.mag_status_entry.configure(state=tk.NORMAL)

        # Must be done in try/except to set text back to readonly
        try:
            ps_status, mag_status = cage.make_connections()
        except Exception as err:
            print("Could not connect instruments | {}".format(err))

        # For applicable connections, delete the entry and update it
        if not (ps_status[0] == False):
            main_page.x_ps_status_entry.delete(0, tk.END)
            main_page.x_ps_status_entry.insert(tk.END, "Connected")

        if not (ps_status[1] == False):
            main_page.y_ps_status_entry.delete(0, tk.END)
            main_page.y_ps_status_entry.insert(tk.END, "Connected")

        if not (ps_status[2] == False):
            main_page.z_ps_status_entry.delete(0, tk.END)
            main_page.z_ps_status_entry.insert(tk.END, "Connected")

        if not (mag_status == False):
            main_page.mag_status_entry.delete(0, tk.END)
            main_page.mag_status_entry.insert(tk.END, "Connected")

        # FIXME: Set the entry fields back to read only
        main_page.x_ps_status_entry.configure(state="readonly")
        main_page.y_ps_status_entry.configure(state="readonly")
        main_page.z_ps_status_entry.configure(state="readonly")
        main_page.mag_status_entry.configure(state="readonly")

    def start_cage(self):
        """
        Start the Helmholtz Cage (hooked up to the "Start Cage" button).
                
        TODO: Test
        """
        
        # Get test options
        main_page = self.controller.frames[MainPage]
        static_or_dynamic = main_page.static_or_dynamic.get()
        field_or_voltage = main_page.field_or_voltage.get()
        
        # Tell cage to start
        success = cage.start_cage(static_or_dynamic, field_or_voltage)
        
        # Start tracking plots
        if success:
            print("found Start Cage text on start button")
            main_page.power_supplies_plot.cla()
            main_page.mag_field_plot.cla()

            # Update plots
            cage.data.plot_titles = "None"
            main_page.update_plot_info()

            # Record start time
            cage.data.start_time = datetime.datetime.now()

            # Start recording data if logging hasn't already started
            # log_session_data()

            # Update buttons
            self.start_cage_update_buttons()

    def start_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has started.
        """
        
        main_page = self.controller.frames[MainPage]
        main_page.stop_button.config(state=tk.NORMAL)
        main_page.refresh_connections_button.config(state=tk.DISABLED)
        main_page.change_template_file_button.config(state=tk.DISABLED)
        main_page.change_calibration_file_button.config(state=tk.DISABLED)
        main_page.calibrate_button.config(state=tk.DISABLED)
        main_page.open_dynamic_csv_button.config(state=tk.DISABLED)

    def stop_cage(self):
        """
        Stop the current run of the cage. Hooked up to the "Stop Cage"
        button.
        
        TODO: Test
        """
        
        # Command the cage to stop
        main_page = self.controller.frames[MainPage]
        success = cage.stop_cage()
        # instruments.log_data = "OFF"  # this will make logging data stop
        # logger.info("stopping cage")
        
        # Reset GUI and data
        if success:
            # If cage is started again in current session, new log file is created
            # TODO
            self.stop_cage_update_buttons()
        
        # Warn user if the cage isn't shutting down
        else:
            print("ERROR: Unable to command cage to stop")

    def stop_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has been stopped.
        """
        
        main_page = self.controller.frames[MainPage]
        main_page.stop_button.configure(state=tk.DISABLED)
        main_page.refresh_connections_button.config(state=tk.NORMAL)
        main_page.change_template_file_button.config(state=tk.NORMAL)
        main_page.change_calibration_file_button.config(state=tk.NORMAL)
        main_page.calibrate_button.config(state=tk.NORMAL)
        main_page.open_dynamic_csv_button.config(state=tk.NORMAL)

    def update_plot_info(self):
        """
        Update the data subplots.
        
                
        TODO: Test
        """
        
        #print("Updating plot info...")

        # Logic to make check lists are equal length in order to be plotted
        max_entries = len(cage.data.time)
        #print("Max entries is {}".format(max_entries))
        if max_entries == 0:
            max_entries = 1
        if len(cage.data.time) != max_entries:
            cage.data.time = [0] * max_entries
        if len(cage.data.Vx) != max_entries:
            cage.data.x_out = [0]*max_entries
        if len(cage.data.Vy) != max_entries:
            cage.data.y_out = [0]*max_entries
        if len(cage.data.Vz) != max_entries:
            cage.data.z_out = [0]*max_entries
        if len(cage.data.x_req) != max_entries:
            cage.data.x_req = [0]*max_entries
        if len(cage.data.y_req) != max_entries:
            cage.data.y_req = [0]*max_entries
        if len(cage.data.z_req) != max_entries:
            cage.data.z_req = [0]*max_entries
        if len(cage.data.Bx) != max_entries:
            cage.data.Bx = [0]*max_entries
        if len(cage.data.By) != max_entries:
            cage.data.By = [0]*max_entries
        if len(cage.data.Bz) != max_entries:
            cage.data.Bz = [0]*max_entries

        # Get voltage graph axis limits
        power_supplies_list = (cage.data.Vx +
                               cage.data.Vy + 
                               cage.data.Vz)
        if cage.data.req_type == "voltage":
             power_supplies_list.append(cage.data.x_req +
                                        cage.data.y_req +
                                        cage.data.z_req)
        
        max_y_plot_one = 1.2*max(power_supplies_list)
        if max_y_plot_one < 1:
            max_y_plot_one = 1
        min_y_plot_one = min(power_supplies_list)
        
        # Get magnetic field graph axis limits
        mag_field_list = (cage.data.Bx +
                                 cage.data.By +
                                 cage.data.Bz)
        if cage.data.req_type == "field":
            mag_field_list = (cage.data.x_req +
                              cage.data.y_req +
                              cage.data.z_req)
                                     
        max_y_plot_two = 1.2*max(mag_field_list)
        if max_y_plot_two < 1:
            max_y_plot_two = 1
        min_y_plot_two = min(mag_field_list)

        # Plot
        # Power supply voltage graph
        self.power_supplies_plot.plot(cage.data.time, cage.data.Vx, 'r', label='x_ps_output')
        self.power_supplies_plot.plot(cage.data.time, cage.data.Vy, 'g', label='y_ps_output')
        self.power_supplies_plot.plot(cage.data.time, cage.data.Vz, 'b', label='z_ps_output')
        if cage.data.req_type == "voltage":
            self.power_supplies_plot.plot(cage.data.time, cage.data.x_req, 'r--', label='x_ps_requested')
            self.power_supplies_plot.plot(cage.data.time, cage.data.y_req, 'g--', label='y_ps_requested')
            self.power_supplies_plot.plot(cage.data.time, cage.data.z_req, 'b--', label='z_ps_requested')

        self.plot_1_axes = self.power_supplies_plot.axes
        self.plot_1_axes.set_ylim(min_y_plot_one, max_y_plot_one)

        # Magnetic field graph
        self.mag_field_plot.plot(cage.data.time, cage.data.Bx, 'r', label='x_mag_field_actual')
        self.mag_field_plot.plot(cage.data.time, cage.data.By, 'g', label='y_mag_field_actual')
        self.mag_field_plot.plot(cage.data.time, cage.data.Bz, 'b', label='z_mag_field_actual')
        if cage.data.req_type == "field":
            self.mag_field_plot.plot(cage.data.time, cage.data.x_req, 'r--', label='x_mag_field_requested')
            self.mag_field_plot.plot(cage.data.time, cage.data.y_req, 'g--', label='y_mag_field_requested')
            self.mag_field_plot.plot(cage.data.time, cage.data.z_req, 'b--', label='z_mag_field_requested')

        self.plot_2_axes = self.mag_field_plot.axes
        self.plot_2_axes.set_ylim(min_y_plot_two, max_y_plot_two)

        # Combine plots for GUI display
        self.power_supplies_plot.get_shared_x_axes().join(self.power_supplies_plot, self.mag_field_plot)
        self.power_supplies_plot.set_xticklabels([])
        
        self.power_supplies_plot.set_facecolor("whitesmoke")
        self.power_supplies_plot.set_title("Voltage")
        self.power_supplies_plot.set_ylabel("Volts")
        
        self.mag_field_plot.set_facecolor("whitesmoke")
        self.mag_field_plot.set_title("Magnetic Flux Density")
        self.mag_field_plot.set_xlabel("Seconds")
        self.mag_field_plot.set_ylabel("Gauss")

        # Create plot titles (only needs to be run once)
        if cage.data.plot_titles == "None": # only need to do this once for the plots
            self.power_supplies_plot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.00),
                                            ncol=3, fancybox=True, prop={'size': 7})
            self.mag_field_plot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0),
                                       ncol=3, fancybox=True, prop={'size': 7})
            cage.data.plot_titles = "Exist"

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

    def change_template_file(self):
        """
        Load the user specifed template file.
        """
        
        # Ask the user for the template file
        main_page = self.controller.frames[MainPage]
        start_dir = os.path.join(main_dir, "templates")
        template_file = filedialog.askopenfilename(initialdir=start_dir,
                                                   filetypes=(("csv file","*.csv"),
                                                              ("All files","*.*")))
        # logger.info("Loading template file [{}]...".format(template_file))
        
        # Retrieve and check template
        template_dir, template_name = os.path.split(template_file)
        template = retrieve_template(template_dir, template_name)
        is_okay = check_template_values(template, [5.0, 1.5]) # <--TODO: replace these
        
        # Give template to the Helmholtz Cage
        if is_okay:
            cage.template = template
            cage.has_template = True
            cage.data.template_file = template_file
        
            # Put template file name into GUI entry
            main_page.template_file_entry.configure(state=tk.NORMAL)
            main_page.template_file_entry.delete(0, 'end')
            main_page.template_file_entry.insert(0, template_file)
            main_page.template_file_entry.configure(state="readonly")
        else:
            print("ERROR: Unable to load selected template file")
    
    def change_calibration_file(self):
        """
        Load the user specifed calibration file.
        
        TODO: Test
        """
        
        # Ask the user for the calibration file
        main_page = self.controller.frames[MainPage]
        start_dir = os.path.join(main_dir, "calibrations")
        calibration_file = filedialog.askopenfilename(initialdir=start_dir,
                                                      filetypes=(("csv file","*.csv"),
                                                                 ("All files","*.*")))
        # logger.info("Loading calibration file [{}]".format(calibration_file))
        
        # Retrieve and check the calibration
        calibration_dir, calibration_name = os.path.split(calibration_file)
        calibration = Calibration(calibration_dir, calibration_name)
        success = calibration.load_calibration_file()
        
        # Give calibration to the Helmholtz Cage
        if success:
            cage.calibration = calibration
            cage.has_calibration = True
            cage.data.calibration_file = calibration_file
            
            # Put calibration file name into GUI entry
            main_page.calibration_file_entry.configure(state=tk.NORMAL)
            main_page.calibration_file_entry.delete(0, 'end')
            main_page.calibration_file_entry.insert(0, calibration_file)
            main_page.calibration_file_entry.configure(state="readonly")
        else:
            print("ERROR: Unable to load selected calibration file")
    
    def calibrate_cage(self):
        """
        Calibrate the Helmholtz Cage, by mapping coil voltages to the 
        magnetic feild strength they create (for each axis individually).
        
        Should be run every time the cage is started, due to natural 
        varience in the Earth's magnetic feild.
        
        TODO: Needs extensive rework.
        """
        pass
        # main_page = self.controller.frames[MainPage]
        # data.stop_calibration = False
        # data_len = len(data.template_voltages_x)

        # # Ensure that all instruments are properly connected
        # if not hasattr(instruments, "connections_checked"):
            # logger.info("Check connections before starting")
        # else:

            # # Connections are checked, start calibration if allowed
            # if not data.calibrating_now:
                
                # # Clear plots if information is on them
                # main_page.power_supplies_plot.cla()
                # main_page.mag_field_plot.cla()
                # data.plot_titles = "None"

                # # Reset information logged into the data class
                # (data.time, data.x_out, data.y_out, data.z_out,
                 # data.x_req, data.y_req, data.z_req,
                 # data.x_mag_field_actual, data.y_mag_field_actual,
                 # data.z_mag_field_actual, data.x_mag_field_requested,
                 # data.y_mag_field_requested, data.z_mag_field_requested) \
                    # = [], [], [], [], [], [], [], [], [], [], [], [], []

                # if not data.stop_calibration:
                    # data.start_time = datetime.datetime.now()
                    # self.calibrate_cage_update_buttons()
            # else:
                # if not data.stop_calibration:
                    # main_page.update_plot_info()
        
        # # Begin the calibration
        # data.calibrating_now = True
        
        # # Run through calibration values
        # for value in range(0, data_len):
            # instruments.send_voltage(x_volts[value], y_volts[value], z_volts[value])
            # sleep(0.1)
                
            # # Read and save returned values
            # (x_act, y_act, z_act) = instruments.get_requested_voltage()
            # (x_mag_field_act, y_mag_field_act, z_mag_field_act) \
                    # = instruments.get_magnetometer_field()
            # data.x_out.append(x_act)
            # data.y_out.append(y_act)
            # data.z_out.append(z_act)
            # data.x_mag_field_actual.append(x_mag_field_act)
            # data.y_mag_field_actual.append(y_mag_field_act)
            # data.x_mag_field_actual.append(z_mag_field_act)
            
            # # Capture where in the data we switch to the next coil
            # if (data_len-value>>2):
                # if (x_volts[value]!=0) and (y_volts[value+2]!=0):
                    # cutoff_x = value
                # if (y_volts[value]!=0) and (z_volts[value+2]!=0):
                    # cutoff_y = value
                    
        # # Reset voltages
        # instruments.send_voltage(0.0, 0.0, 0.0)
        
        # # Perform line fit to the data and analyse results
        # x_data, y_data, z_data = parse_data(fake_data, cutoff_x, cutoff_y)
        # x_equation, y_equation, z_equation = calibration_results_popup(x_data, y_data, z_data)
        
        # # Store equation bits
        # data.x_slope = x_equation[1]
        # data.y_slope = y_equation[1]
        # data.z_slope = z_equation[1]
        # data.x_intercept = x_equation[2]
        # data.y_intercept = y_equation[2]
        # data.z_intercept = z_equation[2]
        
        # # End calibration
        # data.calibrating_now = False
        # data.stop_calibration = True
        # data.current_value = 0
        # logger.info("Stopping calibration")
        # self.calibrate_cage_update_buttons()

    def calibrate_cage_update_buttons(self):
        """
        Update the buttons while the cage is calibrating and afterwards
        """
        
        main_page = self.controller.frames[MainPage]

        # Disable buttons for invalid options during calibration
        if not cage.data.calibrating_now:
            main_page.start_button.config(text="allow calibration to complete")
            main_page.start_button.config(state=tk.DISABLED)

            main_page.refresh_connections_button.config(state=tk.DISABLED)
            main_page.change_template_file_button.config(state=tk.DISABLED)
            main_page.change_calibration_file_button.config(state=tk.DISABLED)
            main_page.calibrate_button.config(state=tk.DISABLED)
            main_page.open_dynamic_csv_button.config(state=tk.DISABLED)
        
        # Reenable buttons
        if not cage.data.calibrating_now and cage.data.stop_calibration \
                and (cage.data.current_value == 0):
            main_page.start_button.config(text="Start Cage")
            main_page.start_button.config(state=tk.NORMAL)
            main_page.refresh_connections_button.config(state=tk.NORMAL)
            main_page.change_template_file_button.config(state=tk.NORMAL)
            main_page.change_calibration_file_button.config(state=tk.NORMAL)
            main_page.calibrate_button.config(state=tk.NORMAL)
            main_page.open_dynamic_csv_button.config(state=tk.NORMAL)


class HelpPage(tk.Frame):
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            # main container to hold all subframes
            container = tk.Frame(self, bg="black")
            container.grid(sticky="nsew")


if __name__ == "__main__":
    
    # Retrieve program directory path
    main_dir = str(sys.argv[1])
    
    try:
        cage = HelmholtzCage(main_dir)
        app = CageApp()
        app.minsize(width=250, height=600)
        app.mainloop()
        
    except Exception:
        traceback.print_exc()
