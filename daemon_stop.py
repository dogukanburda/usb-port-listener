import os
import sys
import time
from daemon import Daemon

class Agent(Daemon):
    def __init__(self,pidfile):
        super(Agent, self).__init__(pidfile,verbose = 0)
    def run(self):
        while True:
            time.sleep(1)



# Simply calls the Daemon class' stop function to kill the daemon process
agent = Agent('/home/ubuntu/daemon.pid')
agent.stop()