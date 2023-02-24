#!/usr/bin/env python

"""
Objects and functions to connect with magnetometers.

Copyright 2023 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.
"""


import random


class FakeMagnetometer(object):
    """
    An object for interfacing with magnetometers using a serial 
    interface.
    """
    
    def __init__(self, config):
        
        # Initialize state variables
        self.connected = False
        
    def connect_to_device(self):
        """
        Pretend to connect to a magnetometer.
        """
        
        # Change connection status for magnetometer
        self.connected = True
            
        return self.connected
    
    def get_field_strength(self):
        """
        Pretend to get the actual measured magnetic field strength.
        """
        
        # Generate some random data
        data = [None]*3
        for i in range(0,3):
            data[i] = random.uniform(-0.5, 0.5)
            
        return data
