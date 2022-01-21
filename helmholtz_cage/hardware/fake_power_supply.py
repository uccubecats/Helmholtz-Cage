#!/usr/bin/env python

"""
  Objects and functions for a fake 'placeholder' power supply, to use 
  with testing the gort.

  Copyright 2021 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import random


class FakePowerSupplyManager(object):
    """
    An object for faking a set of three GPIB-capable power supplies 
    connected using a GPIB daisy chain. Useful for testing the system 
    without access to actual power supplies.
    """
    
    def __init__(self, config):
        
        # Power supply parameters
        self.axes = ["X", "Y", "Z"]
        self.log_data = "ON"
        self.connections_checked = True
        self.is_connected = [False, False, False]
        self.voltages = [0.0, 0.0, 0.0]
        self.resistance = 0.01
        
    def connect_to_device(self):
        """
        Pretend to connect to power supplies.
        """
        
        # Change the connection status for each power supply
        for i in range(0,3):
            self.is_connected[i] = True
            
        return self.is_connected
        
    def send_voltage(self, voltages):
        """
        Pretend to send commanded voltage values to power supplies.
        """
        for i in range(0,3):
            self.voltages[i] = voltages[i]
            
    def stop_field(self):
        """
        Kill all current to all power supplies.
        """
        pass
        
    def get_requested_voltage(self):
        """
        Pretend getting the currently commanded voltages on power
        supplies.
        """
        
        data = [None]*3
        for i in range(0,3):
            data[i] = self.voltages[i]
            
        return data
        
    def get_power_data(self):
        """
        Pretend to get the actual measured voltage and current on the 
        power supplies.
        """
        
        data = [None]*6
        for i in range(0,3):
            data[i] = self.voltages[i] + random.uniform(-0.1, 0.1)
            data[i+3] = data[i]/self.resistance
            
        return data
