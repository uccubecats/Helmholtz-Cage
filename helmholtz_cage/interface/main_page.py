#!/usr/bin/env python

"""
  Main GUI code for the UC Helmholtz Cage

  Copyright 2018-2023 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.

  Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import csv
import os
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# Global constants
MAX_FIELD = 1.5 # Gauss
MAX_VOLTAGE = 18 # Volts
PLOT_TIMESPAN = 60 # secs
UPDATE_PLOT_TIME = 1  # secs
UPDATE_LOG_TIME = 5  # secs
UPDATE_CALIBRATE_TIME = 5  # secs
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 9)


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
        
        # Store the actual name of frame
        self.name = "MainPage"
        
        # Create subframes for main frame
        self.connect_frame = tk.Frame(container,
                                      bg="lightgray",
                                      height=50,
                                      highlightbackground="silver",
                                      highlightcolor="silver",
                                      highlightthickness=2)
        
        self.calibrate_frame = tk.Frame(container,
                                        bg="lightgray",
                                        height=50,
                                        highlightbackground="silver",
                                        highlightcolor="silver",
                                        highlightthickness=2)
        
        self.static_frame = tk.Frame(container,
                                     bg="lightgray",
                                     height=50,
                                     highlightbackground="silver",
                                     highlightcolor="silver",
                                     highlightthickness=2)
        
        self.dynamic_frame = tk.Frame(container,
                                      bg="lightgray",
                                      height=50,
                                      highlightbackground="silver",
                                      highlightcolor="silver",
                                      highlightthickness=2)
        
        self.run_frame = tk.Frame(container,
                                  bg="lightgray",
                                  height=50,
                                  highlightbackground="silver",
                                  highlightcolor="silver",
                                  highlightthickness=2)
        
        self.others_frame = tk.Frame(container,
                                     bg="lightgray",
                                     height=50,
                                     highlightbackground="silver",
                                     highlightcolor="silver",
                                     highlightthickness=2)
        
        self.plots_frame = tk.Frame(container,
                                    bg="lightgray",
                                    width=500,
                                    highlightbackground="silver",
                                    highlightcolor="silver",
                                    highlightthickness=4)
        
        # Position subframes
        self.connect_frame.grid(row=1, sticky="nsew")
        self.calibrate_frame.grid(row=2, sticky="nsew")
        self.static_frame.grid(row=3, sticky="nsew")
        self.dynamic_frame.grid(row=4, sticky="nsew")
        self.run_frame.grid(row=5, sticky="nsew")
        self.others_frame.grid(row=6, sticky="nsew")
        self.plots_frame.grid(row=0, column=1, sticky="nsew", rowspan=7)
        
        # Set weights for expansion
        [container.rowconfigure(r, weight=1) for r in range(1, 5)]
        container.columnconfigure(1, weight=1)
        
        # Fill in the subframes (function calls)
        self.fill_calibrate_frame()
        self.fill_connect_frame()
        self.fill_static_frame(parent)
        self.fill_dynamic_frame()
        self.fill_run_frame()
        self.fill_others_frame()
        self.fill_plot_frame()
    
    def fill_connect_frame(self):
        """
        Fill in the connections subframe.
        """
        
        # Create Tk entry variables
        self.x_ps_status = tk.StringVar()
        self.y_ps_status = tk.StringVar()
        self.z_ps_status = tk.StringVar()
        self.mag_status = tk.StringVar()
        
        # Create labels
        self.cxn_title = tk.Label(self.connect_frame,
                                  text="Connections",
                                  font=LARGE_FONT,
                                  bg="lightgray")
                                    
        self.unit_label = tk.Label(self.connect_frame,
                                   text="Unit",
                                   font=MEDIUM_FONT, 
                                   bg="lightgray")
        
        self.status_label = tk.Label(self.connect_frame,
                                     text="Status",
                                     font=MEDIUM_FONT,
                                     bg="lightgray")
        
        self.x_ps_label = tk.Label(self.connect_frame,
                                   text="X Power Supply",
                                   bg="lightgray",
                                   width=14)
        
        self.y_ps_label = tk.Label(self.connect_frame,
                                   text="Y Power Supply",
                                   bg="lightgray",
                                   width=14)
        
        self.z_ps_label = tk.Label(self.connect_frame,
                                   text="Z Power Supply", 
                                   bg="lightgray",
                                   width=14)
        
        self.mag_label = tk.Label(self.connect_frame,
                                  text="Magnetometer",
                                  bg="lightgray",
                                  width=14)
        
        # Create and configure connection status entries
        self.x_ps_status_entry = tk.Entry(self.connect_frame,
                                          textvariable=self.x_ps_status,
                                          width=22)
        self.x_ps_status_entry.insert(0, "Disconnected")
        self.x_ps_status_entry.configure(state="readonly")
        
        self.y_ps_status_entry = tk.Entry(self.connect_frame,
                                          textvariable=self.y_ps_status,
                                          width=22)
        self.y_ps_status_entry.insert(0, "Disconnected")
        self.y_ps_status_entry.configure(state="readonly")
        
        self.z_ps_status_entry = tk.Entry(self.connect_frame,
                                          textvariable=self.z_ps_status,
                                          width=22)
        self.z_ps_status_entry.insert(0, "Disconnected")
        self.z_ps_status_entry.configure(state="readonly")
        
        self.mag_status_entry = tk.Entry(self.connect_frame,
                                         textvariable=self.mag_status,
                                         width=22)
        self.mag_status_entry.insert(0, "Disconnected")
        self.mag_status_entry.configure(state="readonly")
        
        # Create check connection button
        self.refresh_cxns_button = tk.Button(
            self.connect_frame,
            text="Check Connections",
            command=lambda: self.controller.refresh_connections())
        
        # Position widgets
        self.cxn_title.grid(row=0, column=0, columnspan=2, pady=5,
                            sticky='nsew')
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
        self.calibration_file_entry = tk.Entry(
            self.calibrate_frame,
            textvariable=self.calibration_file_status,
            width=10)
        self.calibration_file_entry.configure(state="readonly")
        
        # Create change calibration file button
        self.change_calibration_file_button = tk.Button(
            self.calibrate_frame,
            text='Select',
            command=lambda: self.controller.change_calibration_file(),
            width=10)
        
        # Position widgets
        self.calibration_label.grid(row=0, column=0, columnspan=3, pady=5,
                                    sticky='nsew')
        self.calibration_file_label.grid(row=2, column=0)
        self.calibration_file_entry.grid(row=2, column=1)
        self.change_calibration_file_button.grid(row=2, column=2,
                                                 sticky='nsew')
    
    def fill_static_frame(self, parent):
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
        field_text = "Enter Magnetic Field \n (Gauss)".format(MAX_FIELD)
        voltage_text = "Enter Voltage \n(Max {} volts)".format(MAX_VOLTAGE)
        
        # Configure validate entry data types (must be float)
        vcmd_field = (parent.register(self.validate_field),
                      '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd_voltage = (parent.register(self.validate_voltage),
                        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        # Create test type selection buttons
        self.select_static = tk.Radiobutton(
            self.static_frame,
            text="Static Test",
            variable=self.test_type,
            command=self.update_static_dynamic_buttons,
            value="static",
            font=LARGE_FONT,
            bg="lightgray",
            highlightthickness=0)
        
        self.select_field = tk.Radiobutton(
            self.static_frame,
            text=field_text,
            variable=self.ctrl_type,
            value="field",
            command=self.update_typable_entries,
            bg="lightgray",
            highlightthickness=0,
            width=15)
        
        self.select_voltage = tk.Radiobutton(
            self.static_frame,
            text=voltage_text,
            variable=self.ctrl_type,
            value="voltage",
            command=self.update_typable_entries,
            bg="lightgray",
            highlightthickness=0,
            width=15)
        
        # Create labels
        self.x_field_label = tk.Label(self.static_frame,
                                      text="x:",
                                      font=LARGE_FONT,
                                      bg="lightgray")
        
        self.x_voltage_label = tk.Label(self.static_frame,
                                        text="x:",
                                        font=LARGE_FONT,
                                        bg="lightgray")
        
        self.y_field_label = tk.Label(self.static_frame,
                                      text="y:",
                                      font=LARGE_FONT,
                                      bg="lightgray")
        
        self.y_voltage_label = tk.Label(self.static_frame,
                                        text="y:",
                                        font=LARGE_FONT,
                                        bg="lightgray")
        
        self.z_field_label = tk.Label(self.static_frame,
                                      text="z:",
                                      font=LARGE_FONT,
                                      bg="lightgray")
        
        self.z_voltage_label = tk.Label(self.static_frame,
                                        text="z:",
                                        font=LARGE_FONT,
                                        bg="lightgray")
                                        
        # Create value entries
        self.x_field_entry = tk.Entry(self.static_frame,
                                      state=tk.DISABLED,
                                      validate='key',
                                      validatecommand=vcmd_field,
                                      textvariable=self.x_field,
                                      width=10)
        
        self.x_voltage_entry = tk.Entry(self.static_frame,
                                        state=tk.DISABLED,
                                        validate='key',
                                        validatecommand=vcmd_voltage,
                                        textvariable=self.x_voltage,
                                        width=10)
        
        self.y_field_entry = tk.Entry(self.static_frame,
                                      state=tk.DISABLED,
                                      validate='key',
                                      validatecommand=vcmd_field,
                                      textvariable=self.y_field,
                                      width=10)
        
        self.y_voltage_entry = tk.Entry(self.static_frame,
                                        state=tk.DISABLED,
                                        validate='key',
                                        validatecommand=vcmd_voltage,
                                        textvariable=self.y_voltage,
                                        width=10)
        
        self.z_field_entry = tk.Entry(self.static_frame,
                                      state=tk.DISABLED,
                                      validate='key',
                                      validatecommand=vcmd_field,
                                      textvariable=self.z_field,
                                      width=10)
        
        self.z_voltage_entry = tk.Entry(self.static_frame,
                                        state=tk.DISABLED,
                                        validate='key',
                                        validatecommand=vcmd_voltage,
                                        textvariable=self.z_voltage,
                                        width=10)
        
        # Create static value command button
        self.static_command_button = tk.Button(
            self.static_frame,
            text='Command Values',
            command=lambda: self.controller.command_static_value(),
            width=15,
            state=tk.DISABLED)
        
        # Position widgets
        self.select_static.grid(row=0, column=0, columnspan=4, pady=5,
                                sticky='nsew')
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
        self.static_command_button.grid(row=5, column=0, columnspan=4,
                                        sticky='ns')
    
    def fill_dynamic_frame(self):
        """
        Fill in the dynamic-test subframe.
        """
        
        # Create Tk entry variables
        self.template_file_status_text = tk.StringVar()
        self.is_calibration_run = tk.BooleanVar()
        
        # Create test type selection button (dynamic)
        self.select_dynamic =  tk.Radiobutton(
            self.dynamic_frame,
            text="Dynamic Test",
            variable=self.test_type,
            command=self.update_static_dynamic_buttons,
            value="dynamic",
            font=LARGE_FONT,
            bg="lightgray",
            highlightthickness=0,
            width=15)
        
        # Create label
        self.template_file_label = tk.Label(self.dynamic_frame,
                                            text="Template file:",
                                            bg="lightgray",
                                            width=12)
        
        # Create and configure template file name entry
        self.template_file_entry = tk.Entry(
            self.dynamic_frame,
            textvariable=self.template_file_status_text,
            width=10)
        self.template_file_entry.configure(state="readonly")
        
        # Create change template file button
        self.change_template_file_button = tk.Button(
            self.dynamic_frame,
            text='Select',
            command=lambda: self.controller.change_template_file(),
            width=10)
        
        # Create button for calibrating from template file
        self.select_calibration = tk.Checkbutton(
            self.dynamic_frame,
            text="Calibrate from template",
            variable=self.is_calibration_run,
            bg="lightgray",
            highlightthickness=0,
            state=tk.DISABLED)
        
        # Position widgets
        self.select_dynamic.grid(row=0, column=0, columnspan=4, pady=5,
            sticky='nsew')
        self.template_file_label.grid(row=1, column=0)
        self.template_file_entry.grid(row=1, column=1)
        self.change_template_file_button.grid(row=1, column=2, sticky='nsew')
        self.select_calibration.grid(row=2, column=0, columnspan=3,
            sticky="nsew")
    
    def fill_run_frame(self):
        """
        Fill in the main functions subframe.
        """
        
        # Create buttons
        self.start_button = tk.Button(
            self.run_frame,
            text='Start Cage',
            command=lambda: self.controller.start_cage())
        
        self.stop_button = tk.Button(
            self.run_frame,
            text='Stop Cage',
            state=tk.DISABLED,
            command=lambda: self.controller.stop_cage())
        
        # Position widgets
        self.start_button.grid(row=0, column=0, sticky='nsew')
        self.stop_button.grid(row=0, column=1, sticky='nsew')
    
    def fill_others_frame(self):
        """
        Fill in the other menu frame (TODO).
        """
        pass
        # # Create buttons
        # self.config_button = tk.Button(
            #self.others_frame,
            #text='Options',
            #command=lambda: self.controller.show_config_page())
        
        # # Position widgets
        # self.config_button.grid(row=0, column=0, sticky='nsew')
    
    def fill_plot_frame(self):
        """
        Fill in the main plot subframe.
        """
        
        # Create figure and initialize plots
        if not self.controller.cage.data.plots_created:
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = \
                plt.subplots(nrows=2, facecolor='lightgray')
            self.power_supplies_plot = plt.subplot(211)
            self.mag_field_plot = plt.subplot(212)
        
        # Separated for easy recreation for new plots after hitting stop
        self.update_plot_info(self.controller.cage.data)
        
        # Add to frame
        if not self.controller.cage.data.plots_created:
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                             fill=tk.BOTH,
                                             expand=True)
        
        # Set flag variable
        self.controller.cage.data.plots_created = True
        
        # Draw plots on subframe
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
    
    def update_plot_info(self, data):
        """
        Update the data subplots.
        
                
        TODO: Rework
        """
        
        # Logic to make check lists are equal length in order to be plotted
        # TODO: Move to 'Data' Class
        max_entries = len(data.time)
        if max_entries == 0:
            max_entries = 1
        if len(data.time) != max_entries:
            data.time = [0] * max_entries
        if len(data.Vx) != max_entries:
            data.x_out = [0]*max_entries
        if len(data.Vy) != max_entries:
            data.y_out = [0]*max_entries
        if len(data.Vz) != max_entries:
            data.z_out = [0]*max_entries
        if len(data.x_req) != max_entries:
            data.x_req = [0]*max_entries
        if len(data.y_req) != max_entries:
            data.y_req = [0]*max_entries
        if len(data.z_req) != max_entries:
            data.z_req = [0]*max_entries
        if len(data.Bx) != max_entries:
            data.Bx = [0]*max_entries
        if len(data.By) != max_entries:
            data.By = [0]*max_entries
        if len(data.Bz) != max_entries:
            data.Bz = [0]*max_entries
        
        # Get voltage graph axis limits
        # TODO: Change
        power_supplies_list = (data.Vx + data.Vy + data.Vz)
        if data.req_type == "voltage":
             power_supplies_list.append(data.x_req + data.y_req + data.z_req)

        max_y_plot_one = 1.2*max(power_supplies_list)
        if max_y_plot_one < 1:
            max_y_plot_one = 1
        min_y_plot_one = min(power_supplies_list)
        
        # Get magnetic field graph axis limits
        mag_field_list = (data.Bx + data.By + data.Bz)
        if data.req_type == "field":
            mag_field_list = (data.x_req + data.y_req + data.z_req)
                                     
        max_y_plot_two = 1.2*max(mag_field_list)
        if max_y_plot_two < 1:
            max_y_plot_two = 1
        min_y_plot_two = min(mag_field_list)
        
        # Plot
        # Power supply voltage graph
        self.power_supplies_plot.plot(data.time, data.Vx, 'r',
                                      label='x_ps_output')
        self.power_supplies_plot.plot(data.time, data.Vy, 'g',
                                      label='y_ps_output')
        self.power_supplies_plot.plot(data.time, data.Vz, 'b',
                                      label='z_ps_output')
        if data.req_type == "voltage":
            self.power_supplies_plot.plot(data.time, data.x_req, 'r--',
                                          label='x_ps_requested')
            self.power_supplies_plot.plot(data.time, data.y_req, 'g--',
                                          label='y_ps_requested')
            self.power_supplies_plot.plot(data.time, data.z_req, 'b--',
                                          label='z_ps_requested')
        
        self.plot_1_axes = self.power_supplies_plot.axes
        self.plot_1_axes.set_ylim(min_y_plot_one, max_y_plot_one)
        
        # Magnetic field graph
        self.mag_field_plot.plot(data.time, data.Bx, 'r',
                                 label='x_mag_field_actual')
        self.mag_field_plot.plot(data.time, data.By, 'g',
                                 label='y_mag_field_actual')
        self.mag_field_plot.plot(data.time, data.Bz, 'b',
                                 label='z_mag_field_actual')
        if data.req_type == "field":
            self.mag_field_plot.plot(data.time, data.x_req, 'r--',
                                     label='x_mag_field_requested')
            self.mag_field_plot.plot(data.time, data.y_req, 'g--',
                                     label='y_mag_field_requested')
            self.mag_field_plot.plot(data.time, data.z_req, 'b--',
                                     label='z_mag_field_requested')
        
        self.plot_2_axes = self.mag_field_plot.axes
        self.plot_2_axes.set_ylim(min_y_plot_two, max_y_plot_two)
        
        # Combine plots for GUI display
        self.power_supplies_plot.get_shared_x_axes().join(
            self.power_supplies_plot, self.mag_field_plot)
        self.power_supplies_plot.set_xticklabels([])
        
        self.power_supplies_plot.set_facecolor("whitesmoke")
        self.power_supplies_plot.set_title("Voltage")
        self.power_supplies_plot.set_ylabel("Volts")
        
        self.mag_field_plot.set_facecolor("whitesmoke")
        self.mag_field_plot.set_title("Magnetic Flux Density")
        self.mag_field_plot.set_xlabel("Seconds")
        self.mag_field_plot.set_ylabel("Gauss")
        
        # Create plot titles (only needs to be run once)
        if data.plot_titles == "None": # only need to do this once for plots
            self.power_supplies_plot.legend(
                loc='upper center',
                bbox_to_anchor=(0.5, 1.00),
                ncol=3,
                fancybox=True,
                prop={'size': 7})
            self.mag_field_plot.legend(
                loc='upper center',
                bbox_to_anchor=(0.5, 1.0),
                ncol=3,
                fancybox=True,
                prop={'size': 7})
            data.plot_titles = "Exist"
            
    def clear_plot_frame(self):
        """
        When stopping the current run, clear the plot frame and reset it
        to run again.
        """
        
        # Clear both plots in plot frame
        self.power_supplies_plot.clear()
        self.mag_field_plot.clear()
        
        # Recreate titles and axis information
        self.fill_plot_frame()
    
    def start_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has started.
        """
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.refresh_cxns_button.config(state=tk.DISABLED)
        self.change_template_file_button.config(state=tk.DISABLED)
        self.change_calibration_file_button.config(state=tk.DISABLED)
    
    def stop_cage_update_buttons(self):
        """
        Update the status of buttons after the cage has been stopped.
        """
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.refresh_cxns_button.config(state=tk.NORMAL)
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
        static_or_dynamic = self.test_type.get()
        
        # Select static test if not selected already
        if static_or_dynamic != "static":
            self.template_file_entry.configure(state=tk.NORMAL)
            self.template_file_entry.delete(0, 'end')
            self.template_file_entry.configure(state="readonly")
            self.static_command_button.configure(state=tk.NORMAL)
            self.select_calibration.deselect()
            self.select_calibration.configure(state=tk.DISABLED)
            self.select_static.select()
        
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
                    if value <= MAX_FIELD:
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
                    if value <= MAX_VOLTAGE:
                        return True
                    else:
                        return False
                
                except ValueError:
                    return False
            else:
                return False
        else:
            return True
