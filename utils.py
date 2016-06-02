import netifaces
import requests
import json
import os
import datetime as dt


def get_mac():
    try:
        macaddr = netifaces.ifaddresses('wlan0')[netifaces.AF_LINK][0]['addr']
        return macaddr
    except IndexError, KeyError:
        pass
    return None


def get_internal_ip():
    try:
        addr = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
        return addr
    except IndexError, KeyError:
        pass
    return None


def get_info():
    JSON_FILE_NAME = 'info.json'
    last_modified_date = dt.datetime.fromtimestamp(
        os.path.getmtime(JSON_FILE_NAME) if os.path.isfile(JSON_FILE_NAME) else 0)
    if not os.path.isfile(JSON_FILE_NAME) or dt.datetime.now() < last_modified_date - dt.timedelta(hours=1):
        url = "http://ip-api.com/json/"
        response = requests.get(url)
        json_data = response.json()

        with open(JSON_FILE_NAME, 'w') as outfile:
            json.dump(json_data, outfile)
    else:
        with open(JSON_FILE_NAME) as json_file:
            json_data = json.load(json_file)

    return json_data


def get_location():
    json_data = get_info()
    return json_data['lat'], json_data['lon']


def get_external_ip():
    return get_info()['query']
