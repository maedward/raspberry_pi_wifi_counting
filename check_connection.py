import socket
import subprocess

REMOTE_SERVER = "www.google.com"
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

if is_connected():
    print "The connection is health"
else:
    print "Run restart script"
    cmd =r"sh /app/raspberry_pi_wifi_counting/check_connection.sh"
    subprocess.Popen(cmd, shell=True)
