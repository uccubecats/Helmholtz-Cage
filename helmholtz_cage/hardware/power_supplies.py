#!/usr/bin/env python3

"""
  Manager objects to work with power supplies
  
  Copyright 2018-2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import os

import pyvisa as visa

from hardware.fake_power_supply import FakePowerSupply
from hardware.hp603xa import HP603xAInterface
from hardware.instruments import PowerSupplyManager


class GPIBPowerSupplyManager(PowerSupplyManager):
    """
    A power supply manager object class for GPIB-controlled power
    supplies, using the PyVISA library. 'visa_src' must be the path to 
    the locally installed VISA backend.
    
    More info at:
    https://pyvisa.readthedocs.io/en/latest/introduction/getting.html#backend
    """
    
    def __init__(self, config):
        
        # Initialize parent class
        super().__init__(config)
        
        # Initialize PyVISA resource manager
        visa_src = config["visa_path"]
        self.rm = visa.ResourceManager(visa_src)
        
        # Get all currently available visa resources
        #try:
        self.resources = self.rm.list_resources()
        #except Exception as err:
        #    print("WARN: Could not get resource manager resources | {}".format(err))
        #    self.resources = None
        
        # Configure each GPIB power supply
        if self.resources is not None:
            for key in self.devices.keys():
                axis_config = self.config[key]
                self.devices[key] = self.configure_axis_device(key, axis_config)
    
    def configure_axis_device(self, axis, config):
        """
        Configure a GPIB power supply interface before connecting to and
        operating it.
        """
        
        device = None
        
        # Retrieve important parameters
        interface = config["interface"]
        address = config["id"]
        params = config["params"]
        
        # Get resource at address from resource manager
        if address in self.resources:
            resource = self.rm.open_resource(address)
        
            # Initialzie axis
            if config["interface"] == "HP603xA":
                device = HP603xAInterface(axis, address, resource, params)
            #elif interface == ...: ADD MORE DEVICE TYPES HERE
            #    ...
            else:
                msg = "'{}' interface object not found".format(interface)
                raise NotImplementedError(msg)
        
        else:
            print("WARN: '{}' not found in VISA resource list".format(address))
            
        return device
        
    def close(self):
        """
        Close each power supply connection resource, and then close the
        PyVISA resource manager.
        """
        
        # Shutdown each device interface
        for key in self.devices:
            self.devices[key].close()
            
        # Shutdown VISA resource manager
        self.rm.close()


class FakePowerSupplyManager(PowerSupplyManager):
    """
    A power supply manager object to simulate controlling an array of 
    power supplies.
    """
    
    def __init__(self, config):
        
        # Initialize parent class
        super().__init__(config)
        
        # Setup fake power supply objects
        for key in self.devices.keys():
            self.devices[key] = FakePowerSupply(key)
    
