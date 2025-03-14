#!/usr/bin/env python3

"""
  Pololu 2386-based relay array interface source code.
  
  Copyright 2018-2025 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


class Pololu2486ControlInterface(object):
    """
    An interface object for a relay array consisting of three 
    Pololu 2486 dual relay modules (one controlling current direction on
    each axis) controlled from a Arduino.
    
    TODO: Test
    """
    
    def __init__(self, serial_obj, limits):
        
        # Store main parameters
        self.wait_time = 0.001
        
        # Store important char lists
        self.keys = ["X", "Y", "Z"]
        
        # Store limits in proper order
        self.limits = []
        for key in self.keys:
            self.limits.append(limits[key])
         
        # Intialize serial port object
        self.serial_port = serial_obj
        
        # Initialize variables
        self.is_connected = False
        self.states = [0, 0, 0]
    
    def test_connection(self):
        """
        Check to see if the device is connected and communicating over 
        the serial bus.
        """
        
        # Create connection check message
        test_msg = "CHECK".encode("utf-8")
        
        # Write message to arduino and listen for response
        self.serial_port.write(test_msg)
        resp_str = self.serial_port.readline().decode("utf-8")
        
        # Check if response recieved
        if "ACK" in resp_str:
            self.is_connected = True
        else:
            self.is_connected = False
        
        return self.is_connected
        
    def set_states(self, relay_cmd, current):
        """
        Set the states of all relay pairs, while checking whether this 
        state is different than the current state and if we can safely
        switch at the current amperage.
        """

        cmd_msg = ""

        # Add switch command only if different from current state
        for i in range(0,3):
            if current[i] <= self.limits[i]:
                if self.states[i] != relay_cmd[i]:
                    cmd_msg += "{}:{}".format(self.key[i], relay_cmd[i])
                    self.state[i] = relay_cmd[i]
                else:
                    pass
            
            # Raise error if beyond safe switching voltage
            else:
                raise ValueError(self.keys[i])
                
        # If not empty, send command on serial port
        if cmd_msg != "":
            cmd = "SET" + cmd_msg
            self.serial_port.write(cmd.encode("utf-8"))
    
    def close(self):
        """
        Shutdown the serial port.
        """
        
        self.serial_port.close()
