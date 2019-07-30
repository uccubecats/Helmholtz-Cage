# Helmholtz-Cage

## Status
Currenty, we are in the process of cleaning up and updating the code. Current todo's

 - Reorganize repository
 - Test calibration file
 - Add the ability to use relays to switch coil polarity
 - Test on Linux system (Ubuntu?)
 - Help documentation?

While this is happening, this repository may be broken. Commit a5349237229607aaa9d528a912eaa073b2b09c50 is the last one that for sure worked. We hope to have it up and running 

##Tips:

Use pycharm community edition on python 3.7+ for development

Can't connect to power supplies?
Download "Keysight Connection Expert" to see if the GPIB to USB connection is working
If it is: change python constants at the top to match the name of the connection in Keysight IO
If it is not: ensure the power supply is powered on before connecting USB. If that doesn't work, google away

Can't send enough voltage when hooked up to cage?
The power supplies have a max amperage setting. When powering on, hold down "DISPLAY SETTINGS" button and spin the dial at the bottom right of the cage until a reasonable max amperage is hit. 

Features within code not working?
The following were not extensively tested as most of this code was written before the cage was finished. Some features which I anticipate will need tested/tweaked:
- when creating a calibration file from a template file, everything works but the buttons do not reset allowing the user to continue using the GUI
- using calibration files to request specific magnetic fields while doing a "static test" has never been done yet 
- using a dynamic field csv has not been extensively developed, but should send a series of requested magnetic fields 

Package requirements should be easy to figure out when trying to run. If something can't be imported, install that package...
Likely need to use these:
pyserial==3.4
serial==0.0.41
PyVISA==1.8
numpy==1.12.0
matplotlib==2.0.0
