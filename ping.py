#!/usr/bin/python
import subprocess
import threading
from utils import get_internal_ip


class RunMyCmd(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = subprocess.Popen(self.cmd)
        self.p.wait()

    def run_the_process(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()   #if your process needs a kill -9 to make
                                 #it go away, use self.p.kill() here instead.

            self.join()


ip = get_internal_ip()
ping_ip = ".".join(ip.split('.')[0:-1]) + '.1'
RunMyCmd(["ping", ping_ip], 5).run_the_process()
