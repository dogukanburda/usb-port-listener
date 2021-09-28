#! /usr/bin/python3
import os
import sys
import time
from datetime import datetime
from pyudev import Context, Monitor, MonitorObserver
import subprocess
import signal
from cysystemd import journal


process = None
def handle_action(device):
        """ Method to call when handling device I/O events """
        global process
        if device.action == 'add':
            # Logging usb events
            journal.send(message="[ADD] Device action detected. Vendor ID : {}, Serial Number: {}".format(device.get('ID_VENDOR_FROM_DATABASE'),device.get('ID_SERIAL_SHORT')),priority=journal.Priority.INFO)
            # Once the USB device is plugged in, call the script and run it as a background process
            process = subprocess.Popen(['/usr/bin/python3', '/home/dogukan/usb-port-listener/opencv_cameracap.py'], stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
            # Get the process pid and log to the journal         
            journal.send(message="[INFO] A daemon process starting with PID: {}".format(str(process.pid)),priority=journal.Priority.INFO, PID=str(process.pid), PTYPE='SUB')

        elif device.action == 'remove':
            # Logging usb events
            journal.send(message="[REMOVE] Device action detected. Vendor ID : {}, Serial Number: {}".format(device.get('ID_VENDOR_FROM_DATABASE'),device.get('ID_SERIAL_SHORT'),priority=journal.Priority.INFO))
            # Terminate the process by its pid
            os.kill(process.pid, signal.SIGTERM) #or signal.SIGKILL
            time.sleep(1)
            # Retrieves the child process' state in order not to fall into zombie state 
            process.poll()

context = Context()
monitor = Monitor.from_netlink(context)
# Filter devices except usb connections 
monitor.filter_by(subsystem='usb',device_type='usb_device')
# MonitorObserver is the daemon process that calls handle_action() function when an event occurs
observer = MonitorObserver(monitor, callback=handle_action, name='monitor-observer')
# Start and join the thread
observer.start()
observer.join(1)
script_pid=os.getpid()
journal.send(message="[INFO] MAIN Script is started with pid: {}".format(script_pid),priority=journal.Priority.INFO, PID=str(script_pid), PTYPE='MAIN')

def init_device_list():
    #context = Context()
    devices = []
    for udevice in context.list_devices(subsystem='usb'):
        usb_id = "Vendor: " + str(udevice.get('ID_VENDOR_FROM_DATABASE')) + " with id: " + str(udevice.get('ID_VENDOR_ID')) +" and serial number: " + str(udevice.get('ID_SERIAL_SHORT'))
        devices.append(usb_id)
    return devices

a_devices = init_device_list()
journal.send(message="[INFO] Current devices: {}".format(a_devices),priority=journal.Priority.INFO, PID=str(script_pid), PTYPE='MAIN')

while True:
    print(str(script_pid))
    time.sleep(100)