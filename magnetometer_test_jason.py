# my own magnetometer test code

# these packages are needed
import visa
import re

# this may need changed depending on how it shows up on your computer
magnetometer_connection_name = "ASRL5::INSTR"

# lists all instruments found by computer
rm = visa.ResourceManager()
print(rm.list_resources())

# match the name you're expecting to one of the found resources and create magnetometer object
if magnetometer_connection_name in rm.list_resources():
    print("magnetometer connection found")
    magnetometer = rm.open_resource(magnetometer_connection_name)
    

    # set the id to 00
    magnetometer.write("*99WE<cr>") # 99 is global address for all units, WE = write enable
    device_id = magnetometer.read("*99ID=") # read device id
    print(device_id)
	
	# start using commands found in the manual pg 8 (https://aerospace.honeywell.com/en/~/media/aerospace/files/datasheet/smartdigitalmagnetometerhmr2300_ds.pdf) below:
