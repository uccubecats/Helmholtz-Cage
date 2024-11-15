#!/usr/bin/env python3

"""
  Main application program for the UC Helmholtz Cage.
  
  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import datetime
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import traceback

from data.calibration import Calibration
from hardware.helmholtz_cage import HelmholtzCage
from interface.config_page import ConfigurationPage
from interface.main_page import MainPage
from interface.help_page import HelpPage
from interface.calibration_page import CalibrationPage
from utilities.template import retrieve_template, check_template_values
from utilities.config import retrieve_configuration_info


# Global constants
UPDATE_PLOT_TIME = 1  # secs


class CageApp(tk.Tk):
    """
    An object class for main Helmholtz Cage application.
    """
    
    def __init__(self, *args, **kwargs):
        
        # Get important directories
        self.cur_path = os.getcwd()
        self.main_path = os.path.abspath(os.path.join(self.cur_path, os.pardir))
        self.config_path = os.path.join(self.main_path, "helmholtz_cage")
        self.calibration_path = os.path.join(self.main_path, "calibrations")
        self.template_path = os.path.join(self.main_path, "templates")
        
        # Retrieve system configuration information
        configs = retrieve_configuration_info(self.config_path)
        ps_config = configs["power_supplies"]
        mag_config = configs["magnetometer"]
        
        # Initialize frame
        tk.Tk.__init__(self, *args, **kwargs)
        
        # Set title
        self.title = "Helmholtz Cage"
        tk.Tk.wm_title(self, self.title)
        
        # Load Icon (TODO: add ico file for cage)
        # tk.Tk.iconbitmap(self, default="icon.ico")
        
        # Expand frame to window
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Initialize Helmholtz Cage interface
        self.cage = HelmholtzCage(self.main_path, ps_config, mag_config)
        
        # Set parameters
        self.log_data = False
        self.is_calibration_run = False
        
        # Intialize frames top of each other
        self.frames = {}
        for Frame in (MainPage, HelpPage):
            frame = Frame(container, self)
            self.frames[Frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        
        # Show the main page
        self.show_frame(MainPage)
    
    def refresh_connections(self):
        """
        Refresh the connections to the connected instruments (activated 
        by the "Check Connenctions" button).
        """
        
        # Attempt connection to intstrumentation
        # NOTE: Must be done in try/except to set text back to readonly
        try:
            ps_status, mag_status = self.cage.connect_to_instruments()
        except Exception as err: #TODO: Improve error handling here
            print("ERROR: {}".format(err))
            ps_status = [False, False, False]
            mag_status = False
        
        # Update the GUI connection fields
        self.frames[MainPage].update_connection_entries(ps_status, mag_status)
        
    def set_logging_option(self):
        """
        Set data logging option, enabling/disabling writing data from a
        run to storage.
        """
        
        self.log_data = self.frames[MainPage].log_data_option.get()
        
    def set_calibration_option(self):
        """
        Set the calibration option, indicating that this dynamic run 
        should be used to calibrate the cage.
        """
        
        self.is_calibration_run = self.frames[MainPage].is_calibration_run.get()
    
    def start_cage(self):
        """
        Start a Helmholz Cage test run (activated by the "Start Cage" 
        button).
        """
        
        # Retrieve test options
        static_or_dynamic = self.frames[MainPage].test_type.get()
        field_or_voltage = self.frames[MainPage].ctrl_type.get()
        
        # Command the cage to start
        success = self.cage.start_cage(static_or_dynamic, field_or_voltage,
                                       self.is_calibration_run)
        
        # Start tracking plots
        # TODO: Rework?
        if success:
            self.frames[MainPage].power_supplies_plot.clear()
            self.frames[MainPage].mag_field_plot.clear()
            self.cage.data.plot_titles = "None"
            
            # Record start time
            self.cage.data.start_time = datetime.datetime.now()
                
            # Start updating plot with live data
            self.update_plots_at_runtime()
            
            # Start control looping for dynamic tests
            if static_or_dynamic == "dynamic":
                self.loop_dynamic_run()
            
            # Update buttons
            self.frames[MainPage].start_cage_update_buttons()
            print("Session starting")
        
        # Notify user that session is not started
        else:
            print("Session start aborted")
    
    def update_plots_at_runtime(self):
        """
        Update the GUI plots at runtime for the cage, using the tk.after
        method.
        """
        
        # Only run function if cage is still running
        if self.cage.is_running:
            
            # Retrieve current data 
            data_now = self.cage.update_data()
            
            # Redraw plots with newest data
            self.frames[MainPage].fill_plot_frame()
            
            # Set next update loop
            self.frames[MainPage].after(UPDATE_PLOT_TIME*1000,
                                        self.update_plots_at_runtime)
    
    def loop_dynamic_run(self):
        """
        Loop once through a dynamic run of the Cage, with the next cycle
        time being determined from template file times.
        
        TODO: Test under real conditions (will threading be necessary?)
        """
        
        # Loop through one cycle of dynamic run
        if self.cage.is_running:
            dt, finished = self.cage.run_once()
            
            # Check if finished, otherwise prepare next loop
            if not finished:
                self.frames[MainPage].after(int(dt*1000), self.loop_dynamic_run)
            else:
                self.stop_cage()
    
    def command_static_value(self):
        """
        Based on the type of control send an appropriate static value
        command (based on user input) to the cage.
        """
        
        # Get control type
        field_or_voltage = self.frames[MainPage].ctrl_type.get()
        
        # If field control, send desired flux density (3-axis)
        if field_or_voltage == "field":
            Bx = float(self.frames[MainPage].x_field.get())
            By = float(self.frames[MainPage].y_field.get())
            Bz = float(self.frames[MainPage].z_field.get())
            self.cage.set_field_strength(Bx, By, Bz)
            
            # Store requested values
            self.cage.x_req = Bx
            self.cage.y_req = By
            self.cage.z_req = Bz
        
        # If voltage control, send desired voltages
        elif field_or_voltage == "voltage":
            Vx = float(self.frames[MainPage].x_voltage.get())
            Vy = float(self.frames[MainPage].y_voltage.get())
            Vz = float(self.frames[MainPage].z_voltage.get())
            self.cage.set_coil_voltages(Vx, Vy, Vz)
            
            # Store requested values
            self.cage.x_req = Vx
            self.cage.y_req = Vy
            self.cage.z_req = Vz
            
    def stop_cage(self):
        """
        Stop the current run of the Helmholtz Cage (activated by the 
        "Stop Cage" button).
        """
        
        # Command the cage to stop
        success = self.cage.stop_cage()
        
        # Reset GUI and data
        if success:
            print("Session ended successfully")
            
            # Log data if requested
            if self.log_data:
                self.cage.data.write_to_file()
            
            # Calibarate cage from data if specified
            if self.is_calibration_run:
                self.cage.calibrate(self.calibration_path)
                self.show_calibration_page()
                
            else:
                # Clear data for next run
                self.cage.data.clear_data()
                
                # Update buttons
                self.frames[MainPage].stop_cage_update_buttons()
                
                # Clear the figure off and recreate plot titles
                self.frames[MainPage].clear_plot_frame()
        
        # Warn user if the cage isn't shutting down
        else:
            print("ERROR: Unable to command cage to stop")
    
    def handle_calibration_output(self, accepted):
        """
        Deal with the calibration results based on user selection.
        """
        
        # If accepted, write to file
        if accepted:
            self.cage.calibration.write_to_file()
            self.cage.has_calibration = True
            print("Calibration accepted")
            
            # Put calibration file name into GUI entry
            file_name = self.cage.calibration.file_name
            self.frames[MainPage].update_calibration_entry(file_name)
        
        # Otherwise, delete calibration
        else:
            self.cage.calibration = None
            self.cage.has_calibration = False
            print("Calibration rejected")
            
        # Clear data for next run
        self.cage.data.clear_data()
                
        # Update buttons
        self.frames[MainPage].stop_cage_update_buttons()
        
        # Clear the figure off and recreate plot titles
        self.frames[MainPage].clear_plot_frame()
    
    def change_calibration_file(self):
        """
        Load the user specifed calibration file.
        """
        
        # Ask the user for the calibration file
        file_name = filedialog.askopenfilename(initialdir=self.calibration_path,
                                               filetypes=(("csv file","*.csv"),
                                                          ("All files","*.*")))
        
        # Retrieve and check the calibration
        calibration_name = os.path.basename(file_name)
        calibration = Calibration(self.calibration_path, calibration_name)
        success = calibration.load_from_file()
        
        # Give calibration to the Helmholtz Cage
        if success:
            print(calibration)
            self.cage.calibration = calibration
            self.cage.has_calibration = True
            self.cage.data.calibration_file = file_name
            
            # Put calibration file name into GUI entry
            self.frames[MainPage].update_calibration_entry(calibration_name)
        else:
            print("ERROR: Unable to load the selected calibration file")
    
    def change_template_file(self):
        """
        Load the user specifed template file.
        """
        
        # Ask the user for the template file
        file_name = filedialog.askopenfilename(initialdir=self.template_path,
                                               filetypes=(("csv file","*.csv"),
                                                          ("All files","*.*")))
        
        # Retrieve and check template
        template_name = os.path.basename(file_name)
        template = retrieve_template(self.template_path, template_name)
        is_okay = check_template_values(template, [5.0, 1.5]) # <--TODO: replace these
        
        # Give template to the Helmholtz Cage
        if is_okay:
            self.cage.template = template
            self.cage.has_template = True
            self.cage.data.template_file = file_name
            
            # Put template file name into GUI entry
            self.frames[MainPage].update_template_entry(template_name)
        else:
            print("ERROR: Unable to load the selected template file")
    
    def show_frame(self, cont):
        """
        Switch to another frame.
        """
        
        # Determine which page needs to come up
        frame = self.frames[MainPage]
        
        # Show the frame
        frame.tkraise()
    
    def show_config_page(self):
        """
        TODO
        """
        
        self.config_page = ConfigurationPage(self)
    
    def show_calibration_page(self):
        """
        Display calibration data within calibration page GUI.
        """
        
        self.calibration_page = CalibrationPage(self, self.cage.calibration,
                                                self.cage.data)
    
    def close_app(self):
        """
        Close the app when the user exits via the GUI window.
        """
        
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.quit()
    
    def cleanup(self):
        """
        Perform any cleanup activities needed before shutting down.
        """
        
        # If cage is still running, stop current session
        if self.cage.is_running:
            self.stop_cage()
            
        # Shutdown cage
        self.cage.shutdown()


if __name__ == "__main__":
    
    try:
        app = CageApp()
        app.minsize(width=250, height=600)
        app.protocol("WM_DELETE_WINDOW", app.close_app)
        app.mainloop()
    
    except NotImplementedError as err:
        print("ERROR: {}".format(err))
    
    except KeyboardInterrupt:
        print("")
    
    except Exception:
        traceback.print_exc()
        
    finally:
        print("Shutting down program")
        try:
            app.cleanup()
        except NameError:
            pass
