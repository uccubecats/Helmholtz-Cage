#!/usr/bin/env python

"""
  Main GUI code for the UC Helmholtz Cage

  Copyright 2018-2021 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.

  Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import csv
#import datetime
import logging
import os
#import threading
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


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

# def log_session_data():
    # """
    # Create a session log file.
    # """
    # main_page = app.frames[MainPage]
    # print("instruments.log_data is {}".format(instruments.log_data))

    # if instruments.log_data == "ON":
        # today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # if data.session_log_filename == "":
            # data.session_log_filename = "HelmholtzCage_SessionData_{}.csv".\
                # format(today)
            # logger.info("creating log: {}".format(data.session_log_filename))

            # if not os.path.exists("session_files"):
                # os.mkdir("session_files")

            # with open(os.path.join("session_files", data.session_log_filename),
                      # 'a') as file:
                # writer = csv.writer(file, delimiter=',')
                # writer.writerow(['time', 'x_req', 'y_req', 'z_req', 'x_out',
                                 # 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])

        # with open(os.path.join("session_files", data.session_log_filename),
                  # 'a') as file:
            # threading.Timer(UPDATE_PLOT_TIME, log_session_data).start()
            # writer = csv.writer(file, delimiter=',')
            # time = int((datetime.datetime.now() - data.start_time)
                       # .total_seconds())
            # print("logging data at {}".format(str(time)))

            # # *** can be used for debugging if requested voltages from template
            # # file seem wrong on the output side from the power supply
            # # x_req, y_req, z_req = instruments.get_requested_voltage()

            # x_out, y_out, z_out = instruments.get_output_voltage()
            # # TODO: add below line back in
            # x_mag, y_mag, z_mag = instruments.get_magnetometer_field()
            # #x_mag, y_mag, z_mag = 100, 100, 100

            # if not x_mag:
                # try:
                    # x_mag = data.x_mag_field_actual[-1]
                # except IndexError:
                    # x_mag = 0.0
            # if not y_mag:
                # try:
                    # y_mag = data.y_mag_field_actual[-1]
                # except IndexError:
                    # y_mag = 0.0
            # if not z_mag:
                # try:
                    # z_mag = data.z_mag_field_actual[-1]
                # except IndexError:
                    # z_mag = 0.0

            # writer.writerow([time,
                             # data.active_x_voltage_requested,
                             # data.active_y_voltage_requested,
                             # data.active_z_voltage_requested,
                             # x_out, y_out, z_out,
                             # x_mag, y_mag, z_mag])

            # data.time.append(time)
            # data.x_req.append(data.active_x_voltage_requested)
            # data.y_req.append(data.active_y_voltage_requested)
            # data.z_req.append(data.active_z_voltage_requested)
            # data.x_out.append(x_out)
            # data.y_out.append(y_out)
            # data.z_out.append(z_out)

            # data.x_mag_field_actual.append(x_mag)
            # data.y_mag_field_actual.append(y_mag)
            # data.z_mag_field_actual.append(z_mag)

            # data.x_mag_field_requested.append(data.active_x_mag_field_requested)
            # data.y_mag_field_requested.append(data.active_y_mag_field_requested)
            # data.z_mag_field_requested.append(data.active_z_mag_field_requested)

            # main_page.fill_plot_frame()

