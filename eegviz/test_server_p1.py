import simplejson as json
import requests
import time, sys, random

HOST_NAME = '172.31.35.47'

try:
    while(True):
        val1 = random.random()

        print str(val1)
        data = {"player1_val": val1}
        jsn = json.dumps(data)
        st = 'http://%s:8000/update_data?update=%s' % (HOST_NAME, jsn)
        requests.post(st)

        delay = random.randint(300, 2000)
        time.sleep(delay / 1000.0)
except KeyboardInterrupt:
    sys.exit()
