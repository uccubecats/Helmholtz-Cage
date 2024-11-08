#!/usr/bin/env python3

"""
  Helmholtz Cage object module source code
  
  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import datetime

from data.calibration import Calibration
from data.data import Data
from utilities.template import retrieve_template, check_template_values

# Implementation specific imports (Replace with yours as needed)
from hardware.power_supplies import (
    GPIBPowerSupplyManager, FakePowerSupplyManager
)
from hardware.magnetometer import (
    SerialMagnetometerManager, FakeMagnetometerManager
)


class HelmholtzCage(object):
    """
    A class object for interfacing and controlling with the overall
    Helmholtz Cage, including it's power supplies and magnetometer
    """
    
    def __init__(self, main_dir, ps_config, mag_config):
        
        # Store main directory location
        self.main_dir = main_dir
        
        # Store hardware configuration information
        self.ps_config = ps_config
        self.mag_config = mag_config
        
        # Intialize data storage/logging class
        self.data = Data(main_dir)
        
        # Initialize variables
        self.all_connected = False
        self.is_running = False
        self.is_calibrating = False
        self.has_calibration = False
        self.has_template = False
        self.run_type = None
        self.ctrl_type = None
        self.template = None
        self.calibration = None
        self.x_req = 0.0
        self.y_req = 0.0
        self.z_req = 0.0
        self.iter = 0
        
        # Setup instrument interface managers
        # NOTE: replace 'elif' options with managers for your hardware
        ps_manager = self.ps_config["manager"]
        mag_manager = self.mag_config["manager"]
        
        if ps_manager == "fake":
            self.power_supplies = FakePowerSupplyManager(ps_config)
        elif ps_manager == "gpib":
            self.power_supplies = GPIBPowerSupplyManager(ps_config)
        #elif ps_manager == ... #ADD YOUR MANAGER HERE
        #   ...
        else:
            msg = "Power supply manager of type '{}' not implemented".format(
                ps_manager)
            raise NotImplementedError(msg)
        
        if mag_manager == "fake":
            self.magnetometer = FakeMagnetometerManager(mag_config)
        elif mag_manager == "serial":
            self.magnetometer = SerialMagnetometerManager(mag_config)
        #elif mag_manager == ... #ADD YOUR MANAGER HERE
        #   ...
        else:
            msg = "Magnetometer manager of type '{}' not implemented".format(
                mag_manager)
            raise NotImplementedError(msg)
    
    def connect_to_instruments(self):
        """ 
        Refresh the connections to the connected instruments (power 
        supplies, magnetometer, etc.)
        """

        # Check each connection
        ps_connected = self.power_supplies.connect_to_device()
        mag_connected = self.magnetometer.connect_to_device()
        
        # Update flag variable
        if all(ps_connected) and mag_connected:
            self.all_connected = True
        else:
            self.all_connected = False
        
        return ps_connected, mag_connected
    
    def start_cage(self, run_type, ctrl_type, is_calibration):
        """
        Start the Helmholtz Cage
        """
        
        is_okay = True
        
        # Store test run type
        self.run_type = run_type
        
        # Make sure run type is actually selected
        if self.run_type is None:
            is_okay = False
            print("WARN: No test type selected")
        
        # For static tests, make sure control type is selected
        elif self.run_type == "static":
            if self.ctrl_type is None:
                is_okay = False
                print("WARN: No control type selected for static test")
            else:
                self.ctrl_type = ctrl_type
                
                # Indicate that static tests can't be used to calibrate
                if is_calibration:
                    print("WARN: Can't calibrate from static runs")
        
        # For dynamic tests, make sure we have all relevant parameters
        elif self.run_type == "dynamic":
            if self.template is None:
                is_okay = False
                print("WARN: No template provided for dynamic run")
            else:
                self.ctrl_type = self.template["type"]
                self.iter = 0
                if is_calibration:
                    self.is_calibrating = True
        
        # Check that all instruments are connected
        if not self.all_connected:
            is_okay = False
            print("WARN: Not all instruments are connected")
        
        # Set flag
        if is_okay:
            self.is_running = True
        
        # Store request type if different
        if self.data.req_type != ctrl_type:
            self.data.req_type = ctrl_type
        
        return is_okay
    
    def stop_cage(self):
        """
        Stop the Helmholtz Cage.
        """
        
        # Set voltages on coils to zero
        success = self.set_coil_voltages(0.0, 0.0, 0.0)
        
        # Reset flags and variables
        self.is_running = False
        self.iter = 0
        
        return success
        
    def update_data(self):
        """
        Store all current data from attached sensors and devices.
        """
        
        # Get time
        time_now = datetime.datetime.now()
        time_elapsed = float((time_now - self.data.start_time).total_seconds())
        self.data.time.append(time_elapsed)
        
        # Store requested values
        self.data.x_req.append(self.x_req)
        self.data.y_req.append(self.y_req)
        self.data.z_req.append(self.z_req)
        
        # Get power supply voltage and currents
        power_data = self.power_supplies.get_power_data()
        self.data.Vx.append(power_data[0])
        self.data.Vy.append(power_data[1])
        self.data.Vz.append(power_data[2])
        self.data.Ix.append(power_data[3])
        self.data.Iy.append(power_data[4])
        self.data.Iz.append(power_data[5])
        
        # Get magnetic field_data
        mag_data = self.magnetometer.get_field_strength()
        self.data.Bx.append(mag_data[0])
        self.data.By.append(mag_data[1])
        self.data.Bz.append(mag_data[2])
        
        return self.data
    
    def set_coil_voltages(self, Vx, Vy, Vz):
        """
        Command a set of desired coil voltages for each axis.
        """
        
        # Ensure the cage is running
        if not self.is_running:
            print("ERROR: Cage is not currently running")
            success = False
        
        # Send voltages to the cages
        else:
            success = self.power_supplies.send_voltages([Vx, Vy, Vz])
            
            # Store commanded values
            if success:
                self.x_req = Vx
                self.y_req = Vy
                self.z_req = Vz
        
        return success
        
    def set_field_strength(self, Bx, By, Bz):
        """
        TODO
        """
        pass
        
    def zero_field(self):
        """
        TODO
        """
        pass
        
    def run_once(self):
        """
        Cycle through one command in the template file and determine 
        the time for the next cycle to stop. Indicate the template is 
        complete once out of points to iterate through.
        """
            
        # Signal completion once out of points
        if self.iter+1 >= len(self.template["time"]):
            dt = -1.0
            finished = True
        
        # Get current iteration command values
        else:
            time = self.template["time"][self.iter]
            dt = self.template["time"][self.iter+1] - time
            x_cmd = self.template["x_val"][self.iter]
            y_cmd = self.template["y_val"][self.iter]
            z_cmd = self.template["z_val"][self.iter]
            
            # Set commanded values
            if self.ctrl_type == "voltage":
                is_okay = self.set_coil_voltages(x_cmd, y_cmd, z_cmd)
            elif self.ctrl_type == "field":
                is_okay = self.set_field_strength(x_cmd, y_cmd, z_cmd)
                
            # Set next index
            self.iter += 1
            
            finished = False
        
        return dt, finished
        
    def calibrate(self, calibration_dir):
        """
        Call the calibration function on the data from the current run
        should only be run at the end of the 
        """
        
        # Create file name
        start_t_str = self.data.start_time.strftime('%Y_%m_%d')
        calibration_file = "calibration_{}.csv".format(start_t_str)
        
        # Initialize calibration object
        self.calibration = Calibration(calibration_dir, calibration_file)
        
        # Run the calibration process
        calibration_output = self.calibration.from_data(self.data)
        self.is_calibrating = False
        
        return calibration_output
    
    def shutdown(self):
        """
        Close down hardware interfaces.
        
        NOTE: Depending on your hardware, further action(s) may be
              required to completely turn off the cage.
        """
        
        self.power_supplies.close()
        self.magnetometer.close()
