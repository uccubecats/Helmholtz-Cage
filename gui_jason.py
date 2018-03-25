# Written by Jason Roll, contact: rolljn@mail.uc.edu, 513-939-9800
# Last modified: 180131
# Don't try to edit this in idle. Are you insane? Get pycharm community edition or at least NP++

# --------------------------------------------------------------------------------
# PYTHON IMPORTS
import tkinter as tk
import os
from os import listdir
from os.path import isfile, join
from tkinter import filedialog
import threading
import datetime
import csv
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TKAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

# OTHER CODE IMPORTS
from connections import *

# --------------------------------------------------------------------------------
# CONSTANTS
max_field_value = 13
max_voltage_value = 1
update_log_time = 5 # seconds
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 9)
cwd = os.getcwd()
downArrow = u"\u25BC"

# --------------------------------------------------------------------------------
# FUNCTIONS - file/program management
def open_csv(app):
    filePath = filedialog.askopenfilename(initialdir=cwd,
                               filetypes=(("CSV File",".csv"),("All Files","*.*")),
                               title="Open File")
    
    # incase filename is typed by user and invalid
    try:
        with open(filePath) as fileData:
            contents=fileData
    except:
        print("File does not exist.")
        return
    Data.file_contents=contents
    Data.file_name=os.path.split(filePath)[-1]

    # update the title to include the fileName
    app.wm_title("Helmholtz Cage "+fileName)

# --------------------------------------------------------------------------------
# CLASSES

# where opened file data will be stored
class Data():
    # this sets initial values for the class attributes 
    def __init__(self):


       # gui related class attributes

       self.plots_created = False # flag variable so plots are only created once
       self.plot_titles = "" # flag variable so titles are only added the first time data is logged

       # these attributes are used so cage is only updated when start/update button is hit
       self.active_x_voltage_requested = 0
       self.active_y_voltage_requested = 0
       self.active_z_voltage_requested = 0

       # template related data
       self.template_file = "none found"
       self.template_voltages_x = [] # all x voltages to send to cage
       self.template_voltages_y = [] # corresponding y voltages to send to cage
       self.template_voltages_z = [] # corresponding z voltages to send to cage

       # calibration related data
       self.calibration_file = "none found"
       self.calibration_voltages_x = [] # all x voltages that were used to get a magnetic field from cage
       self.calibration_voltages_y = [] # corresponding y voltages that were sent to cage
       self.calibration_voltages_z = [] # corresponding z voltages that were sent to cage
       self.calibration_mag_field_x = [] # the mag field x component obtained from the corresponding x,y,z voltage
       self.calibration_mag_field_y = [] # same but y component
       self.calibration_mag_field_z = [] # same but z component

       # logging runs class attributes
       self.log_filename = ""
       self.time = []
       self.x_req = []
       self.y_req = []
       self.z_req = []
       self.x_out = []
       self.y_out = []
       self.z_out = []
       self.x_mag_field_actual = []
       self.y_mag_field_actual = []
       self.z_mag_field_actual = []
       self.x_mag_field_requested = []
       self.y_mag_field_requested = []
       self.z_mag_field_requested = []

class CageApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        # initialize frame
        tk.Tk.__init__(self,*args,**kwargs)

        # title info
        self.title = "Helmholtz Cage"
        tk.Tk.wm_title(self, self.title)
        # tk.Tk.iconbitmap(self, default="icon.ico") #*** add ico file for cage

        # make frame expand to window 
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # frames are laid ontop of each other, startPage shown first
        self.frames = {}
        for Frame in (MainPage, HelpPage):
            frame = Frame(container, self)
            self.frames[Frame] = frame
            frame.grid(row = 0, column = 0, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        self.show_frame(MainPage)

    def get_page(self, page_name):
        return self.frames[page_name]
        
    # call this to switch frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def temp_cmd(self, cont):
        pass

    def refresh_connections(self, cont):
        main_page = self.frames[MainPage]

        # allow the entry fields to be changed
        main_page.x_ps_status_entry.configure(state=tk.NORMAL)
        main_page.y_ps_status_entry.configure(state=tk.NORMAL)
        main_page.z_ps_status_entry.configure(state=tk.NORMAL)
        main_page.mag_status_entry.configure(state=tk.NORMAL)


        # must be done in try/except to set text back to readonly
        try:
            connected_devices = instruments.make_connections()
        except: pass

        # for applicable connections, delete the entry and update it
        if not (instruments.x == "No connection"):
            main_page.x_ps_status_entry.delete(0, tk.END)
            main_page.x_ps_status_entry.insert(tk.END,"Connected")

        if not (instruments.y == "No connection"):
            main_page.y_ps_status_entry.delete(0, tk.END)
            main_page.y_ps_status_entry.insert(tk.END,"Connected")

        if not (instruments.z == "No connection"):
            main_page.z_ps_status_entry.delete(0, tk.END)
            main_page.z_ps_status_entry.insert(tk.END,"Connected")

        if not (instruments.mag == "No connection"):
            main_page.mag_status_entry.delete(0, tk.END)
            main_page.mag_status_entry.insert(tk.END,"Connected")

        # set the entry fields back to read only ***not working??
        main_page.x_ps_status_entry.configure(state="readonly")
        main_page.y_ps_status_entry.configure(state="readonly")
        main_page.z_ps_status_entry.configure(state="readonly")
        main_page.mag_status_entry.configure(state="readonly")

    def start_field(self, cont):

        main_page = self.frames[MainPage]

        static_or_dynamic = main_page.static_or_dynamic.get()
        field_or_voltage = main_page.field_or_voltage.get()

        if static_or_dynamic == "static":
            if field_or_voltage == "voltage":
                print("attempting to send specified voltages...")

                if main_page.x_voltage.get() == "": main_page.x_voltage.set(0)
                if main_page.y_voltage.get() == "": main_page.y_voltage.set(0)
                if main_page.z_voltage.get() == "": main_page.z_voltage.set(0)

                data.active_x_voltage_requested = float(main_page.x_voltage.get())
                data.active_y_voltage_requested = float(main_page.y_voltage.get())
                data.active_z_voltage_requested = float(main_page.z_voltage.get())
                instruments.send_voltage(data.active_x_voltage_requested,
                                         data.active_y_voltage_requested,
                                         data.active_z_voltage_requested)

            if field_or_voltage == "field":
                print("attempting to send specified magnetic field...")
                x_field = main_page.x_field.get()
                y_field = main_page.y_field.get()
                z_field = main_page.z_field.get()
                send_field(x_field, y_field, z_field)

        if static_or_dynamic == "dynamic":
            print("Dynamic field not supported yet")

        if not hasattr(instruments, "connections_checked"):
            print("Check connections before starting")
        else:
            if main_page.start_button["text"] == 'Start Field':
                instruments.log_data = "ON"
                print("found Start Field text on start button")

                main_page.power_supplies_plot.cla()
                main_page.mag_field_plot.cla()

                data.plot_titles = "None"
                main_page.update_plot_info()

                (data.time, data.x_out, data.y_out, data.z_out, data.x_req, data.y_req, data.z_req,
                data.x_mag_field_actual, data.y_mag_field_actual, data.z_mag_field_actual,
                data.x_mag_field_requested, data.y_mag_field_requested, data.z_mag_field_requested) = [], [], [], [], [], [], [], [], [], [], [], [], []

                data.start_time = datetime.datetime.now()
                log_data() # start recording data if logging hasn't already started

                main_page.start_button.config(text="Update Field Values")
                main_page.stop_button.config(state=tk.NORMAL)

    def stop_field(self, cont):
        main_page = self.frames[MainPage]
        print("attempting to stop field...")
        instruments.send_voltage(0, 0, 0)
        instruments.log_data = "OFF" # this will make logging data stop
        data.log_filename = "" # if cage is started again in current session, new log file will be created
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

        main_page.start_button.configure(text="Start Field") # Change "update" text to be start again
        main_page.stop_button.configure(state="disabled")

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        # main container to hold all subframes
        container = tk.Frame(self, bg="black")
        container.grid(sticky="nsew")
        
        # subframes for MainPage
        self.title_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.connections_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.calibrate_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.static_buttons_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.dynamic_buttons_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.main_buttons_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.help_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black", highlightthickness=2)
        self.plots_frame = tk.Frame(container, bg="gray", width=500,
                                    highlightbackground="black", highlightthickness=4)
        
        # position of subframes
        self.title_frame.grid(row=0, sticky="ew")
        self.connections_frame.grid(row=1, sticky="nsew")
        self.calibrate_frame.grid(row=2, sticky="nsew")
        self.static_buttons_frame.grid(row=3, sticky="nsew")
        self.dynamic_buttons_frame.grid(row=4, sticky="nsew")
        self.main_buttons_frame.grid(row=5, sticky="nsew")
        self.help_frame.grid(row=6, sticky="nsew")
        self.plots_frame.grid(row=0, column=1, sticky="nsew", rowspan=7)

        # set weight for expansion
        [container.rowconfigure(r, weight=1) for r in range(1,5)]   
        container.columnconfigure(1, weight=1) 

        # Fill frames functions (organizational purposes)
        self.fill_title_frame()
        self.fill_calibrate_frame()
        self.fill_connections_frame()
        self.fill_static_buttons_frame(parent)
        self.fill_dynamic_buttons_frame()
        self.fill_main_buttons_frame()
        self.fill_help_frame()
        self.fill_plot_frame()

    def fill_title_frame(self):

        self.label_title = tk.Label(self.title_frame, text="Helmholtz Cage", font=LARGE_FONT)
        self.label_title.grid(row=0, column=0)

    def fill_connections_frame(self):

        self.connections_label = tk.Label(self.connections_frame, text="Connections", font=LARGE_FONT)
        self.connections_label.grid(row=0, column=0, columnspan=2, pady=5, sticky='nsew')

        self.unit_label = tk.Label(self.connections_frame, text="Unit", font=LARGE_FONT).grid(row=1, column=0)
        self.status_label = tk.Label(self.connections_frame, text="Status", font=LARGE_FONT).grid(row=1, column=1)

        self.x_ps_status = tk.StringVar()
        self.x_ps_label = tk.Label(self.connections_frame, text="X Power Supply").grid(row=2, column=0)
        self.x_ps_status_entry = tk.Entry(self.connections_frame, textvariable=self.x_ps_status)
        self.x_ps_status_entry.insert(0,"Disconnected")
        self.x_ps_status_entry.configure(state="readonly")
        self.x_ps_status_entry.grid(row=2, column=1)

        self.y_ps_status = tk.StringVar()
        self.y_ps_label = tk.Label(self.connections_frame, text="Y Power Supply").grid(row=3, column=0)
        self.y_ps_status_entry = tk.Entry(self.connections_frame, textvariable=self.y_ps_status)
        self.y_ps_status_entry.insert(0,"Disconnected")
        self.y_ps_status_entry.configure(state="readonly")
        self.y_ps_status_entry.grid(row=3, column=1)

        self.z_ps_status = tk.StringVar()
        self.z_ps_label = tk.Label(self.connections_frame, text="Z Power Supply").grid(row=4, column=0)
        self.z_ps_status_entry = tk.Entry(self.connections_frame, textvariable=self.z_ps_status)
        self.z_ps_status_entry.insert(0,"Disconnected")
        self.z_ps_status_entry.configure(state="readonly")
        self.z_ps_status_entry.grid(row=4, column=1)

        self.mag_status = tk.StringVar()
        self.mag_label = tk.Label(self.connections_frame, text="Magnetometer").grid(row=5, column=0)
        self.mag_status_entry = tk.Entry(self.connections_frame, textvariable=self.mag_status)
        self.mag_status_entry.insert(0,"Disconnected")
        self.mag_status_entry.configure(state="readonly")
        self.mag_status_entry.grid(row=5, column=1)

        self.refresh_connections_button = tk.Button(self.connections_frame, text="Check Connections", command=lambda: self.controller.refresh_connections(app))
        self.refresh_connections_button.grid(row=6, column=0, columnspan=2)

    def fill_calibrate_frame(self):

        self.find_template_file()
        self.find_calibration_file()

        self.calibration_label = tk.Label(self.calibrate_frame, text="Calibration", font=LARGE_FONT)
        self.calibration_label.grid(row=0, column=0, columnspan=3, pady=5, sticky='nsew')

        # find / display template file
        self.template_file_label = tk.Label(self.calibrate_frame, text="Template file:")
        self.template_file_label.grid(row=1, column=0)

        self.template_file_status_text = tk.StringVar()

        self.template_file_entry = tk.Entry(self.calibrate_frame, textvariable=self.template_file_status_text, width=10)
        self.template_file_entry.insert(0, data.template_file)
        self.template_file_entry.configure(state="readonly")
        self.template_file_entry.grid(row=1, column=1)

        self.change_template_file_button = tk.Button(self.calibrate_frame, text='select new', command=lambda: controller.load_template_file())
        self.change_template_file_button.grid(row=1, column=2, sticky='nsew')

        # find / display calibration file
        self.calibration_file_label = tk.Label(self.calibrate_frame, text="Calibration file:")
        self.calibration_file_label.grid(row=2, column=0)

        self.calibration_file_status_text = tk.StringVar()

        self.calibration_file_entry = tk.Entry(self.calibrate_frame, textvariable=self.calibration_file_status_text, width=10)
        self.calibration_file_entry.insert(0, data.calibration_file)
        self.calibration_file_entry.configure(state="readonly")
        self.calibration_file_entry.grid(row=2, column=1)

        self.change_calibration_file_button = tk.Button(self.calibrate_frame, text='select new', command=lambda: controller.load_calibration_file())
        self.change_calibration_file_button.grid(row=2, column=2, sticky='nsew')

        self.calibrate_button = tk.Button(self.calibrate_frame, text='Create Calibration file with template file', command=lambda: controller.calibrate_cage())
        self.calibrate_button.grid(row=3, column=0, columnspan=3, sticky='nsew')

        if data.template_file is not "none found":
            self.load_template_file()

        if data.calibration_file is not "none found":
            self.load_calibration_file()



    def fill_static_buttons_frame(self, parent):

        # used to validate that entries are floats
        vcmd_field = (parent.register(self.validate_field), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd_voltage = (parent.register(self.validate_voltage), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.static_or_dynamic = tk.StringVar()
        self.select_static = tk.Radiobutton(self.static_buttons_frame, text="Static Test: ", variable=self.static_or_dynamic, value="static", font=LARGE_FONT)
        self.select_static.grid(row=0, column=0, columnspan=4, pady=5, sticky='nsew')

        self.field_or_voltage = tk.StringVar()
        field_text = "Enter Magnetic Field \n(Max {} microteslas)".format(max_field_value)
        self.select_field = tk.Radiobutton(self.static_buttons_frame, text=field_text, variable=self.field_or_voltage, value="field", command=self.update_typable_entries)
        self.select_field.grid(row=1, column=0, columnspan=2, sticky='nsew')

        voltage_text = "Enter Voltage \n(Max {} volts)".format(max_voltage_value)
        self.select_voltage = tk.Radiobutton(self.static_buttons_frame, text=voltage_text, variable=self.field_or_voltage, value="voltage", command=self.update_typable_entries)
        self.select_voltage.grid(row=1, column=2, columnspan=2, sticky='nsew')

        self.x_field_label = tk.Label(self.static_buttons_frame, text="x:", font=LARGE_FONT).grid(row=2, column=0, sticky='ns')
        self.x_field = tk.StringVar()
        self.x_field_entry = tk.Entry(self.static_buttons_frame, state=tk.DISABLED, validate='key', validatecommand=vcmd_field, textvariable=self.x_field, width=10)
        self.x_field_entry.grid(row=2, column=1)

        self.x_voltage_label = tk.Label(self.static_buttons_frame, text="x:", font=LARGE_FONT).grid(row=2, column=2)
        self.x_voltage = tk.StringVar()
        self.x_voltage_entry = tk.Entry(self.static_buttons_frame, state=tk.DISABLED, validate='key', validatecommand=vcmd_voltage, textvariable=self.x_voltage, width=10)
        self.x_voltage_entry.grid(row=2, column=3)

        self.y_field_label = tk.Label(self.static_buttons_frame, text="y:", font=LARGE_FONT).grid(row=3, column=0)
        self.y_field = tk.StringVar()
        self.y_field_entry = tk.Entry(self.static_buttons_frame, state=tk.DISABLED, validate='key', validatecommand=vcmd_field, textvariable=self.y_field, width=10)
        self.y_field_entry.grid(row=3, column=1)

        self.y_voltage_label = tk.Label(self.static_buttons_frame, text="y:", font=LARGE_FONT).grid(row=3, column=2)
        self.y_voltage = tk.StringVar()
        self.y_voltage_entry = tk.Entry(self.static_buttons_frame, state=tk.DISABLED, validate='key', validatecommand=vcmd_voltage, textvariable=self.y_voltage, width=10)
        self.y_voltage_entry.grid(row=3, column=3)

        self.z_field_label = tk.Label(self.static_buttons_frame, text="z:", font=LARGE_FONT).grid(row=4, column=0)
        self.z_field = tk.StringVar()
        self.z_field_entry = tk.Entry(self.static_buttons_frame, state=tk.DISABLED, validate='key', validatecommand=vcmd_field, textvariable=self.z_field, width=10)
        self.z_field_entry.grid(row=4, column=1)

        self.z_voltage_label = tk.Label(self.static_buttons_frame, text="z:", font=LARGE_FONT).grid(row=4, column=2)
        self.z_voltage = tk.StringVar()
        self.z_voltage_entry = tk.Entry(self.static_buttons_frame, state=tk.DISABLED, validate='key', validatecommand=vcmd_voltage, textvariable=self.z_voltage, width=10)
        self.z_voltage_entry.grid(row=4, column=3)

    def fill_dynamic_buttons_frame(self):

        self.select_dynamic = tk.Radiobutton(self.dynamic_buttons_frame, text="Dynamic Test: ", variable=self.static_or_dynamic, value="dynamic", font=LARGE_FONT)
        self.select_dynamic.grid(row=0, column=0, columnspan=4, pady=5, sticky='nsew')

        self.open_csv_button = tk.Button(self.dynamic_buttons_frame, text='Load Dynamic Field CSV File', command=lambda: open_csv(app))
        self.open_csv_button.grid(row=1, column=0, sticky='nsew')

    def fill_main_buttons_frame(self):

        self.start_button = tk.Button(self.main_buttons_frame, text='Start Field', command=lambda: self.controller.start_field(app))
        self.start_button.grid(row=0, column=0, sticky='nsew')

        self.stop_button = tk.Button(self.main_buttons_frame, text='Stop Field', state=tk.DISABLED, command=lambda: self.controller.stop_field(app))
        self.stop_button.grid(row=0, column=1, sticky='nsew')

    def fill_help_frame(self):
        pass

    def fill_plot_frame(self):

        if data.plots_created == False:
            # Create figure and initialize plots
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = plt.subplots(nrows=2, facecolor='grey')
            self.power_supplies_plot = plt.subplot(211) # Power supplies plot
            self.mag_field_plot = plt.subplot(212) # Magnetic field plot

        self.update_plot_info() # split out for easy recreation when making new plots after hitting stop field

        if data.plots_created == False:

            # Add to frame
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        data.plots_created = True
        self.canvas.draw()

    def update_plot_info(self):

        self.time = data.time

        x_mag_field_actual = []
        y_mag_field_actual = []
        z_mag_field_actual = []

        x_mag_field_requested = []
        y_mag_field_requested = []
        z_mag_field_requested = []

        # if a list doesn't have all inputs, they're all assumed to be zero
        max_entries = len(self.time)
        if max_entries == 0:
            max_entries = 1
        if len(self.time) != max_entries: self.time = [0] * max_entries
        if len(data.x_out) != max_entries: data.x_out = [0]*max_entries
        if len(data.y_out) != max_entries: data.y_out = [0]*max_entries
        if len(data.z_out) != max_entries: data.z_out = [0]*max_entries
        if len(data.x_req) != max_entries: data.x_req = [0]*max_entries
        if len(data.y_req) != max_entries: data.y_req = [0]*max_entries
        if len(data.z_req) != max_entries: data.z_req = [0]*max_entries
        if len(data.x_mag_field_actual) != max_entries: x_mag_field_actual = [0]*max_entries
        if len(data.y_mag_field_actual) != max_entries: y_mag_field_actual = [0]*max_entries
        if len(data.z_mag_field_actual) != max_entries: z_mag_field_actual = [0]*max_entries
        if len(data.x_mag_field_requested) != max_entries: x_mag_field_requested = [0]*max_entries
        if len(data.y_mag_field_requested) != max_entries: y_mag_field_requested = [0]*max_entries
        if len(data.z_mag_field_requested) != max_entries: z_mag_field_requested = [0]*max_entries

        # get max and min values for power_supplies_plot and mag_field_plot (min/max values used for plot axes)
        power_supplies_master_list = (data.x_out + data.y_out + data.z_out + data.x_req + data.y_req + data.z_req)

        max_y_plot_one = 1.2*max(power_supplies_master_list)
        if max_y_plot_one < 1: max_y_plot_one = 1

        min_y_plot_one = min(power_supplies_master_list)

        mag_field_master_list = (x_mag_field_actual + y_mag_field_actual + z_mag_field_actual +
                                x_mag_field_requested + y_mag_field_requested + z_mag_field_requested)

        max_y_plot_two = 1.2*max(mag_field_master_list)
        if max_y_plot_two < 1: max_y_plot_two = 1

        min_y_plot_two = min(mag_field_master_list)

        self.power_supplies_plot.plot(self.time, data.x_out, 'r', label='x_ps_output')
        self.power_supplies_plot.plot(self.time, data.x_req, 'r--', label='x_ps_requested')
        self.power_supplies_plot.plot(self.time, data.y_out, 'g', label='y_ps_output')
        self.power_supplies_plot.plot(self.time, data.y_req, 'g--', label='y_ps_requested')
        self.power_supplies_plot.plot(self.time, data.z_out, 'b', label='z_ps_output')
        self.power_supplies_plot.plot(self.time, data.z_req, 'b--', label='z_ps_requested')

        self.plot_1_axes = self.power_supplies_plot.axes
        self.plot_1_axes.set_ylim(min_y_plot_one, max_y_plot_one)

        self.mag_field_plot.plot(self.time, x_mag_field_actual, 'r', label='x_mag_field_actual')
        self.mag_field_plot.plot(self.time, x_mag_field_requested, 'r--', label='x_mag_field_requested')
        self.mag_field_plot.plot(self.time, y_mag_field_actual, 'g', label='y_mag_field_actual')
        self.mag_field_plot.plot(self.time, y_mag_field_requested, 'g--', label='y_mag_field_requested')
        self.mag_field_plot.plot(self.time, z_mag_field_actual, 'b', label='z_mag_field_actual')
        self.mag_field_plot.plot(self.time, z_mag_field_requested, 'b--', label='z_mag_field_requested')

        self.plot_2_axes = self.mag_field_plot.axes
        self.plot_2_axes.set_ylim(min_y_plot_two, max_y_plot_two)

        self.power_supplies_plot.get_shared_x_axes().join(self.power_supplies_plot, self.mag_field_plot)
        self.power_supplies_plot.set_xticklabels([])
        self.power_supplies_plot.set_facecolor("grey")
        self.mag_field_plot.set_facecolor("grey")

        self.power_supplies_plot.set_title("Voltage vs. Time")
        self.power_supplies_plot.set_ylabel("Voltage (V)")

        self.mag_field_plot.set_title("Magnetic Field vs. Time")
        self.mag_field_plot.set_ylabel("Magnetic Field (microteslas)")

        if data.plot_titles == "None": # only need to do this once for the plots
            self.power_supplies_plot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.00),
                                            ncol=3, fancybox=True, prop={'size': 7})


            self.mag_field_plot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0),
                                       ncol=3, fancybox=True, prop={'size': 7})


            data.plot_titles = "Exist"

    def update_typable_entries(self):

        # only let user type values in selected option
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
    
    # check that constant value entry can be interpreted as a float
    def validate_field(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        if(action=='1'):
            if text in '0123456789.-+':
                try:
                    value = float(value_if_allowed)
                    if value <= max_field_value:
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
                       prior_value, text, validation_type, trigger_type, widget_name):
        if(action=='1'):
            if text in '0123456789.-+':
                try:
                    value = float(value_if_allowed)
                    if value <= max_voltage_value:
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
        path = os.getcwd()
        only_files = [f for f in listdir(path) if isfile(join(path, f))]
        only_csv_files = [f for f in only_files if f.endswith(".csv")]
        template_files = [f for f in only_csv_files if "template" in f]
        if len(template_files) > 0:
            data.template_file = template_files[0] #use the first found file for now
            print("Found {} template files, using: {}".format(len(template_files), data.template_file))
        else:
            print("No template file found in current working directory")

    def find_calibration_file(self):
        path = os.getcwd()
        only_files = [f for f in listdir(path) if isfile(join(path, f))]
        only_csv_files = [f for f in only_files if f.endswith(".csv")]
        calibration_files = [f for f in only_csv_files if "calibration" in f]
        if len(calibration_files) > 0:
            data.calibration_file = calibration_files[0] #use the first found file for now
            print("Found {} calibration files, using: {}".format(len(calibration_files), data.calibration_file))
        else:
            print("No calibration file found in current working directory")

    def load_template_file(self):
        print("Loading template file...")
        with open(data.template_file) as file:
            file_info = csv.reader(file, delimiter=',')
            for row in file_info:
                data.template_voltages_x.append(row[0])

            print(data.template_voltages_x)


    def load_calibration_file(self):
        pass

class HelpPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        # main container to hold all subframes
        container = tk.Frame(self, bg="black")
        container.grid(sticky="nsew")

# --------------------------------------------------------------------------------
# FUNCTIONS

def log_data():
    main_page = app.frames[MainPage]

    if instruments.log_data == "ON":
        today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if data.log_filename == "":
            data.log_filename = "HelmholtzCageSessionData_{}.csv".format(today)
            print("creating log file: {}".format(data.log_filename))
            with open(data.log_filename, 'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['time','x_req', 'y_req', 'z_req', 'x_out', 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])
        with open(data.log_filename, 'a') as file:
            threading.Timer(update_log_time, log_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time).total_seconds())
            print("logging data at {}".format(str(time)))
            #x_req, y_req, z_req = instruments.get_requested_voltage()
            x_out, y_out, z_out = instruments.get_output_voltage()
            x_mag = 1 #***
            y_mag = 2
            z_mag = 3
            writer.writerow([time,
                             data.active_x_voltage_requested,
                             data.active_y_voltage_requested,
                             data.active_z_voltage_requested,
                             x_out,
                             y_out,
                             z_out,
                             x_mag,
                             y_mag,
                             z_mag])

            data.time.append(time)
            data.x_req.append(data.active_x_voltage_requested)
            data.y_req.append(data.active_y_voltage_requested)
            data.z_req.append(data.active_z_voltage_requested)
            data.x_out.append(x_out)
            data.y_out.append(y_out)
            data.z_out.append(z_out)

            main_page.fill_plot_frame()



# --------------------------------------------------------------------------------
# CODE
instruments = Instruments()
data = Data()
app = CageApp()
app.minsize(width=250, height=600)
app.mainloop()