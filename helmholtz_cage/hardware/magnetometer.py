#!/usr/bin/env python3

"""
  Manager objects to work with magnetometers.

  Copyright 2018-2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.

  Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import serial

from mlx90393 import MLX90393Interface


class SerialMagnetometerManager(MagnetometerManager):
    """
    An object for interfacing with magnetometers which use a serial 
    interface, utilizing the PySerial library.
    """
    
    def __init__(self, config):
        
        super().__init__(config)
        
        # Retrieve parameters from config
        interface_type = self.config["interface"]
        
        # Configure device interface
        self.interface = self.configure_device(self, interface)
    
    def configure_device(self, interface):
        
        # Retrieve important parameters
        port = self.config["port"]
        baudrate = self.config["baudrate"]
        timeout = self.config["timeout"]
        
        # Intialize serial port object
        serial_port = serial.Serial(port,
                                    baudrate,
                                    timeout=timeout,
                                    xonxoff=0, 
                                    rtscts=0,
                                    interCharTimeout=None)
        
        # Find desired device interface
        if interface_type == "MLX90393":
            self.interface = MLX90393Interface(serial_port)
        #elif interface == ...: ADD MORE DEVICE TYPES HERE
        #    ...
        else:
            print("'{}' interface object not found".format(interface))
