#!/usr/bin/env python

"""
  Main application program for the UC Helmholtz Cage.
  
  Copyright 2022-2023 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
  
  WARN: Very work in progress.
"""


import datetime
import os
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import traceback

from data.calibration import Calibration
from hardware.helmholtz_cage import HelmholtzCage
from interface.config_page import ConfigurationPage
from interface.main_page import MainPage
from interface.help_page import HelpPage
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
        except Exception as err:
            print("Could not connect instruments | {}".format(err))
            
        # Update the GUI connection fields
        self.frames[MainPage].update_connection_entries(ps_status, mag_status)
        
    def start_cage(self):
        """
        Start a Helmholz Cage test run (activated by the "Start Cage" 
        button).
        """
        
        # Retrieve test options
        static_or_dynamic = self.frames[MainPage].test_type.get()
        field_or_voltage = self.frames[MainPage].ctrl_type.get()
        
        # Command the cage to start
        success = self.cage.start_cage(static_or_dynamic, field_or_voltage)
        
        # Start tracking plots
        if success:
            try:
                self.frames[MainPage].power_supplies_plot.cla()
                self.frames[MainPage].mag_field_plot.cla()
                self.cage.data.plot_titles = "None"
                #data_now = self.cage.data
                #self.frames[MainPage].update_plot_info(data_now)
                
                # Record start time
                self.cage.data.start_time = datetime.datetime.now()
                
                # Start updating plot with live data
                self.update_plots_at_runtime()

                # Update buttons
                self.frames[MainPage].start_cage_update_buttons()
                print("Session starting")
                
            except Exception as err:
                print("ERROR: Session failed to start | {}".format(err))
                self.cage.is_running = False
    
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
            self.frames[MainPage].update_plot_info(data_now)
            self.frames[MainPage].fill_plot_frame()
            
            # Set next update loop
            self.frames[MainPage].after(UPDATE_PLOT_TIME*1000,
                                        self.update_plots_at_runtime)
    
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
            # If cage is started again in current session, new log file is created
            # TODO
            
            # Update buttons
            self.frames[MainPage].stop_cage_update_buttons()
            
        # Warn user if the cage isn't shutting down
        else:
            print("ERROR: Unable to command cage to stop")
    
    def change_calibration_file(self):
        """
        Load the user specifed calibration file.
        
        TODO: Test
        """
        
        # Ask the user for the calibration file
        search_dir = os.path.join(self.main_path, "calibrations")
        file_name = filedialog.askopenfilename(initialdir=search_dir,
                                               filetypes=(("csv file","*.csv"),
                                                          ("All files","*.*")))
        
        # Retrieve and check the calibration
        calibration_dir, calibration_name = os.path.split(file_name)
        calibration = Calibration(calibration_dir, calibration_name)
        success = calibration.load_calibration_file()
        
        # Give calibration to the Helmholtz Cage
        if success:
            self.cage.calibration = calibration
            self.cage.has_calibration = True
            self.cage.data.calibration_file = file_name
            
            # Put calibration file name into GUI entry
            self.frames[MainPage].update_calibration_entry(file_name)
        else:
            print("ERROR: Unable to load selected calibration file")
    
    def change_template_file(self):
        """
        Load the user specifed template file.
        """
        
        # Ask the user for the template file
        search_dir = os.path.join(self.main_path, "templates")
        file_name = filedialog.askopenfilename(initialdir=search_dir,
                                               filetypes=(("csv file","*.csv"),
                                                          ("All files","*.*")))
        
        # Retrieve and check template
        template_dir, template_name = os.path.split(file_name)
        template = retrieve_template(template_dir, template_name)
        is_okay = check_template_values(template, [5.0, 1.5]) # <--TODO: replace these
        
        # Give template to the Helmholtz Cage
        if is_okay:
            self.cage.template = template
            self.cage.has_template = True
            self.cage.data.template_file = file_name
            
            # Put template file name into GUI entry
            self.frames[MainPage].update_template_entry(file_name)
        else:
            print("ERROR: Unable to load selected template file")

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
        
        """
        
        self.config_page = ConfigurationPage(self)
        
        
    def close_app(self):
        """
        Close the app when exiting from the main window.
        """
        
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            print("Shutting down program")
            self.quit()


if __name__ == "__main__":
    
    try:
        app = CageApp()
        app.minsize(width=250, height=600)
        app.protocol("WM_DELETE_WINDOW", app.close_app)
        app.mainloop()
        
    except Exception:
        traceback.print_exc()
        
    except KeyboardInterrupt:
        print("")
