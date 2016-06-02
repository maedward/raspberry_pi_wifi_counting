# A tool to display the eth0 IP to LCD. This helps identify the IP
# of the Raspberry Pi device at startup without connecting to the monitor.
#
# Extract the IP Address of thefirst network interface (should be eth0)
# then display to the LCD. 

import subprocess, StringIO

# Example for using the Grove I2C color LCD
from grove_rgb_lcd import *


def main():
    try:
        setRGB(0, 0, 0)
        cmd = "ifconfig | sed '2!d'"
        data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        f = StringIO.StringIO(data)
        if f.len != 0:
            setText(f.getvalue().strip().split(' ')[1])
            return ''
        else:
            setText('Unknown IP Address')
    except Exception, e:
        setText("Error:\n" + str(e))
        print "Exception - ", e
        return ''


main()
