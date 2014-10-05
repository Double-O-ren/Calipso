
import serial
import platform
import time
import zephyr
from zephyr.testing import simulation_workflow
import requests
import simplejson as json
from collections import deque

import biosigcorr


HOST_NAME = '172.31.32.38'
#HOST_NAME = '172.31.35.47'

heartLog = open("heartLog.txt", "w")

rri_buffer = deque()
winlen = 30 #number of RR intervals to calculate HRV over
        
# HRM data appears here.
def callback(value_name, value):
    """
    value_name can be:
        heartbeat_interval
        heartrate
        stride
        activity (speed?)
    """
    #print value_name, value
    if value_name == "heartbeat_interval":
        # print RR interval and timestamp
        data = {"heart": value}
        jsn = json.dumps(data)
        st = 'http://%s:8000/update_data?update=%s' % (HOST_NAME, jsn)
        requests.post(st)
        print "RR {0:1.4f} at {1}".format(value, time.time())
        heartLog.write("{0:1.4f} at {1}".format(value, time.time()))

        curtime = time.time()
        data = {"heart": value, "time":curtime}
        rri_buffer.append(data)
        if len(rri_buffer) > winlen:
            rri = [x['heart'] for x in rri_buffer]
            hrv = biosigcorr.getSDNN(rri, winlen, offset=1)[0]
            print "HRV {0:.2f} from {1} RRIs".format(hrv, len(rri_buffer))
            data = {"heart": hrv, "time":curtime}
            jsn = json.dumps(data)
            st = 'http://%s:8000/update_data?update=%s' % (HOST_NAME, jsn)
            requests.post(st)
            rri_buffer.popleft()

def main():
    zephyr.configure_root_logger()

    serial_port_dict = {"Darwin": "/dev/tty.HXM016473-BluetoothSeri",
                        "Windows": 23}

    serial_port = serial_port_dict[platform.system()]
    ser = serial.Serial(serial_port)

    simulation_workflow([callback], ser)

if __name__ == "__main__":
    main()
