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
from hardware.relay_array import (
    FakeRelayArrayManager
)


class HelmholtzCage(object):
    """
    A class object for interfacing and controlling with the overall
    Helmholtz Cage, including it's power supplies and magnetometer
    """
    
    def __init__(self, main_dir, ps_config, mag_config, relay_config):
        
        # Store main directory location
        self.main_dir = main_dir
        
        # Store hardware configuration information
        self.ps_config = ps_config
        self.mag_config = mag_config
        self.relay_config = relay_config
        
        # Intialize data storage/logging class
        self.data = Data(main_dir)
        
        # Initialize variables
        self.all_connected = False
        self.is_running = False
        self.is_calibrating = False
        self.has_calibration = False
        self.has_template = False
        self.sep_relays = False
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
        relay_manager = self.relay_config["manager"]
        
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
        
        if relay_manager == "NA":
            self.sep_relays = False
        else:
            self.sep_relays = True
            if relay_manager == "fake":
                self.relay_array = FakeRelayArrayManager(relay_config)
            #elif mag_manager == ... #ADD YOUR MANAGER HERE
            #   ...
            else:
                msg = "Relay array manager of type '{}' not implemented".format(
                relay_manager)
                raise NotImplementedError(msg)
    
    def connect_to_instruments(self):
        """ 
        Refresh the connections to the connected instruments (power 
        supplies, magnetometer, etc.)
        """
        
        # Check each connection
        ps_connected = self.power_supplies.connect_to_device()
        mag_connected = self.magnetometer.connect_to_device()
        if self.sep_relays:
            relay_connected = self.relay_array.connect_to_device()
        else:
            relay_connected = True
        
        # Update flag variable
        if all(ps_connected) and mag_connected and relay_connected:
            self.all_connected = True
        else:
            self.all_connected = False
        
        return ps_connected + [mag_connected] + [relay_connected]
    
    def start_cage(self, run_type, ctrl_type, is_calibration):
        """
        Start the Helmholtz Cage
        """
        
        is_okay = True
        
        # Store test run type
        self.run_type = run_type
        
        # Make sure run type is actually selected
        if self.run_type is None or self.run_type == "":
            is_okay = False
            print("WARN: No test type selected")
        
        # For static tests, make sure control type is selected
        elif self.run_type == "static":
            if ctrl_type is None or ctrl_type == "":
                is_okay = False
                print("WARN: No control type selected for static test")
            else:
                self.ctrl_type = ctrl_type
                
                # Indicate that static tests can't be used to calibrate
                if is_calibration:
                    is_okay = False
                    print("WARN: Can't calibrate from static runs")
                
                # Make sure calibration is given for feild control
                elif self.ctrl_type == "field" and not self.has_calibration:
                    is_okay = False
                    print("WARN: No calibration provided for field control")
        
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
                
                # Catch not having calibration for dynamic field control
                else:
                    if self.ctrl_type == "field" and not self.has_calibration:
                        is_okay = False
                        print("WARN: No calibration provided for field control")
        
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
        
    def determine_relay_state(self, V):
        """
        Simple function to determine if axis relay is active (1) or
        inactive (0).
        """
        
        if V >= 0.0:
            relay_state = 0
        elif V < 0.0:
            relay_state = 1
            
        return relay_state
    
    def set_coil_voltages(self, Vx, Vy, Vz):
        """
        Command a set of desired coil voltages for each axis.
        """
        
        # Ensure the cage is running
        if not self.is_running:
            print("ERROR: Cage is not currently running")
            success = False
        
        else:
            # Set relay states if required
            if self.sep_relays:
                V_cur = [self.data.Vx[-1], self.data.Vy[-1], self.data.Vz[-1]]
                X = self.determine_relay_state(Vx)
                Y = self.determine_relay_state(Vy)
                Z = self.determine_relay_state(Vz)
                relay_success = self.relay_array.set_relay_states([X,Y,Z], V_cur)
            else:
                relay_success = True
        
            # Send voltages to the cages
            if relay_success:
                success = self.power_supplies.send_voltages([Vx, Vy, Vz])
            else:
                success = False
        
        return success
    
    def set_field_strength(self, Bx, By, Bz):
        """
        Command a desired magnetic field vector.
        """
        
        # Determine voltages to produce desired field
        Vx, Vy, Vz = self.calibration.get_voltage_for_desired_field(Bx, By, Bz)
        
        # Command voltages to cage
        success = self.set_coil_voltages(Vx, Vy, Vz)
        
        return success
    
    def zero_field(self):
        """
        Command the cage to zero out the ambient magnetic feild.
        """
        
        # Retrieve zero field voltages from calibration
        Vx = self.calibration.x_equations["x"].zero
        Vy = self.calibration.y_equations["y"].zero
        Vz = self.calibration.z_equations["z"].zero
        
        # Command voltages to cage
        success = self.set_coil_voltages(Vx, Vy, Vz)
        
        return success
    
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
            self.x_req = self.template["x_val"][self.iter]
            self.y_req = self.template["y_val"][self.iter]
            self.z_req = self.template["z_val"][self.iter]
            
            # Set commanded values
            if self.ctrl_type == "voltage":
                is_okay = self.set_coil_voltages(self.x_req, self.y_req,
                                                 self.z_req)
            elif self.ctrl_type == "field":
                is_okay = self.set_field_strength(self.x_req, self.y_req,
                                                  self.z_req)
            
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
        self.calibration.from_data(self.data)
        self.is_calibrating = False
    
    def shutdown(self):
        """
        Close down hardware interfaces.
        
        NOTE: Depending on your hardware, further action(s) may be
              required to completely turn off the cage.
        """
        
        self.power_supplies.close()
        self.magnetometer.close()
