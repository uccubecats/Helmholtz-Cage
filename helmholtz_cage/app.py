#!/usr/bin/env python

"""
  Main application program for the UC Helmholtz Cage.
  
  Copyright 2021 UC CubeCats
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
import traceback

from hardware.helmholtz_cage import HelmholtzCage
from interface.main_page import MainPage
from interface.help_page import HelpPage


# Global constants
UPDATE_PLOT_TIME = 1  # secs


def update_plots_runtime():
    """
    Threaded function to update the GUI plots at runtime for the cage.
    """
    
    # Check that cage is still running
    if app.cage.is_running:
        
        # Setup next update of plots
        threading.Timer(UPDATE_PLOT_TIME, update_plot_at_runtime).start()
        
        # Get current data from the cage
        data_now = app.cage.data.get_current_data()
        
        # Give to plot to update
        app.frame[MainPage].update_plot_info(data)
    
    # Notify the user when done
    else:
        print("Stopping plot updates")


class CageApp(tk.Tk):
    """
    An object class for main Helmholtz Cage application.
    """
    
    def __init__(self, *args, **kwargs):
        
        # Get important directories
        main_path = os.getcwd()
        
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
        self.cage = HelmholtzCage(main_path)

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
        
        TODO: Test
        """
        
        # Attempt connection to intstrumentation
        # NOTE: Must be done in try/except to set text back to readonly
        try:
            ps_status, mag_status = cage.connect_to_instruments() #TODO: update name of this function in helmholtz cage code
        except Exception as err:
            print("Could not connect instruments | {}".format(err))
            
        # Update the GUI connection fields
        self.frames[MainPage].update_connections_entries(ps_status, mag_status)
        
    def start_cage(self):
        """
        Start a Helmholz Cage test run (activated by the "Start Cage" 
        button).
        
        TODO: Test
        """
        
        # Retrieve test options
        static_or_dynamic = self.frames[MainPage].static_or_dynamic.get()
        field_or_voltage = self.frames[MainPage].field_or_voltage.get()
        
        # Command the cage to start
        success = cage.start_cage(static_or_dynamic, field_or_voltage)
        
        # Start tracking plots
        if success:
            # print("found Start Cage text on start button")
            self.frames[MainPage].power_supplies_plot.cla()
            self.frames[MainPage].mag_field_plot.cla()
            
            # Update plots
            cage.data.plot_titles = "None"
            self.frames[MainPage].update_plot_info()
            
            # Record start time
            self.cage.data.start_time = datetime.datetime.now()

            # Start updating plot with live data
            update_plots_runtime()

            # Update buttons
            self.frames[MainPage].start_cage_update_buttons()
        
    def stop_cage(self):
        """
        Stop the current run of the Helmholtz Cage (activated by the 
        "Stop Cage" button).
        
        TODO: Test
        """
        
        # Command the cage to stop
        success = cage.stop_cage()
        
        # Reset GUI and data
        if success:
            # If cage is started again in current session, new log file is created
            # TODO
            
            # Update buttons
            self.stop_cage_update_buttons()
            
        # Warn user if the cage isn't shutting down
        else:
            print("ERROR: Unable to command cage to stop")
        
    def show_frame(self, cont):
        """
        Switch to another frame.
        """
        
        frame = self.frames[cont]
        frame.tkraise()


if __name__ == "__main__":
    
    try:
        app = CageApp()
        app.minsize(width=250, height=600)
        app.mainloop()
        
    except Exception:
        traceback.print_exc()
