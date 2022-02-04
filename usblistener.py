#! /usr/bin/python3
import os
import sys
import time
from datetime import datetime
from pyudev import Context, Monitor, MonitorObserver
import subprocess
import signal
from cysystemd import journal
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    sasl_mechanism='SCRAM-SHA-256',
    security_protocol='SASL_SSL',
    sasl_plain_username='username',
    sasl_plain_password='passwd',
)
supported_models = ['1000', '6544']
process = None


def handle_action(device):
    """ Method to call when handling device I/O events """
    global process
    if device.action == 'add':
        # Logging usb events
        # device_vendor_id = int("0x" + device.get("ID_VENDOR_ID"), 16)
        # device_product_id = int("0x" + device.get("ID_MODEL_ID"), 16)
        if device.get('ID_VENDOR_ID') == '0930' and device.get('ID_MODEL_ID') in supported_models:
            pass

        journal.send(message="[ADD] Device action detected. Vendor ID : {}, Serial Number: {}".format(
            device.get('ID_VENDOR_FROM_DATABASE'), device.get('ID_SERIAL_SHORT')), priority=journal.Priority.INFO)
        producer.send(topic="logs", key=b"info", value=b"[ADD] Device action detected. Vendor ID : {}, Serial Number: {}".format(
            device.get('ID_VENDOR_FROM_DATABASE'), device.get('ID_SERIAL_SHORT')))
        journal.send(message="[ADD] Model ID : {}, Vendor Hex Number: {}".format(device.get(
            'ID_MODEL_ID'), device.get('ID_VENDOR_ID')), priority=journal.Priority.INFO)
        producer.send(topic="logs", key=b"info", value=b"[ADD] Model ID : {}, Vendor Hex Number: {}".format(device.get(
            'ID_MODEL_ID'), device.get('ID_VENDOR_ID')))
        # Once the USB device is plugged in, call the script and run it as a background process
        process = subprocess.Popen(['/usr/bin/python3', '/home/dogukan/usb-port-listener/opencv_cameracap.py'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        # Get the process pid and log to the journal
        journal.send(message="[INFO] A daemon process starting with PID: {}".format(str(
            process.pid)), priority=journal.Priority.INFO, PID=str(process.pid), PTYPE='SUB')
        producer.send(topic="logs", key=b"info", value=b"[INFO] A daemon process starting with PID: {}".format(str(
            process.pid)))

    elif device.action == 'remove':
        # Logging usb events
        journal.send(message="[REMOVE] Device action detected. Vendor ID : {}, Serial Number: {}".format(
            device.get('ID_VENDOR_FROM_DATABASE'), device.get('ID_SERIAL_SHORT'), priority=journal.Priority.INFO))
        # Terminate the process by its pid
        # The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored.
        os.kill(process.pid, signal.SIGTERM)
        time.sleep(1)
        # Retrieves the child process' state in order not to fall into zombie state
        # Once the subprocess is terminated, it needs to be poll'ed to be fully exited.
        process.poll()


context = Context()
monitor = Monitor.from_netlink(context)
# Filter devices except usb connections
monitor.filter_by(subsystem='usb', device_type='usb_device')
# MonitorObserver is the daemon process that calls handle_action() function when an event occurs
observer = MonitorObserver(
    monitor, callback=handle_action, name='monitor-observer')
# Start and join the thread
observer.start()
observer.join(1)
script_pid = os.getpid()
journal.send(message="[INFO] MAIN Script is started with pid: {}".format(
    script_pid), priority=journal.Priority.INFO, PID=str(script_pid), PTYPE='MAIN')
producer.send(topic="logs", key=b"info", value=b"[INFO] MAIN Script is started with pid: {}".format(
    script_pid))


def init_device_list():
    #context = Context()
    devices = []
    for udevice in context.list_devices(subsystem='usb'):
        usb_id = "Vendor: " + str(udevice.get('ID_VENDOR_FROM_DATABASE')) + " with id: " + str(
            udevice.get('ID_VENDOR_ID')) + " and serial number: " + str(udevice.get('ID_SERIAL_SHORT'))
        devices.append(usb_id)
    return devices


a_devices = init_device_list()
journal.send(message="[INFO] Current devices: {}".format(
    a_devices), priority=journal.Priority.INFO, PID=str(script_pid), PTYPE='MAIN')

while True:
    print(str(script_pid))
    time.sleep(100)
