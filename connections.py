# Written by Jason Roll, contact: rolljn@mail.uc.edu, 513-939-9800
# Last modified: 180114
# *** denotes unfinished section

# ------------------------------------------------------------------------------
# PYTHON IMPORTS
import time
from threading import Thread
import visa
import re
import numpy as np
import serial
import logging
logger = logging.getLogger(__name__)

# visa.log_to_screen()
rm = visa.ResourceManager()

# ------------------------------------------------------------------------------
# FUNCTIONS


def convert_fields_to_voltages(x_field, y_field, z_field, data_object):
    '''
    Linearly interpolate between closest field values in calibration file to
    find a corresponding voltage

    :param x_field: float, requested x magnetic field
    :param y_field: float, requested y magnetic field
    :param z_field: float, requested z magnetic field
    :param data_object:
    :return:
    '''
    print("converting x,y,z field {} {} {} to voltages".format(x_field, y_field, z_field))

    closest_values = {'x': {'closest_fields': [None, None],
                            'closest_voltages': [None, None],
                            'errors': [np.inf, np.inf],
                            'interpolated_voltage': None,
                            'requested_field': float(x_field)},
                      'y': {'closest_fields': [None, None],
                            'closest_voltages': [None, None],
                            'errors' : [np.inf, np.inf],
                            'interpolated_voltage': None,
                            'requested_field': float(y_field)},
                      'z': {'closest_fields': [None, None],
                            'closest_voltages': [None, None],
                            'errors': [np.inf, np.inf],
                            'interpolated_voltage': None,
                            'requested_field': float(z_field)}}

    for plane, interp_data in closest_values.items():
        if plane == 'x':
            mag_field_vals = data_object.calibration_mag_field_x
            requested_field = float(x_field)
            calibration_voltages = data_object.calibration_voltages_x
        if plane == 'y':
            mag_field_vals = data_object.calibration_mag_field_y
            requested_field = float(y_field)
            calibration_voltages = data_object.calibration_voltages_y
        if plane == 'z':
            mag_field_vals = data_object.calibration_mag_field_Z
            requested_field = float(z_field)
            calibration_voltages = data_object.calibration_voltages_z

        # get the closest voltages and fields from the calibration data
        for index, measured_field in enumerate(mag_field_vals):
            print("temp, index: {}, measured_field: {}".format(index, measured_field))
            cal_field = float(measured_field)
            cal_voltage = calibration_voltages[index]
            print("temp: {} {}".format(cal_field, type(cal_field)))
            if abs(cal_field - requested_field) < interp_data['errors'][0]:
                interp_data['closest_voltages'][0] = cal_voltage
                interp_data['closest_fields'][0] = cal_field
                interp_data['errors'] = abs(cal_field - requested_field)

            elif abs(cal_field - requested_field) < interp_data['errors'][1]:
                interp_data['closest_voltages'][1] = cal_voltage
                interp_data['closest_fields'][1] = cal_field
                interp_data['errors'] = abs(cal_field - requested_field)

        # interpolate
        voltage_diff = (interp_data['closest_voltages'][0]
                        - interp_data['closest_voltages'][1])
        field_diff = (interp_data['closest_fields'][0]
                      - interp_data['closest_fields'][1])
        slope = voltage_diff/field_diff
        interp_data['interpolated_voltage'] = (
                interp_data['closest_voltages'][0] +
                ((interp_data['requested_field'] -
                  interp_data['closest_fields'][0])*slope))

        print("interpolation info for plane: {}".format(plane))
        print("requested field: {}".format(interp_data['requested_field']))
        print("closest calibration voltages: {}"
              .format(interp_data['closest_voltages']))
        print("closest calibration fields: {}"
              .format(interp_data['closest_fields']))
        print("interpolated voltage: {}"
              .format(interp_data['interpolated_voltage']))

    return(closest_values['x']['interpolated_voltage'],
           closest_values['y']['interpolated_voltage'],
           closest_values['z']['interpolated_voltage'])


