#!/usr/bin/env python3

"""
  Base classes and methods for connecting with power supply and 
  magnetometer devices.
  
  Copyright 2018-2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.

  Originally written by Jason Roll (rolljn@mail.uc.edu)
"""


import re
import serial


class ReadLine(object):
    """
    A pyserial object wrapper for reading line.
    
    source: https://github.com/pyserial/pyserial/issues/216
    """
    
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
    
    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i + 1]
            self.buf = self.buf[i + 1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]
                return r
            else:
                self.buf.extend(data)


class PowerSupplyManager(object):
    """
    A base object for managing a set of power supplies controlling the
    coils of a Helmholtz Cage.
    
    NOTE: Currently assumes three power supplies one driving a single 
          coil pair
    """
    
    def __init__(self, config):
        
        # Store configuration
        self.config = config       
        
        # Initialize device interface storage dict
        self.devices = {"x-axis": None,
                        "y-axis": None,
                        "z-axis": None}
        
        # Initialize flag variables
        self.is_connected = False
        self.connections_checked = False
    
    def configure_axis(self, interface):
        """
        Placeholder method for inherited class device interface
        configuration.
        
        NOTE: Inherited class must specify this method and call it 
              properly after initilization.
        """
        
        msg = "No 'configure_axis' method override specified for '{}'".format(
            type(self).__name__)
        raise NotImplementedError(msg)
    
    def connect_to_device(self):
        """
        Attempt to connect to all system power supplies.
        """
        
        is_connected = {}
        
        # Attempt to connect to each power supply interface
        for key in self.devices.keys():
            #try:
            device_connected = self.devices[key].test_connection()
            is_connected.update({key: device_connected})
            #except Exception as err:
            #    print("Error in connecting to {} device | {}"
            #        .format(key, err))
        
        # Convert connections status to list
        connect_list = self.dict_to_list(is_connected)
        
        # Set overall is connected flag
        self.is_connected = all(connect_list)
        
        return connect_list
    
    def send_voltages(self, voltages):
        """
        Send the commanded voltage values to the power supplies.
        """
        
        # Convert command list to power supply dict
        cmds = self.list_to_dict(voltages)
        
        # Attempt to set each device voltage
        for key in self.devices.keys(): 
            try: 
                self.devices[key].set_voltage(cmds[key])
                success = True
            except ValueError:
                print("WARN: Commanded voltage for {} higher than set limit".format(
                    key))
                success = False
                # TODO: more to handle this?
            #except Exception as err:
            #    print("Could not send {} voltage | {}".format(key, err))
        
        return success
        
    def get_power_data(self):
        """
        Get the actual measured voltage and current on the power 
        supplies.
        """
        
        v_data = {}
        i_data = {}
        
        # Attempt to retrieve each device output voltage
        for key in self.devices.keys(): 
            #try:
            v = self.devices[key].get_voltage_output()
            v_data.update({key: v})
            #except Exception as err:
            #    print("Could not get {} voltage | {}".format(key, err))
        
        # Attempt to retireve each device output current
        for key in self.devices.keys(): 
            #try:
            i = self.devices[key].get_current_output()
            i_data.update({key: i})
            #except Exception as err:
            #    print("Could not get {} current | {}".format(key, err))
        
        # Package both voltage and current data into list
        v_list = self.dict_to_list(v_data)
        i_list = self.dict_to_list(i_data)
        data_list = v_list + i_list
        
        return data_list
        
    def close(self):
        """
        Close the manager and perform any cleanup activities required by
        the power supply interface(s).
        
        NOTE: Inherited class should implement this function on an as
              needed basis.
        """
        pass
    
    def dict_to_list(self, dict_in):
        """
        Convert a dictionary with power supply related information into 
        a properly ordered list.
        """
        
        list_out = [dict_in["x-axis"],
                    dict_in["y-axis"],
                    dict_in["z-axis"]]
        
        return list_out
    
    def list_to_dict(self, list_in):
        """
        Convert a list with power supply related information into a 
        properly formatted dictionary.        
        """
        
        dict_out = {"x-axis": list_in[0],
                    "y-axis": list_in[1],
                    "z-axis": list_in[2]}
        
        return dict_out


class MagnetometerManager(object):
    """
    A base object for managing a control magnetometer for the Helmholtz
    Cage.
    
    NOTE: Currently assumes a single magnetometer device; possibly
    usable for 3x single axis magnetometers with proper interface.
    """
    
    def __init__(self, config):
        
        # Store config information
        self.config = config
        
        # Intialize interface object
        self.interface = None
        
        # Initialize variables
        self.is_connected = False
        
    def configure_device(self, interface):
        """
        Placeholder method for inherited class device interface
        configuration.
        
        NOTE: Inherited class must specify this method and call it 
              properly after initilization.
        """
        
        msg = "No 'configure_device' method override specified for {}".format(
            type(self).__name__)
        raise NotImplementedError(msg)
    
    def connect_to_device(self):
        """
        Attempt to connect to the magnetometer.
        """
        
        # Attempt to connect to Magnetometer
        #try:
        self.is_connected = self.interface.test_connection()
        #except Exception as err:
        #    print("Error in connecting to magnetometer device | {}"
        #            .format(err))
        
        return self.is_connected
    
    def get_field_strength(self):
        """
        Read the current magnetic field values from the magnetometer.
        """
        
        #try:
        data = self.interface.read_sensor()
        #except Exception as err:
        #    print("Could not read field values | {}". format(err))
        
        return data
        
    def close(self):
        """
        Close the manager and perform any cleanup activities required by
        the magnetometer interface.
        
        Note: Inherited class should implement this function only if
              needed.
        """
        pass
