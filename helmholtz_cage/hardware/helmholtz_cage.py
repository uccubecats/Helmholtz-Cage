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
        self.run_type = ""
        self.ctrl_type = ""
        self.template = None
        self.calibration = None
        self.x_req = 0.0
        self.y_req = 0.0
        self.z_req = 0.0
        
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
        
    def start_cage(self, run_type, ctrl_type):
        """
        Start the Helmholtz Cage
        """
        
        is_okay = True
        
        # Store test parameters
        self.run_type = run_type
        self.ctrl_type = ctrl_type
        
        # Check that all instruments are connected
        if not self.all_connected:
            is_okay = False
            print("WARN: Not all instruments are connected")
        
        # Make sure run type is selected
        elif self.run_type == "":
            is_okay = False
            print("WARN: No test type selected")
        
        # For static tests, make sure control type is selected
        elif self.run_type == "static" and self.ctrl_type == "":
            is_okay = False
            print("WARN: No control type selected for static test")
        
        # For dynamic tests, make sure we have all relevant parameters
        #TODO: Remove once implemented
        elif self.run_type == "dynamic":
            is_okay = False
            print("WARN: Dynamic runs not programmed yet")
        
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
        
        # Reset flags
        self.is_running = False
        self.is_calibrating = False
        
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
    
    def calibrate_cage(self):
        """
        TODO
        """
        pass
        
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
        
    def run_template(self):
        """
        TODO
        """
        pass
        
    def shutdown(self):
        """
        Close down hardware interfaces.
        
        NOTE: Depending on your hardware, further action(s) may be
              required to completely turn off the cage.
        """
        
        self.power_supplies.close()
        self.magnetometer.close()
