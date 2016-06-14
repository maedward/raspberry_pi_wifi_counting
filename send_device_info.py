from utils import *
from config import *
import urllib2, json


#post data to server
def post_device_info(data):
    url = ADD_DEVICE_INFO_API
    json_data = json.dumps(data)
    req = urllib2.Request(url, json_data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()

    print response


def create_device_info():
    device_info = {}
    device_info['internal_ip'] = get_internal_ip()
    device_info['external_ip'] = get_external_ip()
    device_info['mac'] = get_mac()
    device_info['router_mac'] = get_router_mac()
    device_info['lat'], device_info['lon'] = get_location()
    device_info['city'] = get_info()['city']
    device_info['country'] = get_info()['country']
    device_info['isp'] = get_info()['isp']
    device_info['version'] = VERSION

    print device_info
    return device_info


def send_device_info():
    post_device_info(create_device_info())