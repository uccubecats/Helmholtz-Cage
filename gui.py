# Written by Jason Roll, contact: rolljn@mail.uc.edu, 513-939-9800
# Last modified: 180131
# Don't try to edit this in idle. Are you insane? Get pycharm community edition or at least NP++

# --------------------------------------------------------------------------------
# PYTHON IMPORTS
import tkinter as tk
import os
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
        self.plots_created = False

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

        # for applicable connections, delete the entry and update it
        connected_devices = instruments.make_connections()
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

        # set the entry fields back to read only
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
                x_voltage = main_page.x_voltage.get()
                y_voltage = main_page.y_voltage.get()
                z_voltage = main_page.z_voltage.get()
                instruments.send_voltage(x_voltage, y_voltage, z_voltage)

            if field_or_voltage == "field":
                print("attempting to send specified magnetic field...")
                x_field = main_page.x_field.get()
                y_field = main_page.y_field.get()
                z_field = main_page.z_field.get()
                send_field(x_field, y_field, Z_field)

        if static_or_dynamic == "dynamic":
            print("Dynamic field not supported yet")

        if not hasattr(instruments, "cage_power"):
            print("Check connections before starting")
        else:
            if main_page.start_button["text"] == 'Start Field':
                data.start_time = datetime.datetime.now()
                log_data() # start recording data if logging hasn't already started
                main_page.start_button.config(text="Update Field Values")
                main_page.stop_button.config(state=tk.NORMAL)


    def stop_field(self, cont):
        main_page = self.frames[MainPage]
        print("attempting to stop field...")
        instruments.send_voltage(0, 0, 0)
        instruments.cage_power = "OFF" # this will make logging data stop
        data.log_filename = "" # if cage is started again in current session, new log file will be created
        data.log_filename = ""
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
        data.plots_created = False # allow plots to be created next run through
        main_page.start_button.configure(text="Start Field") # Change "update" text to be start again

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

        self.connections_label = tk.Label(self.connections_frame, text="Connections: ", font=LARGE_FONT)
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

        calibrate_button = tk.Button(self.calibrate_frame, text='Calibrate Cage', command=lambda: controller.calibrate_cage())
        calibrate_button.grid(row=1, column=0, columnspan=2, sticky='nsew')

    def fill_static_buttons_frame(self, parent):

        # used to validate that entries are floats
        vcmd_field = (parent.register(self.validate_field), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        vcmd_voltage = (parent.register(self.validate_voltage), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.static_or_dynamic = tk.StringVar()
        self.select_static = tk.Radiobutton(self.static_buttons_frame, text="Static Test: ", variable=self.static_or_dynamic, value="static", font=LARGE_FONT)
        self.select_static.grid(row=0, column=0, columnspan=4, pady=5, sticky='nsew')

        self.field_or_voltage = tk.StringVar()
        field_text = "Enter Magnetic Field \n(Max {} microteslas)".format(max_field_value)
        self.select_field = tk.Radiobutton(self.static_buttons_frame, text=field_text, variable=self.field_or_voltage, value="field")
        self.select_field.grid(row=1, column=0, columnspan=2, sticky='nsew')

        voltage_text = "Enter Voltage \n(Max {} volts)".format(max_voltage_value)
        self.select_voltage = tk.Radiobutton(self.static_buttons_frame, text=voltage_text, variable=self.field_or_voltage, value="voltage")
        self.select_voltage.grid(row=1, column=2, columnspan=2, sticky='nsew')

        self.x_field_label = tk.Label(self.static_buttons_frame, text="x:", font=LARGE_FONT).grid(row=2, column=0, sticky='ns')
        self.x_field = tk.StringVar()
        self.x_field_entry = tk.Entry(self.static_buttons_frame, validate='key', validatecommand=vcmd_field, textvariable=self.x_field, width=10)
        self.x_field_entry.grid(row=2, column=1)

        self.x_voltage_label = tk.Label(self.static_buttons_frame, text="x:", font=LARGE_FONT).grid(row=2, column=2)
        self.x_voltage = tk.StringVar()
        self.x_voltage_entry = tk.Entry(self.static_buttons_frame, validate='key', validatecommand=vcmd_voltage, textvariable=self.x_voltage, width=10)
        self.x_voltage_entry.grid(row=2, column=3)

        self.y_field_label = tk.Label(self.static_buttons_frame, text="y:", font=LARGE_FONT).grid(row=3, column=0)
        self.y_field = tk.StringVar()
        self.y_field_entry = tk.Entry(self.static_buttons_frame, validate='key', validatecommand=vcmd_field, textvariable=self.y_field, width=10)
        self.y_field_entry.grid(row=3, column=1)

        self.y_voltage_label = tk.Label(self.static_buttons_frame, text="y:", font=LARGE_FONT).grid(row=3, column=2)
        self.y_voltage = tk.StringVar()
        self.y_voltage_entry = tk.Entry(self.static_buttons_frame, validate='key', validatecommand=vcmd_voltage, textvariable=self.y_voltage, width=10)
        self.y_voltage_entry.grid(row=3, column=3)

        self.z_field_label = tk.Label(self.static_buttons_frame, text="z:", font=LARGE_FONT).grid(row=4, column=0)
        self.z_field = tk.StringVar()
        self.z_field_entry = tk.Entry(self.static_buttons_frame, validate='key', validatecommand=vcmd_field, textvariable=self.z_field, width=10)
        self.z_field_entry.grid(row=4, column=1)

        self.z_voltage_label = tk.Label(self.static_buttons_frame, text="z:", font=LARGE_FONT).grid(row=4, column=2)
        self.z_voltage = tk.StringVar()
        self.z_voltage_entry = tk.Entry(self.static_buttons_frame, validate='key', validatecommand=vcmd_voltage, textvariable=self.z_voltage, width=10)
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

        time = data.time

        x_mag_field_actual = []
        y_mag_field_actual = []
        z_mag_field_actual = []

        x_mag_field_requested = []
        y_mag_field_requested = []
        z_mag_field_requested = []

        # if a list doesn't have all inputs, they're all assumed to be zero; time will never be missing values
        max_entries = len(time)
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

        # get max and min values for power_supplies_plot and mag_field_plot
        power_supplies_master_list = data.x_out + data.y_out + data.z_out + data.x_req + data.y_req + data.z_req

        # get axes min and max values
        try:
            min_time = min(data.time)
        except Exception as err:
            print("could not get a min time for plot one yet | {}".format(err))
            min_time = 0
        try:
            max_time = max(data.time)
        except Exception as err:
            print("could not get a max time for plot one yet | {}".format(err))
            max_time = 1
        try:
            max_y_plot_one = max(power_supplies_master_list)
        except Exception as err:
            print("could not get a max y for plot one yet | {}".format(err))
            max_y_plot_one = 1
        try:
            min_y_plot_one = min(power_supplies_master_list)
        except Exception as err:
            print("could not get a min y for plot one yet | {}".format(err))
            min_y_plot_one = 0
        mag_field_master_list = x_mag_field_actual + y_mag_field_actual + z_mag_field_actual + x_mag_field_requested + y_mag_field_requested + z_mag_field_requested
        try:
            max_y_plot_two = max(mag_field_master_list)
        except Exception as err:
            print("could not get a max y for plot two yet | {}".format(err))
            max_y_plot_two = 1
        try:
            min_y_plot_two = min(mag_field_master_list)
        except Exception as err:
            print("could not get a min y for plot two yet | {}".format(err))
            min_y_plot_two = 0

        # Power supplies plot
        if data.plots_created == False:
            self.fig, (self.power_supplies_plot, self.mag_field_plot) = plt.subplots(nrows=2, facecolor='grey')

        if data.plots_created == False:
            self.power_supplies_plot = plt.subplot(211)

        self.power_supplies_plot.plot(time, data.x_out, 'r',
                                 time, data.y_out, 'g',
                                 time, data.z_out, 'b',
                                 time, data.x_req, 'r--',
                                 time, data.y_req, 'g--',
                                 time, data.z_req, 'b--')

        plt.ylim(min_y_plot_one, max_y_plot_one)

        # Magnetic field plot
        if data.plots_created == False:
            self.mag_field_plot = plt.subplot(212)

        self.mag_field_plot.plot(time, x_mag_field_actual, 'r',
                             time, y_mag_field_actual, 'g',
                             time, z_mag_field_actual, 'b',
                             time, x_mag_field_requested, 'r--',
                             time, y_mag_field_requested, 'g--',
                             time, z_mag_field_requested, 'b--')

        plt.ylim([min_y_plot_two, max_y_plot_two])


        if data.plots_created == False:
            self.power_supplies_plot.get_shared_x_axes().join(self.power_supplies_plot, self.mag_field_plot)
            self.power_supplies_plot.set_xticklabels([])

            self.power_supplies_plot.set_facecolor("grey")
            self.mag_field_plot.set_facecolor("grey")

            # Add to frame
            self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
            #self.canvas = tk.Canvas(self)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        data.plots_created = True
        self.canvas.draw()


    
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
    if instruments.cage_power == "ON":
        today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if data.log_filename == "":
            data.log_filename = today+"_HelmholtzCageSessionData.csv"
            with open(data.log_filename, 'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['time','x_req', 'y_req', 'z_req', 'x_out', 'y_out', 'z_out', 'x_mag', 'y_mag', 'z_mag'])
        with open(data.log_filename, 'a') as file:
            threading.Timer(update_log_time, log_data).start()
            writer = csv.writer(file, delimiter=',')
            time = int((datetime.datetime.now() - data.start_time).total_seconds())
            #x_req, y_req, z_req = instruments.get_requested_voltage()
            x_req, y_req, z_req = main_page.x_voltage.get(), main_page.y_voltage.get(), main_page.z_voltage.get()
            x_out, y_out, z_out = instruments.get_output_voltage()
            x_mag = 1 #***
            y_mag = 2
            z_mag = 3
            writer.writerow([time,x_req,y_req,z_req,x_out,y_out,z_out,x_mag,y_mag,z_mag])

            data.time.append(time)
            data.x_req.append(x_req)
            data.y_req.append(y_req)
            data.z_req.append(z_req)
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