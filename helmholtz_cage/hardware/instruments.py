#!/usr/bin/env python

"""
Objects and functions to connect with power supplies and magnetometers.

Copyright 2018-2021 UC CubeCats
All rights reserved. See LICENSE file at:
https://github.com/uccubecats/Helmholtz-Cage/LICENSE
Additional copyright may be held by others, as reflected in the commit history.

Originally written by Jason Roll (rolljn@mail.uc.edu)

TODO: run through it and check new classes/functions.
"""


import logging
import re
import serial
import pyvisa as visa

logger = logging.getLogger(__name__)
# visa.log_to_screen()


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

class GPIBDaisyChainPS(object):
    """
    An object for dealing with a set of three GPIB-capable power supplies 
    connected using a GPIB daisy chain.
    """
    
    def __init__(self):
        
        # Note: Check these are correct for your setup
        self.axes = ["X", "Y", "Z"]
        self.id = ["GPIB0::3::INSTR","GPIB0::5::INSTR","GPIB0::4::INSTR"]
        self.resources = 3*["no connection"]
        self.log_data = "ON"
        self.connections_checked = True
        self.is_connected = [False, False, False]
        
        # Create a VISA Resource Manager object
        self.rm = visa.ResourceManager()

    def connect_to_device(self):
        """
        Attempt connections to the power supplies and magnetometer.
        
        NOTE: The control computer may store the power supply addresses 
              in memory, and show they have connected to them, even when
              the cables are completely disconnected. A zero voltage 
              command needs to be sent to confirm successful connection.
              
        TODO: Test
        """
        
        self.is_connected = [False, False, False]
        
        # Get a list of connected devices
        try:
            connected_devices = rm.list_resources()
        except Exception as err:
            print("Could not get resource manager resources | {}".format(err))
            
        # Send 0V commands to see if connections were actually made            
        for connection in connected_devices:
            for i in range(0,3):
                if device == self.id[i]:
                    self.resources[i] = rm.open_resource(connection)
                    try:
                        self.resources[i].write("VSET 0 V")
                        self.is_connected[i] = True
                    except:
                        print("No connection established to {} | {}"
                            .format(self.resource[i],err))
            
        return self.is_connected
        
            # if connection == self.id[0]:
                # self.x = rm.open_resource(connection)
                # try:
                    # self.x.write("VSET 0 V")
                    # self.is_connected = True
                # except Exception as err:
                    # print(
                        # "No X Power Supply connection established to {} | {}".format(
                            # self.x, err))
                    # self.x = "No connection"
                    # self.is_connected[0] = False
                    
            # elif connection == self.y_id:
                # self.y = rm.open_resource(connection)
                # try:
                    # self.y.write("VSET 0 V")
                    # self.is_connected[1] = True
                # except Exception as err:
                    # print(
                        # "No Y Power Supply connection established to {} | {}".format(
                            # self.y, err))
                    # self.y = "No connection"
                    # self.is_connected[1] = False
                    
            # elif connection == self.z_id:
                # self.z = rm.open_resource(connection)
                # try:
                    # self.z.write("VSET 0 V")
                    # self.is_connected[2] = True
                # except Exception as err:
                    # print(
                        # "No Z Power Supply connection established to {} | {}".format(
                            # self.z, err))
                    # self.z = "No connection"
                    # self.is_connected[2] = False

    def send_voltage(self, voltages):
        """
        Send the commanded voltage values to the power supplies.
        
        TODO: Test
        """
        
        for i in range(0,3):
            try:
                command = "VSET {} V".format(voltages[i])
                self.resource[i].write(command)
            except:
                print("Could not send {} voltage | {}".format(
                    self.axis[i], err))
        
        # try:
            # self.x.write(("VSET {} V").format(x_voltage))
        # except Exception as err:
            # print("Could not send x voltage | {}".format(err))
            
        # try:
            # self.y.write(("VSET {} V").format(y_voltage))
        # except Exception as err:
            # print("Could not send y voltage | {}".format(err))
            
        # try:
            # self.z.write(("VSET {} V").format(z_voltage))
        # except Exception as err:
            # print("Could not send z voltage | {}".format(err))

    def stop_field(self):
        """
        Kill all current to all power supplies.
        
        TODO: see if this is necessary
        """
        
        pass
        # print("field stopped)

    def get_requested_voltage(self):
        """
        Get the currently commanded voltages on the power supplies.
        
        TODO: Test
        """
        
        data = [None]*3
        
        # Query the setpoint voltages
        for i in range(0,3):
            try:
                command = "VSET?"
                data[i] = self.resource[i].query(command)
            except:
                "Could not get requested {} voltage, assumed to be zero | {}".format(
                    self.axis[i], err)
                data[i] = 0.0
                
        return data
        
        # try:
            # x_req = self.x.query("VSET?")
            # x_req = re.findall('\d+\.\d+', x_req)[0]
        # except Exception as err:
            # print(
                # "Could not get requested x voltage, assumed to be zero | {}".format(
                    # err))
            # x_req = 0
        # try:
            # y_req = self.y.query("VSET?")
            # y_req = re.findall('\d+\.\d+', y_req)[0]
        # except Exception as err:
            # print(
                # "Could not get requested y voltage, assumed to be zero | {}".format(
                    # err))
            # y_req = 0
            
        # try:
            # z_req = self.z.query("VSET?")
            # z_req = re.findall('\d+\.\d+', z_req)[0]
        # except Exception as err:
            # print(
                # "Could not get requested z voltage, assumed to be zero | {}".format(
                    # err))
            # z_req = 0
            
        # return (x_req, y_req, z_req)

    def get_power_data(self):
        """
        Get the actual measured voltage and current on the power
        supplies.
        
        TODO: Test
        """
        
        data = [None]*3
        
        for i in range(0,3):
            
            # Query the output voltages
            try:
                command = "VOUT?"
                data[i] = self.resource[i].query(command)
            except:
                "Could not get {} voltage, assumed to be zero | {}".format(
                    self.axis[i], err)
                data[i] = 0.0
                
            # Query the output currents
            try:
                command = "IOUT?"
                data[i+3] = self.resource[i].query(command)
            except:
                "Could not get {} current, assumed to be zero | {}".format(
                    self.axis[i], err)
                data[i+3] = 0.0
                
        return data
        
        # try:
            # x_out = self.x.query("VOUT?")
            # x_out = re.findall('\d+\.\d+', x_out)[0]
        # except Exception as err:
            # print(
                # "Could not get x voltage, assumed to be zero | {}".format(err))
            # x_out = 0
            
        # try:
            # y_out = self.y.query("VOUT?")
            # y_out = re.findall('\d+\.\d+', y_out)[0]
        # except Exception as err:
            # print(
                # "Could not get y voltage, assumed to be zero | {}".format(err))
            # y_out = 0
            
        # try:
            # z_out = self.z.query("VOUT?")
            # z_out = re.findall('\d+\.\d+', z_out)[0]
        # except Exception as err:
            # print(
                # "Could not get z voltage, assumed to be zero | {}".format(err))
            # z_out = 0
            
        # return (x_out, y_out, z_out)


if __name__ == "__main__":
    instruments = Instruments()
    rm.list_resources()
