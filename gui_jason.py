# Written by Jason Roll, contact: rolljn@mail.uc.edu, 513-939-9800
# Last modified: 180923
# Don't try to edit this in idle. Use pycharm or other smart python interface
# ------------------------------------------------------------------------------
# PYTHON IMPORTS
import tkinter as tk
import os
import glob
from os import listdir
from os.path import isfile, join
from tkinter import filedialog
import threading
import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# OTHER CODE IMPORTS
from connections import *

# set up logging
import logging
logging.getLogger("visa").setLevel(logging.WARNING)
logger = logging.getLogger("gui_jason.py")

logging.basicConfig(filename='helmholtz-gui.log', level=logging.DEBUG)


# ------------------------------------------------------------------------------
# CONSTANTS
max_field_value = 20
max_voltage_value = 20
update_plot_time = 1  # seconds
update_log_time = 5  # seconds
update_calibrate_time = 5  # seconds
LARGE_FONT = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 9)

# ------------------------------------------------------------------------------
# FUNCTIONS


def log_session_data():
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
            threading.Timer(update_plot_time, log_session_data).start()
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
    # this is used when creating a calibration file from a loaded template file
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

            threading.Timer(update_plot_time, log_calibration_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time)
                       .total_seconds())

            # check if it is time to get new values from template yet
            logger.info("time calibrating is: {}".format(time))
            logger.info("data.current_value is {}".format(data.current_value))
            logger.info("update_calibrate_time * data.current_value is: {}".
                        format(data.current_value * update_calibrate_time))

            if time >= (data.current_value*update_calibrate_time):

                try:
                    # get current calibration voltages for whichever increment
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

            # update values saved to calibration file
            writer.writerow([time, data.cur_cal_x, data.cur_cal_y,
                             data.cur_cal_z, x_out, y_out, z_out,
                             x_mag, y_mag, z_mag])

            # update lists that will be plotted
            data.time.append(time)
            data.x_req.append(data.cur_cal_x)
            data.y_req.append(data.cur_cal_y)
            data.z_req.append(data.cur_cal_z)
            data.x_out.append(x_out)
            data.y_out.append(y_out)
            data.z_out.append(z_out)

        # update plot if calibration is still going on
        if not data.stop_calibration:
            main_page.fill_plot_frame()

        # stop calibration if all template voltages have been used
        if data.current_value == len(data.template_voltages_x):
            instruments.log_data = "OFF"
            logger.info("calibration file {} created - load it in before "
                        "doing a dynamic test or requesting based on "
                        "magnetic field".format(data.calibration_log_filename))
            # allows for a new calibration file to be created again? TODO: test
            data.calibration_log_filename = ""
            data.stop_calibration = True
            logger.info("data.calibrating_now: {} | data.stop_calibration: {}"
                        .format(data.calibrating_now, data.stop_calibration))
            logger.info("in log calibration: data.stop_calibration is {}"
                        .format(data.stop_calibration))
            data.current_value = 0
            logger.info("stopping calibration")
            main_page.calibrate_cage_update_buttons()

# ------------------------------------------------------------------------------
# CLASSES


