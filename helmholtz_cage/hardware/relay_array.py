#!/usr/bin/env python3

"""
  Manager objects to work with magnetometers.

  Copyright 2018-2025 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


from hardware.fake_relay_array import FakeRelayArray
from hardware.instruments import RelayArrayManager


class ArduinoRelayArrayManager(RelayArrayManager):
    """
    A manager object for interfacing with the CubeCats design relay
    array.
    
    TODO: Test
    """
    
    def __init__(self, config):
                
        # Initialize parent class
        super().__init__(config)
                
        # Retrieve parameters from config
        interface_config = self.config["interface"]
                
        # Configure device interface
        self.interface = self.configure_device(interface_config)
        
    def configure_device(self, interface_type):
        
        # Retrieve important parameters
        port = self.config["port"]
        baudrate = self.config["baudrate"]
        timeout = self.config["timeout"]
        limits = self.config["switch_limits"]
        
        # Intialize serial port object
        serial_port = serial.Serial(port,
                                    baudrate,
                                    timeout=timeout,
                                    xonxoff=0, 
                                    rtscts=0,
                                    interCharTimeout=None)
        
        # Find desired device interface
        if interface_type == "Pololu2486":
            interface = Pololu2486ControlInterface(serial_port, limits)
        #elif interface_type == ...: ADD MORE DEVICE TYPES HERE
        #    ...
        else:
            msg = "'{}' interface object not found".format(interface)
            raise NotImplementedError(msg)
        
        return interface
    
    def close(self):
        
        self.interface.close()


class FakeRelayArrayManager(RelayArrayManager):
    """
    A manager object to simulate interfacing with relay array.
    """
    
    def __init__(self, config):
        
        # Initialize parent class
        super().__init__(config)
        
        # Initialize fake relay interface
        self.interface = FakeRelayArray()
