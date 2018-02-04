# Written by Jason Roll, contact: rolljn@mail.uc.edu, 513-939-9800
# Last modified: 180114
# *** denotes unfinished section

# --------------------------------------------------------------------------------
# PYTHON IMPORTS
import visa
import re


# visa.log_to_screen()
rm = visa.ResourceManager()


# --------------------------------------------------------------------------------
# CLASSES
class Instruments():
    def make_connections(self): # ***
        # figure out how to see which power supply is which
        self.x, self.y, self.z, self.mag = 4*["No connection"]
        self.cage_power = "ON"
        try:
            connected_devices = rm.list_resources()
        except Exception as err:
            print("Could not get resource manager resources | {}".format(err))
        for connection in connected_devices:
            # Power supplies can be remembered from computer's memory, must actually
            # send a 0 voltage to see if the connection was made
            if connection == "GPIB0::3::INSTR":
                self.x = rm.open_resource(connection)
                try:
                    self.x.write("VSET 0 V")
                except Exception as err:
                    print("No X Power Supply connection established to {} | {}".format(self.x, err))
                    self.x = "No connection"
            if connection == "GPIB0::4::INSTR":
                self.y = rm.open_resource(connection)
                try:
                    self.y.write("VSET 0 V")
                except Exception as err:
                    print("No Y Power Supply connection established to {} | {}".format(self.y, err))
                    self.y = "No connection"
            if connection == "GPIB0::5::INSTR":
                self.z = rm.open_resource(connection)
                try:
                    self.z.write("VSET 0 V")
                except Exception as err:
                    print("No Z Power Supply connection established to {} | {}".format(self.z, err))
                    self.z = "No connection"
            if connection == "name of magnetometer":
                self.mag = rm.open_resource(connection)

    def send_voltage(self, x_voltage, y_voltage, z_voltage): # ***

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
        
    def send_field(self, x_fields, y_fields, z_fields): # ***
        pass

    def stop_field(self): # ***
        # kill all current to all power supplies
        pass
        # print("field stopped)

    def get_field(self): # ***
        pass
    
    def get_requested_voltage(self):
        try:
            x_req = self.x.query("VSET?")
            x_req = re.findall('\d+\.\d+', x_req)[0]
        except Exception as err:
            print("Could not get requested x voltage, assumed to be zero | {}".format(err))
            x_req = 0
        try:
            y_req = self.y.query("VSET?")
            y_req = re.findall('\d+\.\d+', y_req)[0]
        except Exception as err:
            print("Could not get requested y voltage, assumed to be zero | {}".format(err))
            y_req = 0
        try:
            z_req = self.z.query("VSET?")
            z_req = re.findall('\d+\.\d+', z_req)[0]
        except Exception as err:
            print("Could not get requested z voltage, assumed to be zero | {}".format(err))
            z_req = 0
        return(x_req, y_req, z_req)

    def get_output_voltage(self):
        try:
            x_out = self.x.query("VOUT?")
            x_out = re.findall('\d+\.\d+', x_out)[0]
        except Exception as err:
            print("Could not get x voltage, assumed to be zero | {}".format(err))
            x_out = 0
        try:
            y_out = self.y.query("VOUT?")
            y_out = re.findall('\d+\.\d+', y_out)[0]
        except Exception as err:
            print("Could not get y voltage, assumed to be zero | {}".format(err))
            y_out = 0
        try:
            z_out = self.z.query("VOUT?")
            z_out = re.findall('\d+\.\d+', z_out)[0]
        except Exception as err:
            print("Could not get z voltage, assumed to be zero | {}".format(err))
            z_out = 0
        return(x_out, y_out, z_out)
        
class NameThis():
    def calibrate_cage():
        connected_devices = check_connections()
        # if magnetometer and all ps's are connected, continue...


if __name__ == "__main__":
    instruments = Instruments()
    instruments.make_connections()
    #print(instruments.x.write("VSET 70 MV"))
    #print(instruments.x.query("ERR?"))
    #print(power_supply.query("VSET?"))
