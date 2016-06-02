#!/bin/bash

#sudo airmon-ng check kill

sudo airmon-ng stop mon0
sudo airmon-ng start wlan1
cd /app/raspberry_pi_wifi_counting/
sudo python /app/raspberry_pi_wifi_counting/pulldata.py $* &
sudo airodump-ng --cswitch 0 mon0  --output-format csv --write /tmp/capture
### The command below is for rc.local autostartup, since airodump-ng cannot run in background mode
# sudo screen airodump-ng --cswitch 0  wlan1mon --band bg --write /tmp/capture  > /dev/null 2>&1  &
