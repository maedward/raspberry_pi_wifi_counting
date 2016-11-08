###
# This script is to be used in junction with airodump-ng,
# which produces a WIFI signal scanning log for processing:
# http://www.aircrack-ng.org/doku.php?id=airodump-ng
###
import sys, time
import datetime
from time import sleep
from send_device_info import *
import utils
from config import *

from DBHelper import DBHelper

dbhelper = DBHelper()

# Configurations

#GA ID
GA_ID = "UA-75128946-1"

# Apply the external exclusion list (exclusion.txt)
use_exclusion = True
exclusion_list_filename = "exclusion.txt"

# Tune the signal strength to control the area of devices we want to monitor:
# -30 dBm: Max achievable signal strength
# -67 dBm: Min signal strength for VoIP/streaming video
# -70 dBm: Min signal strength for reliable packet delivery
# -80 dBm: Min signal strength for basic connectivity (may be unreliable)
# -90 dBm: Approaching or drowning in the noise floor.
# typical: -60
signal_strength_threshold = -30

# devices have no WIFI data tranmission (in minutes) will be ignored
idle_threshold = 1

# scanning interval when no discovered device, in seconds
no_device_update_interval = 60

# scanning interval when at least one device is discovered, in seconds
regular_update_interval = 60

# Adhoc exclusion list building time, in minutes. 0 = disable
adhoc_exclusionlist_building_time = 1

# predefined devices for demo. This will override all exclusion lists.
known_devices_list = [['C4:9A:02:84:FC:41', 'Ryan'],
                      ['6C:C2:6B:59:71:53', 'Snow'],
                      ['60:FE:C5:B2:24:4A', 'Wolv'],
                      ['1C:AB:A7:A9:F8:6F', 'Spid'],
                      ['5C:AD:CF:13:F5:9C', 'Arie'],
                      ['8C:2D:AA:87:37:A5', 'Blue']
                      ]


# No configurable items below this line.
scanner_start_time = datetime.datetime.now()
adhoc_exclusionlist = []


# Convert known MAC address into a meaningful name
def mac_lookup(macaddr):
    for device in known_devices_list:
        if macaddr in device:
            return (device)[1]

    return macaddr.replace(":", "")


def is_known_device(macaddr):
    for device in known_devices_list:
        if macaddr in device:
            return True
    return False


def hitGA(last_seen, mac_address, ap_mac, ap_name):
    #print("sent to GA")
    label = last_seen.replace(" ", "") + "||" + mac_address

    if ap_mac != None:
        label += "||" + ap_mac.replace(" ", "")

    if ap_name != None and ap_name != "":
        label += "||" + ap_name.replace(" ", "_")

    urllib2.urlopen("http://www.google-analytics.com/collect?v=1&tid=%s&cid=%s&t=event&ec=Movement&ea=Office&el=%s" % (GA_ID, mac_address, label)).close


