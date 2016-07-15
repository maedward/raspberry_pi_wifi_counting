#!/bin/bash

#change tmp to ram disk for keeping read/write within ram
sudo mount -t tmpfs -o size=10M tmpfs /tmp/

#stop all previous setuped wifi monitor mode
sudo airmon-ng stop wlan1mon

#start the wifi monitor mode
sudo airmon-ng start wlan1

cd /app/raspberry_pi_wifi_counting/

#start passing scanned records to server
sudo python /app/raspberry_pi_wifi_counting/pulldata.py > /dev/null 2>&1 &

#keep checking the network available
(sleep 600; watch -n 120 python /app/raspberry_pi_wifi_counting/check_connection.py > /dev/null 2>&1) &

#start the wifi scanning and write it to tmp folder
sudo airodump-ng --cswitch 0 wlan1mon  --output-format csv --write /tmp/capture > /dev/null 2>&1

### The command below is for rc.local autostartup, since airodump-ng cannot run in background mode
# sudo screen airodump-ng --cswitch 0  wlan1mon --band bg --write /tmp/capture  > /dev/null 2>&1  &
