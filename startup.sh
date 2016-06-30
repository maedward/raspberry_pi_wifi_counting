#!/bin/bash

sudo mount -t tmpfs -o size=10M tmpfs /tmp/
#sudo airmon-ng check kill

sudo airmon-ng stop wlan1mon
sudo airmon-ng start wlan1
cd /app/raspberry_pi_wifi_counting/
sudo python /app/raspberry_pi_wifi_counting/pulldata.py > /dev/null 2>&1 &
watch -n 600 sh /app/raspberry_pi_wifi_counting/check_connection.sh &
sudo airodump-ng --cswitch 0 wlan1mon  --output-format csv --write /tmp/capture > /dev/null 2>&1
### The command below is for rc.local autostartup, since airodump-ng cannot run in background mode
# sudo screen airodump-ng --cswitch 0  wlan1mon --band bg --write /tmp/capture  > /dev/null 2>&1  &
