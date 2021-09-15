#! /home/dogukan/miniconda3/bin/python3
import os
import sys
import time
from datetime import datetime
from pyudev import Context, Monitor, MonitorObserver
import subprocess
import signal
import os
process_pidfile = '/home/dogukan/popenpid.pid'
logfile = '/home/dogukan/devices.txt'

def handle_action(device):
        """ Method to call when handling device I/O events """
        # Possible errors: if daemon detects a 'remove' event before 'add' it will fail to get a pid number


        # Each usb action produces two add/remove and two bind/unbind events
        # Distinctive device properties are used to call the function once
        global process
        device_path = device.device_path.split('/')

        if device.action == 'add' and len(device_path)>6:
            # Logging usb events
            try:
                with open(logfile, 'a') as f:
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except:
                with open(logfile, 'w') as f:
                    f.write('action,sys_name,sys_number,device_path,datetime')
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            # Once the USB device is plugged in, call the script and run it as a background process
            process = subprocess.Popen(['/home/dogukan/miniconda3/bin/python3', '/home/dogukan/usb-port-listener/longscript.py'], stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
            # Get the process pid and write it to a file
            pid = process.pid
            with open(process_pidfile, 'w') as pf:
                pf.write(str(pid))


        elif device.action == 'remove' and len(device_path)>6:
            # Logging usb events
            try:
                with open(logfile, 'a') as f:
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except:
                with open(logfile, 'w') as f:
                    f.write('action,sys_name,sys_number,device_path,datetime')
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Terminate the process by its pid
            os.kill(process.pid, signal.SIGTERM) #or signal.SIGKILL
            time.sleep(1)
            # Retrieves the child process' state in order not to fall into zombie state 
            process.poll()
            #del process



context = Context()
monitor = Monitor.from_netlink(context)
# Filter devices except usb connections 
monitor.filter_by(subsystem='usb')

# MonitorObserver is the daemon process that calls handle_action() function when an event occurs
observer = MonitorObserver(monitor, callback=handle_action, name='monitor-observer')
# Start and join the thread
observer.start()
observer.join(1)
script_pid=os.getpid()
while True:
    print(str(script_pid))
    time.sleep(10)