# ------------------------------------------------------------------------------
# CLASSES
class ReadLine:
    """
    pyserial object wrapper for reading line
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


class Instruments:

    def __init__(self):
        # Note: Check these are correct for you
        self.x_id = "GPIB0::3::INSTR"
        self.y_id = "GPIB0::5::INSTR"
        self.z_id = "GPIB0::4::INSTR"
        self.x, self.y, self.z, self.mag = 4 * ["No connection"]
        self.log_data = "ON"
        self.connections_checked = True

    def make_connections(self):  # TODO: add support for other magnetometer

        try:
            connected_devices = rm.list_resources()
        except Exception as err:
            print("Could not get resource manager resources | {}".format(err))
        for connection in connected_devices:

            # Power supplies can be remembered from computer's memory,
            # must actually send a 0 voltage to see if the connection was made

            if connection == self.x_id:
                self.x = rm.open_resource(connection)
                try:
                    self.x.write("VSET 0 V")
                except Exception as err:
                    print(
                        "No X Power Supply connection established to {} | {}".format(
                            self.x, err))
                    self.x = "No connection"

            if connection == self.y_id:
                self.y = rm.open_resource(connection)
                try:
                    self.y.write("VSET 0 V")
                except Exception as err:
                    print(
                        "No Y Power Supply connection established to {} | {}".format(
                            self.y, err))
                    self.y = "No connection"

            if connection == self.z_id:
                self.z = rm.open_resource(connection)
                try:
                    self.z.write("VSET 0 V")
                except Exception as err:
                    print(
                        "No Z Power Supply connection established to {} | {}".format(
                            self.z, err))
                    self.z = "No connection"

        # connect the magnetometer using com5
        try:
            self.mag = serial.Serial('COM5', baudrate=9600, timeout=0.1,
                                     xonxoff=0, rtscts=0,
                                     interCharTimeout=None)
            #self.mag = ReadLine(self.mag2)
            # test data can be read from connection
            field_string = self.mag.readline().decode("utf-8")

            #Thread(target=self.read_magnetometer(), args=(self.mag,)).start()

        except Exception as err:
            print("No connection established to magnetometer | {}".format(err))
            self.mag = "No connection"

    def send_voltage(self, x_voltage, y_voltage, z_voltage):  # ***

        # send prescribed current to x,y,z power supply
        try:
            self.x.write(("VSET {} V").format(x_voltage))
        except Exception as err:
            print("Could not send x voltage | {}".format(err))
        try:
            self.y.write(("VSET {} V").format(y_voltage))
        except Exception as err:
            print("Could not send y voltage | {}".format(err))
        try:
            self.z.write(("VSET {} V").format(z_voltage))
        except Exception as err:
            print("Could not send z voltage | {}".format(err))

    def send_field(self, x_field, y_field, z_field, data_object):  # ***

        # convert x,y,z fields to voltages, then send the voltages
        x_voltage, y_voltage, z_voltage = convert_fields_to_voltages(x_field, y_field, z_field, data_object)
        self.send_voltage(x_voltage, y_voltage, z_voltage)
        data_object.active_x_voltage_requested = x_voltage
        data_object.active_y_voltage_requested = y_voltage
        data_object.active_z_voltage_requested = z_voltage

    def stop_field(self):  # TODO: see if this is necessary
        # kill all current to all power supplies
        pass
        # print("field stopped)

    def read_magnetometer(self):

        buffer_string = ''
        while True:
            thing = self.mag.read(self.mag.read(1024)).decode("utf-8")
            print("thing is: {}".format(thing))
            buffer_string = buffer_string + thing
            if '\n' in buffer_string:
                pass
            else:
                buffer_string += self.mag.read(1024).decode("utf-8")
                lines = buffer_string.split('\n')  # Guaranteed to have at least 2 entries
                self.mag.last_received = lines[-2]
                # If the Arduino sends lots of empty lines, you'll lose the
                # last filled line, so you could make the above statement conditional
                # like so: if lines[-2]: last_received = lines[-2]
                buffer_string = lines[-1]

    def get_magnetometer_field(self):
        valid_characters = ["0", "1", "2", "3", "4", "5",
                            "6", "7", "8", "9", ".", "-"]

        '''
        The below 5 lines need to remain as is, here's what's happening:
        
        the input buffer is all the lines of data written out from magnetometer, 
        this grows really fast
        
        It is reset, but this could happen in the middle of a line
        
        time.sleep allows the input buffer to populate with multiple 
        '''

        try:
            self.mag.reset_input_buffer()

            time.sleep(0.001)
            field_string = self.mag.readline().decode("utf-8")

            print("reading {} from magnetometer".format(field_string))

            x_string, y_string, z_string = "", "", ""
            currently_reading = None

            with open("temp_mag_field_raw.txt", "a") as f:
                f.write(field_string + "\n")
                print("read in field data")

            for character in field_string:

                # if currently reading for a float, add character if its valid
                if (currently_reading == "X") and (character in valid_characters):
                    x_string += character
                if (currently_reading == "Y") and (character in valid_characters):
                    y_string += character
                if (currently_reading == "Z") and (character in valid_characters):
                    z_string += character

                # see if its time to change what is being read
                if character == "X":
                    currently_reading = "X"
                elif character == "Y":
                    currently_reading = "Y"
                elif character == "Z":
                    currently_reading = "Z"

            # convert the string chunks to floats
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

            return x_field, y_field, z_field
        except AttributeError:
            return 999, 999, 999  # so that it is not confused with 0.0
            # can not reset magnetometer input buffer if not connected

    def get_requested_voltage(self):
        try:
            x_req = self.x.query("VSET?")
            x_req = re.findall('\d+\.\d+', x_req)[0]
        except Exception as err:
            print(
                "Could not get requested x voltage, assumed to be zero | {}".format(
                    err))
            x_req = 0
        try:
            y_req = self.y.query("VSET?")
            y_req = re.findall('\d+\.\d+', y_req)[0]
        except Exception as err:
            print(
                "Could not get requested y voltage, assumed to be zero | {}".format(
                    err))
            y_req = 0
        try:
            z_req = self.z.query("VSET?")
            z_req = re.findall('\d+\.\d+', z_req)[0]
        except Exception as err:
            print(
                "Could not get requested z voltage, assumed to be zero | {}".format(
                    err))
            z_req = 0
        return (x_req, y_req, z_req)

    def get_output_voltage(self):
        try:
            x_out = self.x.query("VOUT?")
            x_out = re.findall('\d+\.\d+', x_out)[0]
        except Exception as err:
            print(
                "Could not get x voltage, assumed to be zero | {}".format(err))
            x_out = 0
        try:
            y_out = self.y.query("VOUT?")
            y_out = re.findall('\d+\.\d+', y_out)[0]
        except Exception as err:
            print(
                "Could not get y voltage, assumed to be zero | {}".format(err))
            y_out = 0
        try:
            z_out = self.z.query("VOUT?")
            z_out = re.findall('\d+\.\d+', z_out)[0]
        except Exception as err:
            print(
                "Could not get z voltage, assumed to be zero | {}".format(err))
            z_out = 0
        return (x_out, y_out, z_out)

if __name__ == "__main__":
    instruments = Instruments()
    # instruments.make_connections()
    # print(instruments.x.write("VSET 70 MV"))
    # print(instruments.x.query("ERR?"))
    # print(power_supply.query("VSET?"))
    rm.list_resources()