#!/usr/bin/env python3

"""
  
  
  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


from hardware.fake_relay_array import FakeRelayArray
from hardware.instruments import RelayArrayManager


class FakeRelayArrayManager(RelayArrayManager):
    """
    A manager object to simulate interfacing with relay magnetometer.
    """
    
    def __init__(self, config):
        
        # Initialize parent class
        super().__init__(config)
        
        # Initialize fake relay interface
        self.interface = FakeRelayArray()
