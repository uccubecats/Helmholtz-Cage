#!/usr/bin/env python3

"""
  Objects and functions to connect with fake 'placeholder' relay arrays
  
  Copyright 2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


class FakeRelayArray(object):
    """
    An object for interfacing with a "placeholder" relay array.
    """
    
    def __init__(self):
                
        # Initialize state variables
        self.connected = False
        self.x_relay_state = 0
        self.y_relay_state = 0
        self.z_relay_state = 0
        
    def test_connection(self):
        
        # Change connection status
        self.connected = True
        
        return self.connected
        
    def set_states(self, relay_state):
        
        # Set state of each axis' relay(s)
        self.x_relay_state = relay_state[0]
        self.y_relay_state = relay_state[1]
        self.z_relay_state = relay_state[2]
