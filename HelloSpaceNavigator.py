# See http://stackoverflow.com/questions/29345325/raspberry-pyusb-gets-resource-busy#29347455
# Run python2 as root (sudo /usr/bin/python2.7 /home/pi/pythondev/HelloSpaceNavigator.py)
import usb.core
import usb.util
import sys
from time import gmtime, strftime
import time

# Look for SpaceNavigator
dev = usb.core.find(idVendor=0x256f, idProduct=0xc631)
if dev is None:
    raise ValueError('SpaceNavigator not found');
else:
    print('SpaceNavigator found')
    print(dev)


# Don't need all this but may want it for a full implementation

cfg = dev.get_active_configuration()
print('cfg is ', cfg)
intf = cfg[(0,0)]
print('intf is ', intf)
ep = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
print('ep is ', ep)

reattach = False
if dev.is_kernel_driver_active(0):
    reattach = True
    dev.detach_kernel_driver(0)

ep_in = dev[0][(0,0)][0]
ep_out = dev[0][(0,0)][1]

print('')
print('Exit by pressing any button on the SpaceNavigator')
print('')
#print(ep_in.bLength)

run = True
while run:
    try:
        data = dev.read(ep_in.bEndpointAddress, 13, 0)
        # raw data
        # print(data)

        # print it correctly T: x,y,z R: x,y,z
        if data[0] == 1:
            print('translation & rotation')
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
            # print("T: ", tx, ty, tz,)
            # if data[0] == 2:
            # print('rotation')
            # rotation packet
            rx = data[7] + (data[8]*256)
            ry = data[9] + (data[10]*256)
            rz = data[11] + (data[12]*256)
            if data[8] > 127:
                rx -= 65536
            if data[10] > 127:
                ry -= 65536
            if data[12] > 127:
                rz -= 65536
            print(" T: ",tx,ty,tz," R: ", rx, ry, rz)
        if data[0] == 3 and data[1] == 0:
            # button packet - exit on the release
            run = False

    except usb.core.USBError:
        print("USB error")
    except:
        print("read failed")
# end while
usb.util.dispose_resources(dev)

if reattach:
    dev.attach_kernel_driver(0)
