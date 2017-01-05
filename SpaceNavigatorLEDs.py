# See http://stackoverflow.com/questions/29345325/raspberry-pyusb-gets-resource-busy#29347455
# Run python2 as root (sudo /usr/bin/python2.7 /home/pi/pythondev/SpaceNavigatorLEDs.py)

import usb.core
import usb.util
import sys
from time import gmtime, strftime
import time
import RPi.GPIO as GPIO

# Look for SpaceNavigator
dev = usb.core.find(idVendor=0x46d, idProduct=0xc626)
if dev is None:
    raise ValueError('SpaceNavigator not found');
else:
    print ('SpaceNavigator found')
    print dev

# Setup GPIO pins
TX_NEG_PIN = 11
TX_POS_PIN = 8
TY_NEG_PIN = 5
TY_POS_PIN = 7
TZ_NEG_PIN = 6
TZ_POS_PIN = 12
RX_NEG_PIN = 13
RX_POS_PIN = 16
RY_NEG_PIN = 19
RY_POS_PIN = 20
RZ_NEG_PIN = 26
RZ_POS_PIN = 21

GPIO.setmode(GPIO.BCM) # logical numbering

GPIO.setup(TX_NEG_PIN,GPIO.OUT)
GPIO.setup(TX_POS_PIN,GPIO.OUT)
GPIO.setup(TY_NEG_PIN,GPIO.OUT)
GPIO.setup(TY_POS_PIN,GPIO.OUT)
GPIO.setup(TZ_NEG_PIN,GPIO.OUT)
GPIO.setup(TZ_POS_PIN,GPIO.OUT)
GPIO.setup(RX_NEG_PIN,GPIO.OUT)
GPIO.setup(RX_POS_PIN,GPIO.OUT)
GPIO.setup(RY_NEG_PIN,GPIO.OUT)
GPIO.setup(RY_POS_PIN,GPIO.OUT)
GPIO.setup(RZ_NEG_PIN,GPIO.OUT)
GPIO.setup(RZ_POS_PIN,GPIO.OUT)

# Don't need all this but may want it for a full implementation

cfg = dev.get_active_configuration()
print 'cfg is ', cfg
intf = cfg[(0,0)]
print 'intf is ', intf
ep = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
print 'ep is ', ep

reattach = False
if dev.is_kernel_driver_active(0):
    reattach = True
    dev.detach_kernel_driver(0)

ep_in = dev[0][(0,0)][0]
ep_out = dev[0][(0,0)][1]

print ''
print 'Exit by pressing any button on the SpaceNavigator'
print ''

run = True
while run:
    try:
        data = dev.read(ep_in.bEndpointAddress, ep_in.bLength, 0)
        # raw data
        # print data

        # print it correctly T: x,y,z R: x,y,z
        if data[0] == 1:
            # translation packet
            tx = data[1] + (data[2]*256)
            ty = data[3] + (data[4]*256)
            tz = data[5] + (data[6]*256)
            
            if data[2] > 127:
                tx -= 65536
            if data[4] > 127:
                ty -= 65536
            if data[6] > 127:
                tz -= 65536
            print "T: ", tx, ty, tz

            # light up either -tive or +tive LED                
            if tx < 0:
                GPIO.output(TX_NEG_PIN, tx/2*2 == tx)
            if tx > 0:
                GPIO.output(TX_POS_PIN, tx/2*2 == tx)
            if tx == 0:
                GPIO.output(TX_NEG_PIN, GPIO.LOW)
                GPIO.output(TX_POS_PIN, GPIO.LOW)

            if ty < 0:
                GPIO.output(TY_NEG_PIN, ty/2*2 == ty)
            if ty > 0:
                GPIO.output(TY_POS_PIN, ty/2*2 == ty)
            if ty == 0:
                GPIO.output(TY_NEG_PIN, GPIO.LOW)
                GPIO.output(TY_POS_PIN, GPIO.LOW)
            
            if tz < 0:
                GPIO.output(TZ_NEG_PIN, tz/2*2 == tz)
            if tz > 0:
                GPIO.output(TZ_POS_PIN, tz/2*2 == tz)
            if tz == 0:
                GPIO.output(TZ_NEG_PIN, GPIO.LOW)
                GPIO.output(TZ_POS_PIN, GPIO.LOW)

        if data[0] == 2:
            # rotation packet
            rx = data[1] + (data[2]*256)
            ry = data[3] + (data[4]*256)
            rz = data[5] + (data[6]*256)
            
            if data[2] > 127:
                rx -= 65536
            if data[4] > 127:
                ry -= 65536
            if data[6] > 127:
                rz -= 65536
            print "R: ", rx, ry, rz
            
            # light up either -tive or +tive LED                
            if rx < 0:
                GPIO.output(RX_NEG_PIN, rx/2*2 == rx)
            if rx > 0:
                GPIO.output(RX_POS_PIN, rx/2*2 == rx)
            if rx == 0:
                GPIO.output(RX_NEG_PIN, GPIO.LOW)
                GPIO.output(RX_POS_PIN, GPIO.LOW)

            if ry < 0:
                GPIO.output(RY_NEG_PIN, ry/2*2 == ry)
            if ry > 0:
                GPIO.output(RY_POS_PIN, ry/2*2 == ry)
            if ry == 0:
                GPIO.output(RY_NEG_PIN, GPIO.LOW)
                GPIO.output(RY_POS_PIN, GPIO.LOW)
                
            if rz < 0:
                GPIO.output(RZ_NEG_PIN, rz/2*2 == rz)
            if rz > 0:
                GPIO.output(RZ_POS_PIN, rz/2*2 == rz)
            if rz == 0:
                GPIO.output(RZ_NEG_PIN, GPIO.LOW)
                GPIO.output(RZ_POS_PIN, GPIO.LOW)
             
        if data[0] == 3 and data[1] == 0:
            # button packet - exit on the release
            run = False

            
    except usb.core.USBError:
       print("USBError")
#    except:
#       print("read failed")
# end while

# Cleanup GPIO pins
GPIO.cleanup()

usb.util.dispose_resources(dev)

if reattach:
    dev.attach_kernel_driver(0)

