# Helmholtz-Cage

## Summary
This is the repository for the UC Helmholtz Cage project. The designed cage is capable of generating a uniform +/- 1.5 Gauss magnetic field along 3-axes, in a volume large enough to fit a 3U CubeSat (30cm x 30cm x 30cm). The cage is controlled by a GUI-based Python program, which can manage instrument connections (working), calibrate the cage (still being tested), and run both single-value tests (working) and time-varying replications of orbital magnetic fields (still being tested). Additionally, the design includes both a static test stand for simple tests, and an air-bearing table for more dynamic testing of CubeSat Attitude Determination and Control Systems (ADCS) on hardware.

This project is currently a WIP. We are currently in the progress of getting the software up and running on Linux.  While this is happening, the most recent commits are likely broken. The "[Initial Function](https://github.com/uccubecats/Helmholtz-Cage/releases/tag/v0.9)" release is the last "working" (albeit disorganized) version, which implimented basic cage functionality under Windows 10.

## Requirements
This software was developed and tested in:

 - Ubuntu 22.04 LTS
 - ROS Noetic
 - Python 3.8

The following python packages need to be installed:

 - scipy
 - pyserial
 - pyvisa
 - pyvisa-py
 - matplotlib
 - PIL

Additionally the following items must be installed:

 - python3-tk
 - python3-pil.image

## Status
High priority "todo" items: 
 - Get control software up-and-running on Linux (currently targeting Ubuntu)
 - Upload hardware CAD files and design documents
 - Add instructions and help documentations.
 - Test "dynamic" runs of the cage
 - Add support for relay switches to reverse coil polarity
 - Test calibration

## Instructions:
Coming Soon

## Notes:
 - When creating a calibration file from a template file, everything works but the buttons do not reset, allowing the user to continue using the GUI (This should not happen).

## License
This program is licensed under the MIT license, as presented in the LICENSE file

Program is Copyright (c) UC Cubecats
