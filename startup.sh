#!/bin/sh -e

#sudo airmon-ng check kill

sudo airmon-ng stop mon0
sudo airmon-ng start wlan1 > /dev/null 2>&1 &
sudo screen -d -m airodump-ng --cswitch 0  wlan1mon --band bg --write /tmp/capture  > /dev/null 2>&1  &
#sudo screen -AdmS airodump airodump-ng --output-format csv --write /tmp/capture mon0 > /dev/null 2>&1  &
sudo python /app/raspberry_pi_wifi_counting/pulldata.py $* &

#sudo airodump-ng --cswitch 0  mon0 --manufacturer --output-format csv --write /tmp/capture > /dev/null 2>&1
#sudo wpa_supplicant -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf &
#sudo dhcpcd wlan0
### The command below is for rc.local autostartup, since airodump-ng cannot run in background mode
# sudo screen airodump-ng --cswitch 0  wlan1mon --band bg --write /tmp/capture  > /dev/null 2>&1  &