# def log_calibration_data():
    # """
    # Creates a calibration file from a loaded template file.
    # """
    # main_page = app.frames[MainPage]

    # if instruments.log_data == "ON":
        # today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # if data.calibration_log_filename == "":
            # data.calibration_log_filename = "HelmholtzCage_CalibrationData_{}" \
                                            # ".csv".format(today)
            # if not os.path.exists("calibration_files"):
                # os.mkdir("calibration_files")

            # logger.info("creating calibration file: {}"
                        # .format(data.calibration_log_filename))

            # with open(os.path.join("calibration_files",
                                   # data.calibration_log_filename), 'a') as file:

                # writer = csv.writer(file, delimiter=',')
                # writer.writerow(['time', 'x_req', 'y_req', 'z_req', 'x_out',
                                 # 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])
                # data.start_time = datetime.datetime.now()
                # data.current_value = 0

        # with open(os.path.join("calibration_files",
                               # data.calibration_log_filename), 'a') as file:

            # threading.Timer(UPDATE_PLOT_TIME, log_calibration_data).start()
            # writer = csv.writer(file, delimiter=',')
            # time = int((datetime.datetime.now() - data.start_time)
                       # .total_seconds())

            # # Check if it is time to get new values from template yet
            # logger.info("time calibrating is: {}".format(time))
            # logger.info("data.current_value is {}".format(data.current_value))
            # logger.info("update_calibrate_time * data.current_value is: {}".
                        # format(data.current_value * update_calibrate_time))
                        
            # # Get current calibration voltages for whichever increment
            # if time >= (data.current_value*update_calibrate_time):
                # try:
                    # data.cur_cal_x = float(data.template_voltages_x
                                           # [data.current_value])
                    # data.cur_cal_y = float(data.template_voltages_y
                                           # [data.current_value])
                    # data.cur_cal_z = float(data.template_voltages_z
                                           # [data.current_value])
                # except Exception as err:
                    # logger.info("Could not get x,y,z voltages to send, likely "
                                # "finished calibrating | {}".format(err))
                    # data.cur_cal_x, data.cur_cal_y, data.cur_cal_z = 0, 0, 0
                # instruments.send_voltage(data.cur_cal_x, data.cur_cal_y,
                                         # data.cur_cal_z)
                # data.current_value += 1

            # # *** can be used for debugging if requested voltages from template
            # # file seem wrong on the output side from the power supply
            # # x_req, y_req, z_req = instruments.get_requested_voltage()

            # # TODO: verify this gets the correct output voltage
            # # get the currently read voltages on the power supply displays
            # x_out, y_out, z_out = instruments.get_output_voltage()
            # x_mag = 1  # *** this will have to come from magnetometer connection
            # y_mag = 2
            # z_mag = 3

            # # Update values saved to calibration file
            # writer.writerow([time, data.cur_cal_x, data.cur_cal_y,
                             # data.cur_cal_z, x_out, y_out, z_out,
                             # x_mag, y_mag, z_mag])

            # # Update lists that will be plotted
            # data.time.append(time)
            # data.x_req.append(data.cur_cal_x)
            # data.y_req.append(data.cur_cal_y)
            # data.z_req.append(data.cur_cal_z)
            # data.x_out.append(x_out)
            # data.y_out.append(y_out)
            # data.z_out.append(z_out)

        # # Update plot if calibration is still going on
        # if not data.stop_calibration:
            # main_page.fill_plot_frame()

        # # Stop calibration if all template voltages have been used
        # if data.current_value == len(data.template_voltages_x):
            # instruments.log_data = "OFF"
            # logger.info("calibration file {} created - load it in before "
                        # "doing a dynamic test or requesting based on "
                        # "magnetic field".format(data.calibration_log_filename))
            # # Allows for a new calibration file to be created again? TODO: test
            # data.calibration_log_filename = ""
            # data.stop_calibration = True
            # logger.info("data.calibrating_now: {} | data.stop_calibration: {}"
                        # .format(data.calibrating_now, data.stop_calibration))
            # logger.info("in log calibration: data.stop_calibration is {}"
                        # .format(data.stop_calibration))
            # data.current_value = 0
            # logger.info("stopping calibration")
            # main_page.calibrate_cage_update_buttons()

