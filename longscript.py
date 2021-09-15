from datetime import datetime
import time
# datetime object containing current date and time
now = datetime.now()
 
for i in range(100):
    now = datetime.now()
    file = open('/home/dogukan/usb-port-listener/log.txt','a')
    file.write(str(now))
    file.write('\n')
    time.sleep(1)