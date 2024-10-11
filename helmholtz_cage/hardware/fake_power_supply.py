#!/usr/bin/env python3

"""
  Objects and functions for a fake 'placeholder' power supply, to use 
  with testing.

  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import random


class FakePowerSupply(object):
    """
    An object for faking a GPIB-capable power supply device within the
    Helmholtz Cage operating software.
    """
    
    def __init__(self, axis):
        
        # Set parameters
        self.axis = axis
        self.is_connected = False
        self.v_lim = 10.0
        self.i_lim = 1.0
        self.r = 10.0
        
        # Set variables
        self.v = 0.0
        self.i = 0.0
    
    def test_connection(self):
        """
        Pretend to connect to the power supply.
        """
        
        return True
    
    def set_voltage(self, v):
        """
        Pretend to send voltage command.
        """
        
        self.v = v
        self.i = self.v/self.r
        
        return True
        
    def get_voltage_output(self):
        """
        Get out fake voltage value.
        """
        
        v_out = self.v + random.uniform(-0.01, 0.01)
        
        return v_out
        
    def get_current_output(self):
        """
        Get out fake current value.
        """
        
        i_out = self.i + random.uniform(-0.01, 0.01)
        
        return i_out
