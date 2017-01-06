# 3d-mouse-rpi-python
This project shows simple ways to access a 3D mouse on a Raspberry Pi.  

The samples are written in python.  They rely on some standard imports.
Unless otherwise mentioned, they have been developed on a RPi 3.

HelloSpaceNavigator.py - opens a SpaceNavigator and prints the data to stdout

SpaceNavigatorTxLEDs.py - reads a SN and lights up LEDs based on the data of the tx axis.  One LED for positive; one for negative direction.,

SpaceNavigatorLEDs.py - reads a SN and lights up LEDs connected to every axis.  12 LEDs (and resistors) connected to 12 pins.  One for each positive and one for each negative half-axis.  Shows which half-axis is active.  Doesn't show the relative value of that axis.  Just on/off when abs(val) is != 0.
