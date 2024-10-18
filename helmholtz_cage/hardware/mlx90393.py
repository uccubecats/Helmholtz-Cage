#!/usr/bin/env python3

"""
  MLX90939 magnetometer interface object source code.
  
  Copyright 2018-2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import time


class MLX90393Interface(object):
    """
    An interface object for the MLX90393 magnetometer using the PySerial
    library.
    """
    
    def __init__(self, serial_obj):
        
        # Retrieve main parameters
        self.wait_time = 0.001
        
        # Store important char lists
        self.keys = ["X", "Y", "Z"]
        self.valid_chars = ["0", "1", "2", "3", "4", "5",
                            "6", "7", "8", "9", ".", "-"]
        
        # Intialize serial port object
        self.serial_port = serial_obj
        
        # Initialize variables
        self.is_connected = False
    
    def test_connection(self):
        """
        Check to see if the device is connected and sending data over
        the serial port connection.
        """
        
        # Retrieve test line from serial port
        test_str = self.serial_port.readline().decode("utf-8")
        
        # Look for expected key chars
        if any(k in test_str for k in self.keys):
            self.is_connected = True
        else:
            self.is_connected = False
        
        return self.is_connected
    
    def read_sensor(self):
        """
        Extract magnetic field data from incoming string messages via 
        the serial port.
        """
        
        # Read in data
        try:
            field_str = self.serial_port.readline().decode("utf-8")
            x_str, y_str, z_str = "", "", ""
            currently_reading = None
            
            # Reset serial buffer to pervent it from growing too large.
            self.serial_port.reset_input_buffer()
            
            # If currently reading for float, add character if it's valid
            for char in field_str:
                if currently_reading == "X" and char in self.valid_chars:
                    x_str += char
                if currently_reading == "Y" and char in self.valid_chars:
                    y_str += char
                if currently_reading == "Z" and char in self.valid_chars:
                    z_str += char
                
                # See if it's time to change what is being read
                if char == "X":
                    currently_reading = "X"
                elif char == "Y":
                    currently_reading = "Y"
                elif char == "Z":
                    currently_reading = "Z"
                elif char == "E":
                    break
            
            # Convert the string chunks to floats
            try:
                x_field = float(x_str)
            except Exception as err:
                x_field = 999.0
                print("Could not determine x field from string {} | {}"
                      .format(x_str, err))
            try:
                y_field = float(y_str)
            except Exception as err:
                y_field = 999.0
                print("Could not determine y field from string {} | {}"
                      .format(y_string, err))
            try:
                z_field = float(z_string)
            except Exception as err:
                z_field = 999.0
                print("Could not determine z field from string {} | {}"
                      .format(z_str, err))
            
            return (x_field, y_field, z_field)
        
        # Print 999 so that it is not confused with 0.0
        except AttributeError:
            return (999.0, 999.0, 999.0)
            
    def close(self):
        """
        Shutdown the serial port.
        """
        
        self.serial_port.close()
