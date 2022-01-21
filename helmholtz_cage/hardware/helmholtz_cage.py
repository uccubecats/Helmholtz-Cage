"""
Helmholtz Cage object module

Copyright 2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit
history.
"""


import datetime
import logging

from data.calibration import Calibration
from data.data import Data
from hardware.instruments import GPIBDaisyChainPS
from hardware.fake_power_supply import FakePowerSupplyManager
from hardware.magnetometer import SerialMagnetometer
from utilities.template import retrieve_template, check_template_values


class HelmholtzCage(object):
    """
    A class object for the Helmholtz Cage.
    """
    
    def __init__(self, main_dir, ps_config, mag_config):
        
        # Store main directory location
        self.main_dir = main_dir
        
        # Store hardware configuration information
        self.ps_config = ps_config
        self.mag_config = mag_config
        
        # Data storage/logging class
        self.data = Data(main_dir)
        
        # System state variables
        self.all_connected = False
        self.is_running = False
        self.is_calibrating = False
        self.has_calibration = False
        self.has_template = False
        self.static_or_dynamic = ""
        self.field_or_voltage = ""
        self.template = None
        self.calibration = None
        
        # Insturment interfaces
        self.power_supplies = None
        self.magnetometer = None
        
        # System commands
        self.x_req = 0.0
        self.y_req = 0.0
        self.z_req = 0.0
        
    def connect_to_instruments(self):
        """ 
        Refresh the connections to the connected instruments (power 
        supplies, magnetometer, etc.)
        """
        
        # Instantiate interface objects for each instrument
        #TODO: handle other types of managers
        self.power_supplies = FakePowerSupplyManager(self.ps_config)
        self.magnetometer = SerialMagnetometer(self.mag_config) 

        # Check each connection
        ps_connected = self.power_supplies.connect_to_device()
        mag_connected = self.magnetometer.connect_to_device()
        
        # Update flag variable
        if all(ps_connected) and mag_connected:
            self.all_connected = True
        
        return ps_connected, mag_connected
        
    def start_cage(self, run_type, ctrl_type):
        """
        Start the Helmholtz Cage
        
        TODO: Test
        """
        
        is_okay = True
        
        # Store test parameters
        self.static_or_dynamic = run_type
        self.field_or_voltage = ctrl_type
        
        # Check that all instruments are connected
        if not self.all_connected:
            is_okay = False
        
        # For dynamic tests, make sure we have the parameters we need
        if self.static_or_dynamic == "dynamic":
            pass # TODO
        
        # Set the flag
        if is_okay:
            self.is_running = True
        
        return is_okay

    def stop_cage(self):
        """
        Stop the Helmholtz Cage.
        
        TODO: Test
        """
        
        # Set voltages on the coils to zero
        success = self.set_coil_voltages(0.0, 0.0, 0.0)
        
        # Reset flags
        self.is_running = False
        self.is_calibrating = False
        
        return success
        
    def update_data(self):
        """
        Refresh all data from the cage.
        
        TODO: Test
        """
        
        # Get time
        time_now = datetime.datetime.now()
        time_elapse = int((time_now - self.data.start_time).total_seconds())
        self.data.time.append(time_elapse)
        
        # Store requested values
        self.data.x_req.append(self.x_req)
        self.data.y_req.append(self.y_req)
        self.data.z_req.append(self.z_req)
        self.data.req_type.append(self.field_or_voltage)
        
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
    
    def calibrate_cage(self):
        """
        TODO
        """
        pass
        
    def set_coil_voltages(self, Vx, Vy, Vz):
        """
        Send a set of axis coil voltages.
        
        TODO: Test
        """
        
        # Ensure the cage is running
        if not self.is_running:
            print("ERROR: Cage is not currently running")
            return False
            
        # Validate input voltages
        #TODO
        
        # Send voltages to the cages
        self.power_supplies.send_voltage([Vx, Vy, Vz])
        
        return True
        
    def set_field_strength(self, Bx, By, Bz):
        """
        TODO
        """
        pass
        
    def set_static_value(self):
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
