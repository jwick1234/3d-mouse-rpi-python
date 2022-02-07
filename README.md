# 3d-mouse-rpi-python
This project shows simple ways to access a 3D mouse on a Raspberry Pi.  

The samples are written in python.  They rely on some standard imports.
Unless otherwise mentioned, they have been developed on a RPi 3.

HelloSpaceNavigator.py - opens a SpaceNavigator and prints the data to stdout

### wildanxgifari modified the file for Space Mouse Pro

SpaceNavigatorTxLEDs.py - reads a SN and lights up LEDs based on the data of the tx axis.  One LED for positive; one for negative direction.,

SpaceNavigatorLEDs.py - reads a SN and lights up LEDs connected to every axis.  12 LEDs (and resistors) connected to 12 pins.  One for each positive and one for each negative half-axis.  Shows which half-axis is active.  Doesn't show the relative value of that axis.  Just on/off when abs(val) is != 0.

SNLEDsPWM.py - reads the SN and lights up LEDs with an intensity proportional to the magnitude of the half-axis.  It uses PWM (Pulse Width Modulation). That is, it turns the LED on/off really fast to achieve the dimming. This is a good start for any type of motor controller.  The frequence can be set.  By default it is 100Hz.   This requries python3.4 because of the mechanism used to communicate with the PWM threads.

SNLEDsPWMnl.py - same as SNLEDsPWM.py but uses a non-linear (squared) warping on the data to add more precision at the low end.
The eye doesn't respond linearly to input.  This makes the LEDs look more responsive.  It is also probably more useful for motor control.

SNDrive.py - SN drives a small tracked Pololu Zumo tank kit.  Two micromotors on the front wheels.  Ty goes forward/backwards.  Rz turns it.  Using the non-linear data it gives quite good user control.  With encoders on the motors, and a feedback loop, I could have exceptional control.
