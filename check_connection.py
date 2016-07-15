import socket
import subprocess
from time import sleep
from utils import ping

REMOTE_SERVER = "www.google.com"
network_is_connected = False

def is_connected():
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(REMOTE_SERVER)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

for times in range(3):
    #ping network first
    ping()
    sleep(10)

    if is_connected():
        network_is_connected = True
        exit(0)

if not network_is_connected:
    print "Run restart script"
    cmd =r"sh /app/raspberry_pi_wifi_counting/check_connection.sh"
    subprocess.Popen(cmd, shell=True)
