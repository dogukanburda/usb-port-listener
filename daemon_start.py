import os
import sys
import time
from datetime import datetime
from pyudev import Context, Monitor, MonitorObserver
from daemon import Daemon
import subprocess
import signal
import os

process = None

class Agent(Daemon):
    def __init__(self,pidfile):
        super(Agent, self).__init__(pidfile,verbose = 0)
        self.process_pidfile = '/home/ubuntu/popenpid.pid'
        self.logfile = '/home/ubuntu/devices.txt'


    def handle_action(self,device):
        """ Method to call when handling device I/O events """
        # Possible errors: if daemon detects a 'remove' event before 'add' it will fail to get a pid number


        # Each usb action produces two add/remove and two bind/unbind events
        # Distinctive device properties are used to call the function once
        global process
        device_path = device.device_path.split('/')

        if device.action == 'add' and len(device_path)>11:
            # Logging usb events
            try:
                with open(self.logfile, 'a') as f:
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except:
                with open(self.logfile, 'w') as f:
                    f.write('action,sys_name,sys_number,device_path,datetime')
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            # Once the USB device is plugged in, call the script and run it as a background process
            process = subprocess.Popen(['/usr/bin/python3', '/home/ubuntu/python-daemon/opencv_samplescript.py'], stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
            # Get the process pid and write it to a file
            pid = process.pid
            with open(self.process_pidfile, 'w') as pf:
                pf.write(str(pid))


        elif device.action == 'remove' and len(device_path)>11:
            # Logging usb events
            try:
                with open(self.logfile, 'a') as f:
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except:
                with open(self.logfile, 'w') as f:
                    f.write('action,sys_name,sys_number,device_path,datetime')
                    f.write('{0.action},{0.sys_name},{0.sys_number},{0.device_path},'.format(device))
                    f.write(' {} \n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Terminate the process by its pid
            os.kill(process.pid, signal.SIGTERM) #or signal.SIGKILL
            time.sleep(1)
            # Retrieves the child process' state in order not to fall into zombie state 
            process.poll()
            #del process


    def run(self):
        time.sleep(0.3)
        context = Context()
        monitor = Monitor.from_netlink(context)
        # Filter devices except usb connections 
        monitor.filter_by(subsystem='usb')

        # MonitorObserver is the daemon process that calls handle_action() function when an event occurs
        observer = MonitorObserver(monitor, callback=self.handle_action, name='monitor-observer')
        # Start and join the thread
        observer.start()
        observer.join(1)
        while True:
            time.sleep(1)


# Initialize the deamon agent
agent = Agent('/home/ubuntu/daemon.pid')
# Restart it in case its already running.
agent.restart()