#!/usr/bin/env python

"""
Objects and functions to connect with magnetometers.

Copyright 2018-2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.

Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import serial
import time


class SerialMagnetometer(object):
    """
    An object for interfacing with magnetometers using a serial 
    interface.
    """
    
    def __init__(self, address, baudrate):
        
        # Initialize state variables
        self.address = address
        self.baudrate = baudrate
        self.connected = False
        
    def connect_to_device(self):
        """
        Attempt to connect to the magnetometer using Serial.
        """
        
        try:
            # Recreate the serial interface
            self.interface = serial.Serial(self.address,
                                           self.baudrate,
                                           timeout=0.1,
                                           xonxoff=0, 
                                           rtscts=0,
                                           interCharTimeout=None)
            
            # Test that data can be read from connection
            field_string = self.interface.readline().decode("utf-8")
            self.connected = True
        
        except Exception as err:
            print("No connection established to magnetometer | {}".format(err))
            self.connected = False
            
        return self.connected
    
    def get_field_strength(self):
        """
        Read the current magnetic field values from the magnetometer.
        """
       
        valid_characters = ["0", "1", "2", "3", "4", "5",
                            "6", "7", "8", "9", ".", "-"]

        try:
            
            # Reset serial buffer to pervent it from growing too large.
            self.interface.reset_input_buffer()
            time.sleep(0.001)
            
            # Read in data
            field_string = self.interface.readline().decode("utf-8")
            x_string, y_string, z_string = "", "", ""
            currently_reading = None
            
            # Record raw output
            #with open("temp_mag_field_raw.txt", "a") as f:
                #f.write(field_string + "\n")
                #print("read in field data")

            # If currently reading for float, add character if it's valid
            for character in field_string:
                if (currently_reading == "X") and (character in valid_characters):
                    x_string += character
                if (currently_reading == "Y") and (character in valid_characters):
                    y_string += character
                if (currently_reading == "Z") and (character in valid_characters):
                    z_string += character

                # See if it's time to change what is being read
                if character == "X":
                    currently_reading = "X"
                elif character == "Y":
                    currently_reading = "Y"
                elif character == "Z":
                    currently_reading = "Z"

            # Convert the string chunks to floats
            try:
                x_field = float(x_string)
            except Exception as err:
                x_field = None
                print("Could not determine x field from string {} | {}"
                      .format(x_string, err))
            try:
                y_field = float(y_string)
            except Exception as err:
                y_field = None
                print("Could not determine y field from string {} | {}"
                      .format(y_string, err))
            try:
                z_field = float(z_string)
            except Exception as err:
                z_field = None
                print("Could not determine z field from string {} | {}"
                      .format(z_string, err))
            
            return (x_field, y_field, z_field)
        
        # Print 999 so that it is not confused with 0.0
        except AttributeError:
            return (999, 999, 999)
