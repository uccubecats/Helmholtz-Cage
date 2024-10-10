#!/usr/bin/env python3

"""
  Manager objects to work with power supplies
  
  Copyright 2018-2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


import pyvisa as visa

from instruments import PowerSupplyManager
from hp603xa import HP603xAInterface


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
        try:
            self.resources = self.rm.list_resources()
        except Exception as err:
            print("Could not get resource manager resources | {}".format(err))
            self.resources = None
        
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
                print("'{}' interface object not found".format(interface))
        
        else:
            print("'{}' not found in VISA resource list".format(address))
            
        return device