#post data to server
def post_wifi_data(data):
    #check wifi connection
    ping()
    sleep(10)

    #Send the detected wifi to server
    url = ADD_WIFI_DATA_API
    json_data = json.dumps(data)
    req = urllib2.Request(url, json_data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()

    #send device info to server
    send_device_info()

    print response


def create_wifi_data(last_seen, mac_address, ap_mac, ap_name, power):
    class DatetimeEncoder(json.JSONEncoder):
         def default(self, obj):
             if isinstance(obj, datetime):
                 return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
             elif isinstance(obj, date):
                 return obj.strftime('%Y-%m-%d')
             # Let the base class default method raise the TypeError
             return json.JSONEncoder.default(self, obj)

    wifi_data = {}
    last_seen_formated = datetime.datetime.strptime(last_seen, " %Y-%m-%d %H:%M:%S")
    wifi_data['last_seen_time'] = last_seen_formated.isoformat()
    wifi_data['category'] = 'Motherapp_office'
    wifi_data['action'] = 'Check_point'
    wifi_data['label'] = ''
    wifi_data['location_name'] = utils.get_mac()
    wifi_data['device_mac'] = mac_address
    wifi_data['power'] = power
    wifi_data['router_mac'] = ap_mac
    wifi_data['router_name'] = ap_name

    print wifi_data
    return wifi_data


def fetch_data():
    # Refresh exclusion list
    exclusionlist = []
    if use_exclusion == True:
        try:
            infile = open(exclusion_list_filename, "rb")
            reader = csv.reader(infile)

            for row in reader:
                exclusionlist.append(row[0])

        except Exception, e:
            print "error parsing exclusion list: ", e

    else:
        exclusionlist = []

    # Check if we are still building the adhoc exclusion list
    if (adhoc_exclusionlist_building_time > 0) and (datetime.datetime.now() - scanner_start_time) < datetime.timedelta(
            minutes=adhoc_exclusionlist_building_time):
        print "*** Building Adhoc exclusion list (%s minutes) ***" % adhoc_exclusionlist_building_time
        building_adhoc_list = True

    else:
        building_adhoc_list = False

    # get the newest capture.csv file, then use awk to extra wifi client list (no APs)
    try:
        cmd = r"cat `ls -Art /tmp/capture*.csv | grep -v kismet | tail -n 1` | awk '/Station/{y=1;next}y'"
        data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        f = StringIO.StringIO(data)

        # If the log is not ready, nothing we can do
        if f.len == 0:
            return 0

        # convert the data to a list of dict() objects
        conv = lambda row: {'station_mac': row[0],
                            'first_time_seen': row[1],
                            'last_time_seen': row[2],
                            'power': row[3],
                            'ap_mac': row[5],
                            'ap_name': row[6]}
        data = [row for row in csv.reader(f, delimiter=',') if len(row) != 0]
        rawstationlist = [conv(row) for row in data]

        iosmaclist = []
        devicelist = []

        wifi_data_list = []
        wifi_data_list_for_sqlite = []

        # filtering
        for row in rawstationlist:
            last_seen = row['last_time_seen']
            current_mac = row['station_mac']
            ap_mac = row['ap_mac']
            ap_name = row['ap_name']
            power = row['power']

            # Filter out idle devices
            lastseen = datetime.datetime.strptime(row['last_time_seen'], " %Y-%m-%d %H:%M:%S")
            elapsed = datetime.datetime.now() - lastseen
            if elapsed >= datetime.timedelta(minutes=idle_threshold):
                # Device idled too long, we do not count it
                continue

            #send to GA
            #hitGA(last_seen,current_mac, ap_mac, ap_name)

            #bulk post data
            wifi_data_list.append(create_wifi_data(last_seen, current_mac, ap_mac, ap_name, power))
            last_seen_formated = datetime.datetime.strptime(last_seen, " %Y-%m-%d %H:%M:%S")
            wifi_data_list_for_sqlite.append((last_seen_formated, ap_mac, current_mac, power))

            if current_mac in exclusionlist and not is_known_device(current_mac):
                # print "filtered: in exclusion list - ", current_mac
                continue

            if current_mac in adhoc_exclusionlist:
                continue

            try:
                if int(row['power']) < signal_strength_threshold:
                    # Device has a weak signal, we do not count it
                    continue

            except ValueError:
                continue

            # Extract iOS Randomized MAC devices to a seperate list
            # http://blog.mojonetworks.com/ios8-mac-randomization-analyzed/
            iosmacidentifier = current_mac[1]
            if iosmacidentifier in ['2', '6', 'A', 'E']:
                iosmaclist.append(current_mac)

                if building_adhoc_list:
                    adhoc_exclusionlist.append(current_mac)

                continue

            # No more rules to proceed. Add to the discovered device list
            if building_adhoc_list and not is_known_device(current_mac):
                adhoc_exclusionlist.append(current_mac)
            devicelist.append(current_mac)

        #Post bulk data to server
        post_wifi_data(wifi_data_list)
        dbhelper.insertWifiData(wifi_data_list_for_sqlite)


        # Display device list to console
        lcd_device_list = ""

        print "Devices in range:"
        if len(devicelist) > 0:
            for row in devicelist:
                addr = mac_lookup(row)
                print "... ", addr
                lcd_device_list += addr[-4:] + " "

        else:
            print "(none)"

        if len(iosmaclist) > 0:
            print "\niOS devices with randomized MAC in range:"
            for row in iosmaclist:
                addr = mac_lookup(row)
                print "... ", addr
                lcd_device_list += addr[-4:] + " "

        return len(devicelist)

    except IndexError:
        # Sometimes airodump-ng produces corrupted log file
        # We can simply empty the file, it will regenerate during the next channel scan
        print "IndexError - Reseting log file"

        cmd = r"echo '' > `ls -Art /tmp/capture*.csv | grep -v kismet | tail -n 1`"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        return 0

    except Exception, e:
        print "Exception - ", e
        return 0


def main():
    global adhoc_exclusionlist_building_time

    # Option: set adhoc exclusion list building time
    if len(sys.argv) == 2:
        try:
            adhoc_exclusionlist_building_time = int(sys.argv[1])

        except Exception, e:
            print "Invalid adhoc exclusion list building time. Using default %s minutes" % adhoc_exclusionlist_building_time

    while True:
        print '-' * 50
        print time.strftime('%d %b %Y %l:%M:%S%p %Z')

        detected_device_count = fetch_data()

        # No device is detected, we monitor the log file more frequently
        if detected_device_count == 0:
            sleep(no_device_update_interval)

        else:
            sleep(regular_update_interval)


main()
