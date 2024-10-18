#!/usr/bin/env python3

"""
  HP603xA series power supply interface object source code.
  
  Copyright 2018-2024 UC CubeCats
  All rights reserved. See LICENSE file at:
  https://github.com/uccubecats/Helmholtz-Cage/LICENSE
  Additional copyright may be held by others, as reflected in the commit
  history.
"""


MODELS = {"HP6030A": 
              {"V_limit": 200,
               "I_limit": 17,
               "P_limit": 1000},
          "HP6031A":
              {"V_limit": 20,
               "I_limit": 120,
               "P_limit": 840},
          "HP6032A":
              {"V_limit": 60,
               "I_limit": 50,
               "P_limit": 1000},
          "HP6033A":
              {"V_limit": 20,
               "I_limit": 30,
               "P_limit": 200},
          "HP6035A":
              {"V_limit": 500,
               "I_limit": 5,
               "P_limit": 1000},
          "HP6038A":
              {"V_limit": 60,
               "I_limit": 10,
               "P_limit": 200}}


class HP603xAInterface(object):
    """
    An interface object for the HP603x series power supplies using the 
    PyVISA library.
    
    NOTE: Does not impliment all functions of the power supplies
    TODO: Add more functionality if needed.
    """
    
    def __init__(self, axis, id_str, resource, params):
        
        # Store main parameters
        self.axis = axis
        self.id = id_str
        self.v_lim = params["max_voltage"]
        self.i_lim = params["max_current"]
        
        # Store PyVISA interface
        self.resource = resource
        
        # Create and store name
        self.name = "{}-axis power supply".format(axis)
        
        # Initialize other variables/parameters
        self.is_connected = False
        self.v_set = 0.0
        self.v_max = 0.0
        self.i_max = 0.0
        self.model = None
    
    def test_connection(self):
        """
        Check to see if the device is connected and responding to
        queries.
        """
        
        # Ask for ID
        out = self.resource.query("ID?")
        
        # If ID returned, set connection parameter
        if "ID" in out:
            self.is_connected = True
            
            # Set parameters for power supply model
            if self.model is None:
                self.model = self.format_query_resp(out, "ID", "str")
                self.v_max = MODELS[self.model]["V_limit"]
                self.i_max = MODELS[self.model]["I_limit"]
            
            # Write important parameters to device
            self.set_voltage_limit(self.v_lim)
            self.set_current_limit(self.i_lim)
        
        # Otherwise, set connection variable to False
        else:
            self.is_connected = False
        
        return self.is_connected
    
    def set_voltage_limit(self, v_lim):
        """
        Set the device's maximum voltage limit.
        
        NOTE: this is a 'soft' limit due to most likely being lower than
        the device's maximum output limit.
        """
        
        okay = True
        
        # Prevent voltage limit being set over device maximum
        if v_lim > self.v_max:
            raise ValueError
        
        # Write limit value if not same as current value
        elif v_lim != self.v_lim:
            self.resource.write("VMAX {} V".format(v_lim))
            self.v_lim = v_lim
        
        return okay
    
    def set_current_limit(self, i_lim):
        """
        Set the device's maximum current limit.
        
        NOTE: this is a 'soft' limit due to most likely being lower than
        the device's maximum output limit.
        """
        
        okay = True
        
        # Prevent current limit being set over device maximum
        if i_lim > self.i_max:
            raise ValueError
                
        # Write limit value if not same as current value
        elif i_lim != self.i_lim:
            self.resource.write("IMAX {} A".format(i_lim))
            self.i_lim = i_lim
            
        return okay
    
    def set_voltage(self, v):
        """
        Set the device's command voltage.
        """
        
        okay = True
        
        # Prevent commands larger than device maximum
        if v > self.v_lim:
            raise ValueError
        
        # Write voltage cmd if not same as current cmd
        elif v != self.v_set:
            self.resource.write("VSET {} V".format(v))
            self.v_set = v
    
    def get_voltage_output(self):
        """
        Get the device's measured (actual) voltage output.
        """
        
        out = self.resource.query("VOUT?")
        v_out = self.format_query_resp(out, "VOUT", "float")
        
        return v_out
    
    def get_current_output(self):
        """
        Get the device's measured (actual) current output.
        """
        
        out = self.resource.query("IOUT?")
        i_out = self.format_query_resp(out, "IOUT", "float")
        
        return i_out
    
    def reset(self):
        """
        Reset the device if it has been disabled by onboard processes 
        (OVP, foldback, remote inhibit, etc.)
        """
        
        # Set commanded voltage to 0V
        self.set_voltage(0.0)
        
        # Write reset command
        self.resource.write("RST")
    
    def get_error(self):
        """
        Ask the device for the current error code, and return an 
        appropriate error message.
        """
        
        has_err = True
        
        # Ask for error code
        err_out = self.resource.query("ERR?")
        err_code = self.format_query_resp(err_out, "ERR", "int")
        
        # Retreive error message
        if err_code == 0:
            has_err = False
        elif err_code == 1:
            err_str = "Unrecognized character recieved in command/query"
        elif err_code == 2:
            err_str = "Improper number recieved in command/query"
        elif err_code == 3:
            err_str = "Unrecognized string recieved in command/query"
        elif err_code == 4:
            err_str = "Syntax error in command/query"
        elif err_code == 5:
            err_str = "Number in command out of range"
        elif err_code == 6:
            err_str = "Commanded value exceeds set limits"
        elif err_code == 7:
            err_str = "Attempted to set limit with invalid value"
        elif err_code == 8:
            err_str = "Data requested without prerequisite query"
        elif err_code == 9:
            err_str = "Relay accessory is not connected or improperly configured"
        
        # Add name of power supply to error
        if has_err:
            print(err_str + " for " + self.name)
        
        return has_err
    
    def format_query_resp(self, resp, cmd, out_type):
        """
        Removing carrage returns, line breaks, command titles, etc.. 
        from a query response, and ensure proper typing for the actual
        message content.
        """
        
        # Remove uneeded elements from response
        resp = resp.replace(cmd, "")
        resp = resp.replace("\n", "")
        resp = resp.replace("\r", "")
        resp = resp.replace(" ", "")
        
        # Properly type message
        if out_type == "str":
            resp_out = str(resp)
        elif out_type == "int":
            resp_out = int(resp)
        elif out_type == "float":
            resp_out = float(resp)
        
        return resp_out
        
    def close(self):
        """
        Close the PyVISA resource (interface).
        """
        
        self.resource.close()