# where opened file data will be stored
class Data:

    def __init__(self):

        # --- plot related data ---
        # flag variable so plots are only created once
        self.plots_created = False
        # flag variable so titles are only added the first time data is logged
        self.plot_titles = ""

        # --- button clicking related data ---
        # prevent buttons from being used when the cage is in a certain mode
        self.cage_on = False
        self.cage_calibrating = False
        self.cage_in_dynamic = False

        # --- template related data ---
        self.template_file = "none found"
        # voltages loaded in from template file to send to cage to calibrate
        self.template_voltages_x = []
        self.template_voltages_y = []
        self.template_voltages_z = []

        # --- calibration related data ---
        # used when creation a new calibration file from template file
        self.calibrating_now = False
        self.stop_calibration = False
        self.calibration_log_filename = ""
        self.calibration_file = "none found"
        # not needed for anything but good to keep track of
        self.calibration_time = []
        # the voltages that were used to get a magnetic field
        self.calibration_voltages_x = []
        self.calibration_voltages_y = []
        self.calibration_voltages_z = []
        # the magnetic fields that were obtained by the (x,y,z) voltages
        self.calibration_mag_field_x = []
        self.calibration_mag_field_y = []
        self.calibration_mag_field_z = []
        self.current_value = 0

        # --- logging data ---
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
    def __init__(self, *args, **kwargs):
        # initialize frame
        tk.Tk.__init__(self, *args, **kwargs)

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
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
        self.show_frame(MainPage)

    # call this to switch frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # the controller allows MainPage to access things from CageApp class
        self.controller = controller

        # main container to hold all subframes
        container = tk.Frame(self, bg="black")
        container.grid(sticky="nsew")

        # subframes for MainPage
        self.title_frame = tk.Frame(container, bg="gray", height=50,
                                    highlightbackground="black",
                                    highlightthickness=2)
        self.connections_frame = tk.Frame(container, bg="gray", height=50,
                                          highlightbackground="black",
                                          highlightthickness=2)
        self.calibrate_frame = tk.Frame(container, bg="gray", height=50,
                                        highlightbackground="black",
                                        highlightthickness=2)
        self.static_buttons_frame = tk.Frame(container, bg="gray", height=50,
                                             highlightbackground="black",
                                             highlightthickness=2)
        self.dynamic_buttons_frame = tk.Frame(container, bg="gray", height=50,
                                              highlightbackground="black",
                                              highlightthickness=2)
        self.main_buttons_frame = tk.Frame(container, bg="gray", height=50,
                                           highlightbackground="black",
                                           highlightthickness=2)
        self.help_frame = tk.Frame(container, bg="gray", height=50,
                                   highlightbackground="black",
                                   highlightthickness=2)
        self.plots_frame = tk.Frame(container, bg="gray", width=500,
                                    highlightbackground="black",
                                    highlightthickness=4)

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
        [container.rowconfigure(r, weight=1) for r in range(1, 5)]
        container.columnconfigure(1, weight=1)

        # Initialize class attributes to follow stupid PEP8 guidelines..
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

        # Fill frames functions (organizational purposes)
        self.fill_title_frame()
        self.fill_calibrate_frame()
        self.fill_connections_frame()
        self.fill_static_buttons_frame(parent)
        self.fill_dynamic_buttons_frame()
        self.fill_main_buttons_frame()
        self.fill_help_frame()
        self.fill_plot_frame()

        # --- frame widget creation / organization in all "fill" attributes ---
    def fill_title_frame(self):

        self.label_title = tk.Label(self.title_frame, text="Helmholtz Cage",
                                    font=LARGE_FONT)
        self.label_title.grid(row=0, column=0)

    def fill_connections_frame(self):

        self.connections_label = tk.Label(self.connections_frame,
                                          text="Connections", font=LARGE_FONT)
        self.connections_label.grid(row=0, column=0, columnspan=2,
                                    pady=5, sticky='nsew')

        self.unit_label = tk.Label(self.connections_frame,
                                   text="Unit", font=LARGE_FONT)
        self.unit_label.grid(row=1, column=0)

        self.status_label = tk.Label(self.connections_frame,
                                     text="Status", font=LARGE_FONT)
        self.status_label.grid(row=1, column=1)

        self.x_ps_status = tk.StringVar()
        self.x_ps_label = tk.Label(self.connections_frame,
                                   text="X Power Supply")
        self.x_ps_label.grid(row=2, column=0)

        self.x_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.x_ps_status)
        self.x_ps_status_entry.insert(0, "Disconnected")
        self.x_ps_status_entry.configure(state="readonly")
        self.x_ps_status_entry.grid(row=2, column=1)

        self.y_ps_status = tk.StringVar()
        self.y_ps_label = tk.Label(self.connections_frame,
                                   text="Y Power Supply").grid(row=3, column=0)
        self.y_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.y_ps_status)
        self.y_ps_status_entry.insert(0, "Disconnected")
        self.y_ps_status_entry.configure(state="readonly")
        self.y_ps_status_entry.grid(row=3, column=1)

        self.z_ps_status = tk.StringVar()
        self.z_ps_label = tk.Label(self.connections_frame,
                                   text="Z Power Supply").grid(row=4, column=0)
        self.z_ps_status_entry = tk.Entry(self.connections_frame,
                                          textvariable=self.z_ps_status)
        self.z_ps_status_entry.insert(0, "Disconnected")
        self.z_ps_status_entry.configure(state="readonly")
        self.z_ps_status_entry.grid(row=4, column=1)

        self.mag_status = tk.StringVar()
        self.mag_label = tk.Label(self.connections_frame,
                                  text="Magnetometer").grid(row=5, column=0)
        self.mag_status_entry = tk.Entry(self.connections_frame,
                                         textvariable=self.mag_status)
        self.mag_status_entry.insert(0, "Disconnected")
        self.mag_status_entry.configure(state="readonly")
        self.mag_status_entry.grid(row=5, column=1)

        self.refresh_connections_button = \
            tk.Button(self.connections_frame,
                      text="Check Connections",
                      command=lambda: self.refresh_connections())
        self.refresh_connections_button.grid(row=6, column=0, columnspan=2)

    def fill_calibrate_frame(self):
        self.find_template_file()
        self.find_calibration_file()

        self.calibration_label = \
            tk.Label(self.calibrate_frame, text="Calibration", font=LARGE_FONT)
        self.calibration_label.grid(row=0, column=0, columnspan=3,
                                    pady=5, sticky='nsew')

        # find / display template file
        self.template_file_label = \
            tk.Label(self.calibrate_frame, text="Cal. Template file:")
        self.template_file_label.grid(row=1, column=0)

        self.template_file_status_text = tk.StringVar()

        self.template_file_entry = \
            tk.Entry(self.calibrate_frame,
                     textvariable=self.template_file_status_text, width=10)
        self.template_file_entry.insert(0, data.template_file)
        self.template_file_entry.configure(state="readonly")
        self.template_file_entry.grid(row=1, column=1)

        self.change_template_file_button = \
            tk.Button(self.calibrate_frame, text='select new',
                      command=lambda: self.change_template_file())
        self.change_template_file_button.grid(row=1, column=2, sticky='nsew')

        # find / display calibration file
        self.calibration_file_label = \
            tk.Label(self.calibrate_frame, text="Calibration file:")
        self.calibration_file_label.grid(row=2, column=0)

        self.calibration_file_status_text = tk.StringVar()

        self.calibration_file_entry = \
            tk.Entry(self.calibrate_frame,
                     textvariable=self.calibration_file_status_text, width=10)
        self.calibration_file_entry.insert(0, data.calibration_file)
        self.calibration_file_entry.configure(state="readonly")
        self.calibration_file_entry.grid(row=2, column=1)

        self.change_calibration_file_button = \
            tk.Button(self.calibrate_frame, text='select new',
                      command=lambda: self.change_calibration_file())
        self.change_calibration_file_button.grid(row=2, column=2, sticky='nsew')

        self.calibrate_button = \
            tk.Button(self.calibrate_frame,
                      text='Create calibration file with template file',
                      command=lambda: self.calibrate_cage())
        self.calibrate_button.grid(row=3, column=0, columnspan=3, sticky='nsew')

        if data.template_file is not "none found":
            try:
                self.load_template_file()
            except Exception as err:
                print("Couldn't load template file | {}".format(err))

        if data.calibration_file is not "none found":
            try:
                self.load_calibration_file()
            except Exception as err:
                print("Couldn't load calibration file | {}".format(err))

    def fill_static_buttons_frame(self, parent):

        # used to validate that entries are floats
        vcmd_field = (parent.register(self.validate_field),
                      '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd_voltage = (parent.register(self.validate_voltage),
                        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.static_or_dynamic = tk.StringVar()
        self.select_static = \
            tk.Radiobutton(self.static_buttons_frame,
                           text="Static Test: ",
                           variable=self.static_or_dynamic,
                           value="static", font=LARGE_FONT)
        self.select_static.grid(row=0, column=0, columnspan=4,
                                pady=5, sticky='nsew')

        self.field_or_voltage = tk.StringVar()

        # TODO: update field text to find max field for max voltage
        field_text = "Enter Magnetic Field \n(Max {} Gauss)"\
                     .format(max_field_value)
        field_text = "Enter Magnetic Field \n (Gauss)" \
            .format(max_field_value)
        self.select_field = \
            tk.Radiobutton(self.static_buttons_frame,
                           text=field_text, variable=self.field_or_voltage,
                           value="field", command=self.update_typable_entries)
        self.select_field.grid(row=1, column=0, columnspan=2, sticky='nsew')

        voltage_text = "Enter Voltage \n(Max {} volts)"\
                       .format(max_voltage_value)
        self.select_voltage = \
            tk.Radiobutton(self.static_buttons_frame,
                           text=voltage_text, variable=self.field_or_voltage,
                           value="voltage", command=self.update_typable_entries)
        self.select_voltage.grid(row=1, column=2, columnspan=2, sticky='nsew')

        self.x_field_label = \
            tk.Label(self.static_buttons_frame,
                     text="x:", font=LARGE_FONT).grid(row=2, column=0,
                                                      sticky='ns')
        self.x_field = tk.StringVar()
        self.x_field_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_field,
                     textvariable=self.x_field, width=10)
        self.x_field_entry.grid(row=2, column=1)

        self.x_voltage_label = \
            tk.Label(self.static_buttons_frame,
                     text="x:", font=LARGE_FONT).grid(row=2, column=2)
        self.x_voltage = tk.StringVar()
        self.x_voltage_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_voltage,
                     textvariable=self.x_voltage, width=10)
        self.x_voltage_entry.grid(row=2, column=3)

        self.y_field_label = \
            tk.Label(self.static_buttons_frame,
                     text="y:", font=LARGE_FONT).grid(row=3, column=0)
        self.y_field = tk.StringVar()
        self.y_field_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_field,
                     textvariable=self.y_field, width=10)
        self.y_field_entry.grid(row=3, column=1)

        self.y_voltage_label = \
            tk.Label(self.static_buttons_frame,
                     text="y:", font=LARGE_FONT).grid(row=3, column=2)
        self.y_voltage = tk.StringVar()
        self.y_voltage_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_voltage,
                     textvariable=self.y_voltage, width=10)
        self.y_voltage_entry.grid(row=3, column=3)

        self.z_field_label = \
            tk.Label(self.static_buttons_frame,
                     text="z:", font=LARGE_FONT).grid(row=4, column=0)
        self.z_field = tk.StringVar()
        self.z_field_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_field,
                     textvariable=self.z_field, width=10)
        self.z_field_entry.grid(row=4, column=1)

        self.z_voltage_label = \
            tk.Label(self.static_buttons_frame,
                     text="z:", font=LARGE_FONT).grid(row=4, column=2)
        self.z_voltage = tk.StringVar()
        self.z_voltage_entry = \
            tk.Entry(self.static_buttons_frame,
                     state=tk.DISABLED, validate='key',
                     validatecommand=vcmd_voltage,
                     textvariable=self.z_voltage, width=10)
        self.z_voltage_entry.grid(row=4, column=3)

    def fill_dynamic_buttons_frame(self):

        self.select_dynamic = tk.Radiobutton(self.dynamic_buttons_frame,
                                             text="Dynamic Test: ",
                                             variable=self.static_or_dynamic,
                                             value="dynamic", font=LARGE_FONT)
        self.select_dynamic.grid(row=0, column=0, columnspan=4,
                                 pady=5, sticky='nsew')

        self.open_dynamic_csv_button = \
            tk.Button(self.dynamic_buttons_frame,
                      text='Load Dynamic Field CSV File',
                      command=lambda: open_csv(app))
        self.open_dynamic_csv_button.grid(row=1, column=0, sticky='nsew')

    def fill_main_buttons_frame(self):

        self.start_button = \
            tk.Button(self.main_buttons_frame,
                      text='Start Cage', command=lambda: self.start_cage())
        self.start_button.grid(row=0, column=0, sticky='nsew')

        self.stop_button = \
            tk.Button(self.main_buttons_frame,
                      text='Stop Cage', state=tk.DISABLED,
                      command=lambda: self.stop_cage())
        self.stop_button.grid(row=0, column=1, sticky='nsew')

    def fill_help_frame(self):
        pass

    def fill_plot_frame(self):

        print("filling plot frame...")
        if not data.plots_created:
            # Create figure and initialize plots
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = \
                plt.subplots(nrows=2, facecolor='grey')
            self.power_supplies_plot = plt.subplot(211) # Power supplies plot
            self.mag_field_plot = plt.subplot(212) # Magnetic field plot

        # separated for easy recreation when making new plots after hitting stop
        self.update_plot_info()

        if not data.plots_created:

            # Add to frame
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH,
                                             expand=True)

        data.plots_created = True
        self.canvas.draw()

    # --- operational functions for MainPage below ---
    def refresh_connections(self):
        main_page = self.controller.frames[MainPage]

        # allow the entry fields to be changed
        main_page.x_ps_status_entry.configure(state=tk.NORMAL)
        main_page.y_ps_status_entry.configure(state=tk.NORMAL)
        main_page.z_ps_status_entry.configure(state=tk.NORMAL)
        main_page.mag_status_entry.configure(state=tk.NORMAL)

        # must be done in try/except to set text back to readonly
        try:
            instruments.make_connections()
        except Exception as err:
            print("Could not connect instruments | {}".format(err))

        # for applicable connections, delete the entry and update it
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

        # set the entry fields back to read only ***not working??
        main_page.x_ps_status_entry.configure(state="readonly")
        main_page.y_ps_status_entry.configure(state="readonly")
        main_page.z_ps_status_entry.configure(state="readonly")
        main_page.mag_status_entry.configure(state="readonly")

    # serves as both start_cage and update_cage
    def start_cage(self):
        print("starting the cage")

        main_page = self.controller.frames[MainPage]
        static_or_dynamic = main_page.static_or_dynamic.get()
        field_or_voltage = main_page.field_or_voltage.get()

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

                # start recording data if logging hasn't already started
                log_session_data()

                self.start_cage_update_buttons()

    def start_cage_update_buttons(self):
        main_page = self.controller.frames[MainPage]

        main_page.start_button.config(text="Update Cage Values")
        main_page.stop_button.config(state=tk.NORMAL)

        main_page.refresh_connections_button.config(state=tk.DISABLED)
        main_page.change_template_file_button.config(state=tk.DISABLED)
        main_page.change_calibration_file_button.config(state=tk.DISABLED)
        main_page.calibrate_button.config(state=tk.DISABLED)
        main_page.open_dynamic_csv_button.config(state=tk.DISABLED)

    def stop_cage(self):
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
        main_page = self.controller.frames[MainPage]

        main_page.start_button.configure(text="Start Cage")
        main_page.stop_button.configure(state="disabled")

        main_page.refresh_connections_button.config(state=tk.NORMAL)
        main_page.change_template_file_button.config(state=tk.NORMAL)
        main_page.change_calibration_file_button.config(state=tk.NORMAL)
        main_page.calibrate_button.config(state=tk.NORMAL)
        main_page.open_dynamic_csv_button.config(state=tk.NORMAL)

    def update_plot_info(self):
        print("updating plot info...")

        # initialize lists for each variable that can be plotted
        x_mag_field_actual = data.x_mag_field_actual
        y_mag_field_actual = data.y_mag_field_actual
        z_mag_field_actual = data.z_mag_field_actual

        x_mag_field_requested = []
        y_mag_field_requested = []
        z_mag_field_requested = []

        # logic to make check lists are of equal length in order to be plotted
        max_entries = len(data.time)
        print("max entries is {}".format(max_entries))
        print("len of x_mag_field_requested: {}".format(len(data.x_mag_field_requested)))
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

        # get axis limits
        power_supplies_list = (data.x_out + data.y_out + data.z_out +
                               data.x_req + data.y_req + data.z_req)
        power_supplies_master_list = [float(x) for x in power_supplies_list]
        print("power_supplies_master_list: {}".format(power_supplies_master_list))
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

        # plot
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
        self.power_supplies_plot.set_facecolor("grey")
        self.mag_field_plot.set_facecolor("grey")

        self.power_supplies_plot.set_title("Voltage vs. Time")
        self.power_supplies_plot.set_ylabel("Voltage (V)")

        self.mag_field_plot.set_title("Magnetic Field vs. Time")
        self.mag_field_plot.set_ylabel("Magnetic Field (Gauss)")

        # create plot titles (only needs to be ran once)
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
                           prior_value, text, validation_type, trigger_type,
                           widget_name):
            if (action == '1'):
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
                       prior_value, text, validation_type, trigger_type,
                       widget_name):
        if (action == '1'):
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
                         prior_value, text, validation_type, trigger_type,
                         widget_name):
        if (action == '1'):
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
        template_files = [f for f in only_csv_files if "TEMPLATE" in f.upper()]
        if len(template_files) > 0:
            data.template_file = template_files[0]  # use the first found file
            logger.info("Found {} template files, loading: {}".format(
                len(template_files), data.template_file))
            self.load_template_file()
        else:
            logger.info("No template file found in current working directory")

    def find_calibration_file(self):
        root = os.getcwd()
        path = os.path.join(root, "calibration_files")
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
        logger.info("Loading template file [{}]...".format(data.template_file))
        with open(data.template_file) as file:
            # if the file is opened, reinitialize the data class
            data.template_voltages_x = []
            data.template_voltages_y = []
            data.template_voltages_z = []
            file_info = csv.reader(file, delimiter=',')
            next(file_info, None)  # skip the 1st line, these are headers
            for row in file_info:
                data.template_voltages_x.append(row[0])
                data.template_voltages_y.append(row[1])
                data.template_voltages_z.append(row[2])

        logger.info("loaded {} x, {} y, {} z voltages"
                    .format(len(data.template_voltages_x),
                            len(data.template_voltages_y),
                            len(data.template_voltages_z)))
        logger.info("x template voltages: {}".format(data.template_voltages_x))
        logger.info("y template voltages: {}".format(data.template_voltages_y))
        logger.info("z template voltages: {}".format(data.template_voltages_z))
        logger.info("...completed loading template file")

    def load_calibration_file(self):
        logger.info("Loading calibration file [{}]".format(data.calibration_file))
        with open(data.calibration_file) as file:
            # if the file is opened, reinitialize the data class
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
        main_page = self.controller.frames[MainPage]
        data.stop_calibration = False

        if not hasattr(instruments, "connections_checked"):
            logger.info("Check connections before starting")
        else:
            # connections are checked, start calibration if allowed
            if not data.calibrating_now:
                # clear plots if information is on them
                main_page.power_supplies_plot.cla()
                main_page.mag_field_plot.cla()
                data.plot_titles = "None"

                # reset information logged into the data class
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
                # data.calibrating_now == true, so update the plots
                if not data.stop_calibration:
                    main_page.update_plot_info()

            # check voltages that will be sent to allow calibration
            if not data.calibrating_now and not data.stop_calibration:
                if len(data.template_voltages_x) == \
                        len(data.template_voltages_y) == \
                        len(data.template_voltages_z):
                    logger.info("Will calibrate using {} different X, Y, Z "
                                "voltages every {} seconds"
                                .format(len(data.template_voltages_x),
                                        update_log_time))
                    s_remaining = update_log_time*len(data.template_voltages_x)
                    logger.info("Do not use GUI until process completes | {} "
                                "seconds remaining".format(s_remaining))

                    for value in range(0, len(data.template_voltages_x)):
                        x = float(data.template_voltages_x[value])
                        y = float(data.template_voltages_y[value])
                        z = float(data.template_voltages_z[value])

                        # check that none of the requested voltages
                        # exceed max or are less than zero
                        if (x > max_voltage_value) or (x < 0):
                            logger.info("ERROR: cannot calibrate, x voltage of "
                                        "{} is above the max {} volts, or "
                                        "negative".format(x, max_voltage_value))
                            data.stop_calibration = True
                        if (y > max_voltage_value) or (y < 0):
                            logger.info("ERROR: cannot calibrate, y voltage of "
                                        "{} is above the max {} volts, or "
                                        "negative".format(y, max_voltage_value))
                            data.stop_calibration = True
                        if (z > max_voltage_value) or (z < 0):
                            logger.info("ERROR: cannot calibrate, z voltage of "
                                        "{} is above the max {} volts, or "
                                        "negative".format(z, max_voltage_value))
                            data.stop_calibration = True

                else:
                    logger.info("The amount of X Y Z voltages are not all "
                                "equal, calibration stopped")
                    data.stop_calibration = True
                    instruments.log_data = "OFF"  # stops the logging process
                    data.calibration_log_filename = ""

            if data.current_value == len(data.template_voltages_x):
                data.calibrating_now = False
                data.stop_calibration = True
                data.current_value = 0
                logger.info("stopping calibration")
                self.calibrate_cage_update_buttons()
                logger.info("should not need this")

            if not data.stop_calibration:
                if not data.calibrating_now:
                    instruments.log_data = "ON"
                    log_calibration_data()  # starts the calibration process
                data.calibrating_now = True
                threading.Timer(update_log_time, self.calibrate_cage).start()
                try:
                    x = float(data.template_voltages_x[data.current_value])
                    y = float(data.template_voltages_y[data.current_value])
                    z = float(data.template_voltages_z[data.current_value])
                except Exception as err:
                    logger.info("Could not get x,y,z voltage for "
                                "data.current_value, likely finished "
                                "calibrating | {}".format(err))
                    x, y, z = 0, 0, 0

                main_page.x_voltage.set(x)
                main_page.y_voltage.set(y)
                main_page.z_voltage.set(z)

    def calibrate_cage_update_buttons(self):
        main_page = self.controller.frames[MainPage]

        if not data.calibrating_now:
            main_page.start_button.config(text="allow calibration to complete")
            main_page.start_button.config(state=tk.DISABLED)

            main_page.refresh_connections_button.config(state=tk.DISABLED)
            main_page.change_template_file_button.config(state=tk.DISABLED)
            main_page.change_calibration_file_button.config(state=tk.DISABLED)
            main_page.calibrate_button.config(state=tk.DISABLED)
            main_page.open_dynamic_csv_button.config(state=tk.DISABLED)

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
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            # main container to hold all subframes
            container = tk.Frame(self, bg="black")
            container.grid(sticky="nsew")


# ------------------------------------------------------------------------------
# CODE
instruments = Instruments()
data = Data()
app = CageApp()
app.minsize(width=250, height=600)
app.mainloop()
