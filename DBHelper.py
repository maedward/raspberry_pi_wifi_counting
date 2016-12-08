import sqlite3
import datetime
import requests
from config import DOMAIN
import utils



class DBHelper():
    def __init__(self):
        #init db
        #self.conn = sqlite3.connect(":memory:")
        self.conn = sqlite3.connect("sqlite")
        self.c = self.conn.cursor()
        self.minutesCount = 0
        self.checkPerMinutes = 5
        self.removeOldRecordsDays = 10

        #create table in db
        self.__createTable()

    def __createTable(self):
        try:
            self.c.execute("""CREATE TABLE wifi_data (
            id INTEGER PRIMARY KEY   AUTOINCREMENT,
            update_date DATE DEFAULT (datetime('now','localtime')),
            date DATE NOT NULL,
            this_mac TEXT NOT NULL,
            client_mac TEXT NOT NULL,
            signal INTEGER NOT NULL DEFAULT 0)""")
            self.conn.commit()
        except:
            print("The table is exist")

    def insertWifiData(self, data):
        #Testing data
        #data = [('2016-11-04 12:12:10', 'b8:27:eb:e3:c0:4c', 'B0:65:BD:F0:B1:1D', -31),
        #        ('2016-11-04 12:12:11', 'b8:27:eb:e3:c0:4c', 'B0:65:BD:F0:B1:1D', -31)]

        self.c.executemany("INSERT INTO wifi_data (date,this_mac,client_mac,signal) VALUES  (?,?,?,?)", data)
        self.conn.commit()


        #update minutesCount
        self.minutesCount += 1
        if self.minutesCount >= self.checkPerMinutes*2:
            self.checkDiff()
            self.minutesCount -= self.checkPerMinutes

    def checkDiff(self):
        print(">>CheckDiff")

        a_table = "select distinct client_mac from wifi_data where update_date > '%s' and update_date < '%s' and signal < -1" %\
                  ((datetime.datetime.now() - datetime.timedelta(minutes=self.checkPerMinutes*2)).strftime("%Y-%m-%d %H:%M:%S"),
                   (datetime.datetime.now() - datetime.timedelta(minutes=self.checkPerMinutes)).strftime("%Y-%m-%d %H:%M:%S"))
        print a_table
        self.c.execute(a_table)
        result = self.c.fetchall()
        print(">>Show A table")
        print(result)

        b_table = "select distinct client_mac from wifi_data where update_date > '%s' and update_date < '%s' and signal < -1" %\
          ((datetime.datetime.now() - datetime.timedelta(minutes=self.checkPerMinutes)).strftime("%Y-%m-%d %H:%M:%S"),
           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.c.execute(b_table)
        result = self.c.fetchall()
        print(">>Show B table")
        print(result)

        # #Test Case
        # a_table = "select * from wifi_data where id <=3"
        # print a_table
        # self.c.execute(a_table)
        # result = self.c.fetchall()
        # print(">>Show A table")
        # print(result)
        #
        # b_table = "select * from wifi_data where id >= 3"
        # self.c.execute(b_table)
        # result = self.c.fetchall()
        # print(">>Show B table")
        # print(result)

        out_sql = "select count(*) from (%s) a left join (%s) b on a.client_mac = b.client_mac where b.client_mac is null" % (a_table, b_table)
        self.c.execute(out_sql)
        result = self.c.fetchall()
        print(">>Show Out count")
        print(result[0][0])
        out_count = result[0][0]

        in_sql = "select count(*) from (%s) a left join (%s) b on a.client_mac = b.client_mac where b.client_mac is null" % (b_table, a_table)
        self.c.execute(in_sql)
        result = self.c.fetchall()
        print(">>Show In count")
        print(result[0][0])
        in_count = result[0][0]

        self.callApi(in_count, out_count)


    def send_raspberry_pi_att(self, device_id, in_data, out_data, datetime_str, domain=DOMAIN):
        url = "https://" + DOMAIN + "/api/save_entity_att/"
        payload = {"device_id": device_id, "in_data":in_data, "out_data":out_data, "create_time": datetime_str}
        print payload
        print url
        response = requests.post(url, data=payload, verify=False)
        return response.text

    def callApi(self, in_count, out_count):
        print(">>Call Api")

        #TODO:
        self.send_raspberry_pi_att(utils.get_mac(), in_count, out_count, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

        #remove the 10 day
        self.removeOldRecords()

    def removeOldRecords(self):
        out_sql = "DELETE FROM wifi_data WHERE update_date < '%s'" % (datetime.datetime.now() - datetime.timedelta(days=self.removeOldRecordsDays)).strftime("%Y-%m-%d %H:%M:%S")
        print out_sql
        self.c.execute(out_sql)
        self.c.fetchall()
