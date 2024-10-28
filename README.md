# Helmholtz-Cage

This is the repository for the UC Helmholtz Cage project. The designed cage is capable of generating a uniform +/- 1.5 Gauss magnetic field along 3-axes, in a volume large enough to fit a 3U CubeSat (30cm x 30cm x 30cm). The cage is controlled by a GUI-based Python program, which can manage instrument connections, calibrate the cage (```WIP```), and run both single-value tests and time-varying replications of orbital magnetic fields (```WIP```). Additionally, the design includes both a static test stand for simple tests, and an air-bearing table (```WIP```) for more dynamic testing of CubeSat Attitude Determination and Control Systems (ADCS) on hardware.

This design is meant to be somewhat modular, particularly with respect to hardware selection; The UC CubeCats implementation uses three [HP6038A DC Power Supplies](https://www.keysight.com/us/en/product/6038A/system-autoranging-dc-power-supply-60v-10a.html), (with each powering one axis pair) and a [MLX90939 magnetometer](https://www.melexis.com/en/product/MLX90393/Triaxis-Micropower-Magnetometer).

## Status
This project is currently a WIP. The most recent version (0.2) has basic functionality, allowing manual control of the Cage via the GUI control panel and data logging. Currently, some high-priority "todo" items include:

 - ~~Get control software "up-and-running" on Linux (currently targeting Ubuntu)~~ (Complete!)
 - Design new magnetometer housing
 - Implement calibration functions
 - Add support for relay switches to reverse coil polarity
 - Add ability to run "dynamic" tests
 - Upload hardware CAD files and design documents
 - Add instructions and help documentations

## Requirements
This software was developed and tested in:

 - Ubuntu 22.04 LTS
 - Python 3.8

The following Python packages need to be installed:

 - matplotlib
 - numpy
 - PIL
 - scipy

For the specific hardware used in the UC CubeCats implementation, the following Python packages and other software are also required:

 - pyserial
 - pyvisa
 - A VISA interface library

If you are using different hardware, you may need other packages or software to make them work.

## Installation

To install this program, first install all required dependencies listed above. Then clone the repository in the location of your choosing

## Instructions

To launch the control software, open a terminal and go to the main directory of the ```Helmholtz-Cage``` program. Then launch the GUI via the command:

```
./launch_gui.sh
```

Once the GUI has launched, connect the device to all instruments using the ```Check Connections``` button. Select ```Static Test```, and then the ```Enter Voltage``` command option (```Enter Field``` command option is not yet implemented). Finally, select whether to log the test run's data or not (using the ```Log Data``` checkbox).

If all devices are connected, click the ```Start Cage``` data to begin a test run. While the cage is running you can enter desired voltage values into the voltage commmand entries for each axis and click ```Command Values``` to change the voltage for each axis. When you are finished with the current test run, click ```Stop Cage``` to end the run and log the data (if that option was selected).

## Notes
 - When creating a calibration file from a template file, everything works but the buttons do not reset, allowing the user to continue using the GUI (This should not happen).

## Licensing
This program is licensed under the MIT license, as presented in the LICENSE file

Program is Copyright (c) UC Cubecats