class MainPage(tk.Frame):
    """
    A Tkinter Frame object class for the main page of the Helmholtz Cage
    application.
    """
    
    def __init__(self, parent, controller):
        
        # Initialize Tkinter frame
        tk.Frame.__init__(self, parent)
        
        # Add controller to access parent CageApp class
        self.controller = controller
        
        # Create container for all the subframes on the GUI
        container = tk.Frame(self, bg="silver")
        container.grid(sticky="nsew")
        
        # Create subframes for main frame
        self.connections_frame = tk.Frame(container,
                                          bg="lightgray",
                                          height=50,
                                          highlightbackground="silver",
                                          highlightthickness=2)
        
        self.calibrate_frame = tk.Frame(container,
                                        bg="lightgray",
                                        height=50,
                                        highlightbackground="silver",
                                        highlightthickness=2)
        
        self.static_buttons_frame = tk.Frame(container,
                                             bg="lightgray",
                                             height=50,
                                             highlightbackground="silver",
                                             highlightthickness=2)
        
        self.dynamic_buttons_frame = tk.Frame(container,
                                              bg="lightgray",
                                              height=50,
                                              highlightbackground="silver",
                                              highlightthickness=2)
        
        self.main_buttons_frame = tk.Frame(container,
                                           bg="lightgray",
                                           height=50,
                                           highlightbackground="silver",
                                           highlightthickness=2)
        
        self.help_frame = tk.Frame(container,
                                   bg="lightgray",
                                   height=50,
                                   highlightbackground="silver",
                                   highlightthickness=2)
        
        self.plots_frame = tk.Frame(container,
                                    bg="lightgray",
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
        
        # Set weights for expansion
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
        
        # Create Tk entry variables
        self.x_ps_status = tk.StringVar()
        self.y_ps_status = tk.StringVar()
        self.z_ps_status = tk.StringVar()
        self.mag_status = tk.StringVar()
        
        # Create labels
        self.cxn_title = tk.Label(self.connections_frame,
                                  text="Connections",
                                  font=LARGE_FONT,
                                  bg="lightgray")
                                    
        self.unit_label = tk.Label(self.connections_frame,
                                   text="Unit",
                                   font=MEDIUM_FONT, 
                                   bg="lightgray")
        
        self.status_label = tk.Label(self.connections_frame,
                                     text="Status",
                                     font=MEDIUM_FONT,
                                     bg="lightgray")
        
        self.x_ps_label = tk.Label(self.connections_frame,
                                   text="X Power Supply",
                                   bg="lightgray",
                                   width=14)
        
        self.y_ps_label = tk.Label(self.connections_frame,
                                   text="Y Power Supply",
                                   bg="lightgray",
                                   width=14)
        
        self.z_ps_label = tk.Label(self.connections_frame,
                                   text="Z Power Supply", 
                                   bg="lightgray",
                                   width=14)
        
        self.mag_label = tk.Label(self.connections_frame,
                                  text="Magnetometer",
                                  bg="lightgray",
                                  width=14)
        
        # Create and configure connection status entries
        self.x_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.x_ps_status,
                                          width=22)
        self.x_ps_status_entry.insert(0, "Disconnected")
        self.x_ps_status_entry.configure(state="readonly")
        
        self.y_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.y_ps_status,
                                          width=22)
        self.y_ps_status_entry.insert(0, "Disconnected")
        self.y_ps_status_entry.configure(state="readonly")
        
        self.z_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.z_ps_status,
                                          width=22)
        self.z_ps_status_entry.insert(0, "Disconnected")
        self.z_ps_status_entry.configure(state="readonly")
        
        self.mag_status_entry = tk.Entry(self.connections_frame,
                                         textvariable=self.mag_status,
                                         width=22)
        self.mag_status_entry.insert(0, "Disconnected")
        self.mag_status_entry.configure(state="readonly")
        
        # Create check connection button
        self.refresh_cxns_button = tk.Button(self.connections_frame,
                                             text="Check Connections",
                                             command=lambda: self.controller.refresh_connections())
        
        # Position widgets
        self.cxn_title.grid(row=0, column=0, columnspan=2, pady=5, sticky='nsew')
        self.unit_label.grid(row=1, column=0)
        self.status_label.grid(row=1, column=1)
        self.x_ps_label.grid(row=2, column=0)
        self.x_ps_status_entry.grid(row=2, column=1)
        self.y_ps_label.grid(row=3, column=0)
        self.y_ps_status_entry.grid(row=3, column=1)
        self.z_ps_label.grid(row=4, column=0)
        self.z_ps_status_entry.grid(row=4, column=1)
        self.mag_label.grid(row=5, column=0)
        self.mag_status_entry.grid(row=5, column=1)
        self.refresh_cxns_button.grid(row=6, column=0, columnspan=2)
    
    def fill_calibrate_frame(self):
        """
        Fill in the calibration subframe.
        """
        
        # Create calibration file Tk entry variable
        self.calibration_file_status = tk.StringVar()
        
        # Create labels
        self.calibration_label = tk.Label(self.calibrate_frame,
                                          text="Calibration",
                                          font=LARGE_FONT,
                                          bg="lightgray")
        
        self.calibration_file_label = tk.Label(self.calibrate_frame,
                                               text="Calibration file:",
                                               bg="lightgray",
                                               width=12)
        
        # Create and configure file entry
        self.calibration_file_entry = tk.Entry(self.calibrate_frame,
                                               textvariable=self.calibration_file_status,
                                               width=10)
        self.calibration_file_entry.configure(state="readonly")
        
        # Create change calibration file button
        self.change_calibration_file_button = tk.Button(self.calibrate_frame,
                                                        text='Select',
                                                        command=lambda: self.controller.change_calibration_file(),
                                                        width=10)
        
        # Position widgets
        self.calibration_label.grid(row=0, column=0, columnspan=3, pady=5, sticky='nsew')
        self.calibration_file_label.grid(row=2, column=0)
        self.calibration_file_entry.grid(row=2, column=1)
        self.change_calibration_file_button.grid(row=2, column=2, sticky='nsew')
    
    def fill_static_buttons_frame(self, parent):
        """
        Fill in the static-test subframe.
        """
        
        # Create Tk entry variables
        self.test_type = tk.StringVar()
        self.ctrl_type = tk.StringVar()
        self.x_field = tk.StringVar()
        self.x_voltage = tk.StringVar()
        self.y_field = tk.StringVar()
        self.y_voltage = tk.StringVar()
        self.z_field = tk.StringVar()
        self.z_voltage = tk.StringVar()
        
        # Pre-create button text labels
        # TODO: update field text to find max field for max voltage
        field_text = "Enter Magnetic Field \n (Gauss)".format(MAX_FIELD_VALUE)
        voltage_text = "Enter Voltage \n(Max {} volts)".format(MAX_VOLTAGE_VALUE)
        
        # Configure validate entry data types (must be float)
        vcmd_field = (parent.register(self.validate_field),
                      '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd_voltage = (parent.register(self.validate_voltage),
                        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        # Create test type selection buttons
        self.select_static = tk.Radiobutton(self.static_buttons_frame,
                                            text="Static Test",
                                            variable=self.test_type,
                                            command=self.update_static_dynamic_buttons,
                                            value="static",
                                            font=LARGE_FONT,
                                            bg="lightgray",
                                            highlightthickness=0)
        
        self.select_field = tk.Radiobutton(self.static_buttons_frame,
                                           text=field_text,
                                           variable=self.ctrl_type,
                                           value="field",
                                           command=self.update_typable_entries,
                                           bg="lightgray",
                                           highlightthickness=0,
                                           width=15)
        
        self.select_voltage = tk.Radiobutton(self.static_buttons_frame,
                                             text=voltage_text,
                                             variable=self.ctrl_type,
                                             value="voltage",
                                             command=self.update_typable_entries,
                                             bg="lightgray",
                                             highlightthickness=0,
                                             width=15)
        
        # Create labels
        self.x_field_label = tk.Label(self.static_buttons_frame,
                                      text="x:",
                                      font=LARGE_FONT,
                                      bg="lightgray")
        
        self.x_voltage_label = tk.Label(self.static_buttons_frame,
                                        text="x:",
                                        font=LARGE_FONT,
                                        bg="lightgray")
        
        self.y_field_label = tk.Label(self.static_buttons_frame,
                                      text="y:",
                                      font=LARGE_FONT,
                                      bg="lightgray")
        
        self.y_voltage_label = tk.Label(self.static_buttons_frame,
                                        text="y:",
                                        font=LARGE_FONT,
                                        bg="lightgray")
        
        self.z_field_label = tk.Label(self.static_buttons_frame,
                                      text="z:",
                                      font=LARGE_FONT,
                                      bg="lightgray")
        
        self.z_voltage_label = tk.Label(self.static_buttons_frame,
                                        text="z:",
                                        font=LARGE_FONT,
                                        bg="lightgray")
                                        
        # Create value entries
        self.x_field_entry = tk.Entry(self.static_buttons_frame,
                                      state=tk.DISABLED,
                                      validate='key',
                                      validatecommand=vcmd_field,
                                      textvariable=self.x_field,
                                      width=10)
        
        self.x_voltage_entry = tk.Entry(self.static_buttons_frame,
                                        state=tk.DISABLED,
                                        validate='key',
                                        validatecommand=vcmd_voltage,
                                        textvariable=self.x_voltage,
                                        width=10)
        
        self.y_field_entry = tk.Entry(self.static_buttons_frame,
                                      state=tk.DISABLED,
                                      validate='key',
                                      validatecommand=vcmd_field,
                                      textvariable=self.y_field,
                                      width=10)
        
        self.y_voltage_entry = tk.Entry(self.static_buttons_frame,
                                        state=tk.DISABLED,
                                        validate='key',
                                        validatecommand=vcmd_voltage,
                                        textvariable=self.y_voltage,
                                        width=10)
        
        self.z_field_entry = tk.Entry(self.static_buttons_frame,
                                      state=tk.DISABLED,
                                      validate='key',
                                      validatecommand=vcmd_field,
                                      textvariable=self.z_field,
                                      width=10)
        
        self.z_voltage_entry = tk.Entry(self.static_buttons_frame,
                                        state=tk.DISABLED,
                                        validate='key',
                                        validatecommand=vcmd_voltage,
                                        textvariable=self.z_voltage,
                                        width=10)
        
        # Create static value command button
        self.static_command_button = tk.Button(self.static_buttons_frame,
                                               text='Command Values',
                                               command=lambda: self.controller.command_static_value(),
                                               width=15,
                                               state=tk.DISABLED)
        
        # Position widgets
        self.select_static.grid(row=0, column=0, columnspan=4, pady=5, sticky='nsew')
        self.select_field.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.select_voltage.grid(row=1, column=2, columnspan=2, sticky='nsew')
        self.x_field_label.grid(row=2, column=0, sticky='ns')
        self.x_field_entry.grid(row=2, column=1)
        self.x_voltage_label.grid(row=2, column=2)
        self.x_voltage_entry.grid(row=2, column=3)
        self.y_field_label.grid(row=3, column=0)
        self.y_field_entry.grid(row=3, column=1)
        self.y_voltage_label.grid(row=3, column=2)
        self.y_voltage_entry.grid(row=3, column=3)
        self.z_field_label.grid(row=4, column=0)
        self.z_field_entry.grid(row=4, column=1)
        self.z_voltage_label.grid(row=4, column=2)
        self.z_voltage_entry.grid(row=4, column=3)
        self.static_command_button.grid(row=5, column=0, columnspan=4, sticky='ns')
    
    def fill_dynamic_buttons_frame(self):
        """
        Fill in the dynamic-test subframe.
        """
        
        # Create Tk entry variables
        self.template_file_status_text = tk.StringVar()
        self.is_calibration_run = tk.BooleanVar()
        
        # Create test type selection button (dynamic)
        self.select_dynamic =  tk.Radiobutton(self.dynamic_buttons_frame,
                                              text="Dynamic Test",
                                              variable=self.test_type,
                                              command=self.update_static_dynamic_buttons,
                                              value="dynamic",
                                              font=LARGE_FONT,
                                              bg="lightgray",
                                              highlightthickness=0,
                                              width=15)
        
        # Create label
        self.template_file_label = tk.Label(self.dynamic_buttons_frame,
                                            text="Template file:",
                                            bg="lightgray",
                                            width=12)
        
        # Create and configure template file name entry
        self.template_file_entry = tk.Entry(self.dynamic_buttons_frame,
                                            textvariable=self.template_file_status_text,
                                            width=10)
        self.template_file_entry.configure(state="readonly")
        
        # Create change template file button
        self.change_template_file_button = tk.Button(self.dynamic_buttons_frame,
                                                     text='Select',
                                                     command=lambda: self.controller.change_template_file(),
                                                     width=10)
        
        # Create button for calibrating from template file
        self.select_calibration = tk.Checkbutton(self.dynamic_buttons_frame,
                                                 text="Calibrate from template",
                                                 variable=self.is_calibration_run,
                                                 bg="lightgray",
                                                 highlightthickness=0,
                                                 state=tk.DISABLED)
        
        # Position widgets
        self.select_dynamic.grid(row=0, column=0, columnspan=4, pady=5, sticky='nsew')
        self.template_file_label.grid(row=1, column=0)
        self.template_file_entry.grid(row=1, column=1)
        self.change_template_file_button.grid(row=1, column=2, sticky='nsew')
        self.select_calibration.grid(row=2, column=0, columnspan=3, sticky="nsew")
    
    def fill_main_buttons_frame(self):
        """
        Fill in the main functions subframe.
        """
        
        # Create buttons
        self.start_button = tk.Button(self.main_buttons_frame,
                                      text='Start Cage',
                                      command=lambda: self.controller.start_cage())
        
        self.stop_button = tk.Button(self.main_buttons_frame,
                                     text='Stop Cage',
                                     state=tk.DISABLED,
                                     command=lambda: self.controller.stop_cage())
        
        # Position widgets
        self.start_button.grid(row=0, column=0, sticky='nsew')
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
        if not self.controller.cage.data.plots_created:
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = \
                plt.subplots(nrows=2, facecolor='lightgray')
            self.power_supplies_plot = plt.subplot(211) # Power supplies plot
            self.mag_field_plot = plt.subplot(212) # Magnetic field plot
        
        # Separated for easy recreation when making new plots after hitting stop
        self.update_plot_info()
        
        # Add to frame
        if not self.controller.cage.data.plots_created:
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                             fill=tk.BOTH,
                                             expand=True)
        
        self.controller.cage.data.plots_created = True
        self.canvas.draw()
    
    def update_connection_entries(self, ps_status, mag_status):
        """
        Update the connection frame status entries for each connected 
        device
        """
        
        # Allow the entry fields to be changed
        main_page = self.controller.frames[MainPage]
        main_page.x_ps_status_entry.configure(state=tk.NORMAL)
        main_page.y_ps_status_entry.configure(state=tk.NORMAL)
        main_page.z_ps_status_entry.configure(state=tk.NORMAL)
        main_page.mag_status_entry.configure(state=tk.NORMAL)
        
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
    
    def update_plot_info(self):
        """
        Update the data subplots.
        
                
        TODO: Update and Test
        """
        return
        #print("Updating plot info...")
        
        # Logic to make check lists are equal length in order to be plotted
        max_entries = len(self.controller.cage.data.time)
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
    
    def start_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has started.
        """
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.refresh_connections_button.config(state=tk.DISABLED)
        self.change_template_file_button.config(state=tk.DISABLED)
        self.change_calibration_file_button.config(state=tk.DISABLED)
    
    def stop_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has been stopped.
        """
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.refresh_connections_button.config(state=tk.NORMAL)
        self.change_template_file_button.config(state=tk.NORMAL)
        self.change_calibration_file_button.config(state=tk.NORMAL)
        
    def update_calibration_entry(self, file_name):
        """
        Update the calibration file name entry
        """
        
        self.calibration_file_entry.configure(state=tk.NORMAL)
        self.calibration_file_entry.delete(0, 'end')
        self.calibration_file_entry.insert(0, file_name)
        self.calibration_file_entry.configure(state="readonly")
        
    def update_template_entry(self, file_name):
        """
        Update the template file name entry
        """
        
        self.template_file_entry.configure(state=tk.NORMAL)
        self.template_file_entry.delete(0, 'end')
        self.template_file_entry.insert(0, file_name)
        self.template_file_entry.configure(state="readonly")
    
    def update_typable_entries(self):
        """
        Determine, based on the selected radiobutton in the static test 
        bar, if column should be enabled/disabled.
        """
        
        # Get desired static control type
        field_or_voltage = self.ctrl_type.get()
        
        # Set up for voltage control
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
        
        # Set up for magnetic field control
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
    
    def update_static_dynamic_buttons(self):
        """
        Determine based on the selected radiobutton if the static frame,
        or dynamic frame should be enabled/disabled.
        """
        
        # Get desired test type
        static_or_dynamic = self.test_type.get()
        
        # Set up for static test
        if static_or_dynamic == "static":
            self.template_file_entry.configure(state=tk.NORMAL)
            self.template_file_entry.delete(0, 'end')
            self.template_file_entry.configure(state="readonly")
            self.static_command_button.configure(state=tk.NORMAL)
            self.select_calibration.deselect()
            self.select_calibration.configure(state=tk.DISABLED)
        
        # Setup for dynamic test
        if static_or_dynamic == "dynamic":
            self.select_field.deselect()
            self.select_voltage.deselect()
            self.static_command_button.configure(state=tk.DISABLED)
            self.select_calibration.configure(state=tk.NORMAL)
            self.x_voltage_entry.delete(0, 'end')
            self.y_voltage_entry.delete(0, 'end')
            self.z_voltage_entry.delete(0, 'end')
            self.x_field_entry.delete(0, 'end')
            self.y_field_entry.delete(0, 'end')
            self.z_field_entry.delete(0, 'end')
            self.x_voltage_entry.configure(state=tk.DISABLED)
            self.y_voltage_entry.configure(state=tk.DISABLED)
            self.z_voltage_entry.configure(state=tk.DISABLED)
            self.x_field_entry.configure(state=tk.DISABLED)
            self.y_field_entry.configure(state=tk.DISABLED)
            self.z_field_entry.configure(state=tk.DISABLED)
            
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
