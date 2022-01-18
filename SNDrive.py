# SNDrive.py - SpaceNavigator output for two motors to drive a car.
#              Also sends PRM nonlinear output to LEDs
#
# See http://stackoverflow.com/questions/29345325/raspberry-pyusb-gets-resource-busy#29347455
# Run python3.4 as root (sudo -i ...)
# (requires python3 for pypubsub)
# python3 SNMotors.py

# This sample reads the 3D mouse and uses Pulse Width Modulation to light
# the LEDs relative to the magnitude of the half-axis value.
# It also outputs the same PWM signals to two motors connected to an L298
# H-bridge motor controller
#
# It is a bit more complex because threads need to be run for each axis to implement the PWM.
# The main loop reads the USB device and sends the data to the threads using pypubsub.
#aaa

import usb.core
import usb.util
import sys
from time import gmtime, strftime
import time
import RPi.GPIO as GPIO
import threading
from pubsub import pub

def NonLinear( val ):
   "Warp the incoming data to get more precision at the low end"
   val = val*(val*val)/(350*350)

   #comment this out if you want to implement a dead zone close to zero.
   #it helps to isolate user input
   if val > 0 and val < 1:
      val = 1
      
   return val

############################ Classes #######################################
class PWMThread(threading.Thread):
   # class variables
   updateRate = 100  # Hz
   period = 1 / updateRate
   axisRange = 350

   def __init__(self, pos, neg, event):
      self.posPin = pos
      self.negPin = neg
      self.axisVal = 0
      theThread = threading.Thread(target=self.PWMAxis)
      theThread.daemon = True
      theThread.start()
      
      pub.subscribe(self.setAxisValue, event)

   
   def setAxisValue(self, val):
      self.axisVal = val
      #print("The axis Val is now ", self.axisVal);
      return
   
   def PWMAxis(self):
      "PWM the LED on an axis"
      # Need fast cycle rates (>100Hz) to make the LEDs look like they are dimming
      while True:
         if self.axisVal < 0:
            pin = self.negPin
            val = -self.axisVal
            onTime = val/PWMThread.axisRange * PWMThread.period
            offTime = PWMThread.period - onTime
            GPIO.output(self.posPin, GPIO.LOW)
         elif self.axisVal > 0:
            pin = self.posPin
            val = self.axisVal
            onTime = val/PWMThread.axisRange * PWMThread.period
            offTime = PWMThread.period - onTime
            GPIO.output(self.negPin, GPIO.LOW)
         else:
            pin = 0
            GPIO.output(self.posPin, GPIO.LOW)
            GPIO.output(self.negPin, GPIO.LOW)
            time.sleep(.5)  # wait longer to let other threads run

         if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(onTime)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(offTime)

      return

######################## Main ##############################################


# Look for SpaceNavigator
dev = usb.core.find(idVendor=0x46d, idProduct=0xc626)
if dev is None:
    raise ValueError('SpaceNavigator not found');
else:
    print ('SpaceNavigator found')
    print (dev)

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

# pins to drive the motors left/right forward/backward
MOT_RIGHT_FWD_PIN =17
MOT_RIGHT_BCK_PIN = 27
MOT_LEFT_FWD_PIN = 22
MOT_LEFT_BCK_PIN = 18

GPIO.setmode(GPIO.BCM) # logical numbering (and BCM Motorsports)
GPIO.setwarnings(False);

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

GPIO.setup(MOT_RIGHT_FWD_PIN,GPIO.OUT)
GPIO.setup(MOT_RIGHT_BCK_PIN,GPIO.OUT)
GPIO.setup(MOT_LEFT_FWD_PIN,GPIO.OUT)
GPIO.setup(MOT_LEFT_BCK_PIN,GPIO.OUT)

# Don't need all this but may want it for a full implementation

cfg = dev.get_active_configuration()
print ('cfg is ', cfg)
intf = cfg[(0,0)]
print ('intf is ', intf)
ep = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
print ('ep is ', ep)

reattach = False
if dev.is_kernel_driver_active(0):
    reattach = True
    dev.detach_kernel_driver(0)

ep_in = dev[0][(0,0)][0]
ep_out = dev[0][(0,0)][1]

# Make threads for the 6 axes
txThread = PWMThread(pos=TX_POS_PIN, neg=TX_NEG_PIN, event='tx')
tyThread = PWMThread(pos=TY_POS_PIN, neg=TY_NEG_PIN, event='ty')
tzThread = PWMThread(pos=TZ_POS_PIN, neg=TZ_NEG_PIN, event='tz')
rxThread = PWMThread(pos=RX_POS_PIN, neg=RX_NEG_PIN, event='rx')
ryThread = PWMThread(pos=RY_POS_PIN, neg=RY_NEG_PIN, event='ry')
rzThread = PWMThread(pos=RZ_POS_PIN, neg=RZ_NEG_PIN, event='rz')

motRightThread = PWMThread(pos=MOT_RIGHT_FWD_PIN, neg=MOT_RIGHT_BCK_PIN, event='motRight')
motLeftThread = PWMThread(pos=MOT_LEFT_FWD_PIN, neg=MOT_LEFT_BCK_PIN, event='motLeft')

print ('')
print ('Exit by pressing any button on the SpaceNavigator')
print ('')

run = True
tx = 0
ty = 0
tz = 0
rx = 0
ry = 0
rz = 0
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
            print ("T: ", tx, ty, tz)
            tx = NonLinear(tx);
            ty = NonLinear(ty);
            tz = NonLinear(tz);
            pub.sendMessage('tx', val=tx)
            pub.sendMessage('ty', val=ty)
            pub.sendMessage('tz', val=tz)

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
            print ("R: ", rx, ry, rz)

            rx=NonLinear(rx)
            ry=NonLinear(ry)
            rz=NonLinear(rz)
            pub.sendMessage('rx', val=rx)
            pub.sendMessage('ry', val=ry)
            pub.sendMessage('rz', val=rz)
             
        if data[0] == 3 and data[1] == 0:
            # button packet - exit on the release
            run = False

        # -ty controls forward movement, +ty backwards
        # -rz turns right, rz turns left
        motRight = -ty - rz;
        motLeft = -ty + rz;
        if motRight > 350:
           motRight = 350;
        if motRight < -350:
           motRight = -350;
        if motLeft > 350:
           motLeft = 350;
        if motLeft < -350:
           motLeft = -350;
        pub.sendMessage('motRight', val=motRight);
        pub.sendMessage('motLeft', val=motLeft);
            
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

