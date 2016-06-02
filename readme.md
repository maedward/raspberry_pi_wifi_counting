# Wifi for ppl counting (Raspberry Pi version)

## Prerequisite:
1. Aircrack-ng: http://www.aircrack-ng.org/

	The Python log parsing utility relies on the output from airodump-ng which is part of the Aircrack-ng package.

2. Grove-LCD RGB Backlight module

	If the module is missing, the Python log parsing utility should be modified to remove the related function calls. 



## Starting the program

`./startup [adhoc exclusion list building time]`

The startup script does the followings:

1. Enable monitoring mode for the wireless NIC
2. Start airodump-ng to scan WIFI signals and generate capture log at /tmp/
3. Start pulldata.py to parse the capture log and output results


## Stopping the program
Press Ctrl+C to stop. 

Airodump-ng should stop immediately. If the pulldata.py does not stop, you may need to kill the python process (using `killall python` or by `kill <PID of python>`)


## Limitation
Aircrack-ng currently supports 802.11a/b/g only. It cannot detect 802.11n only devices.
