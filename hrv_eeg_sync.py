# -*- coding: utf-8 -*-
"""
Created on Sun Oct 05 10:04:31 2014

@author: mpesavento
"""

import serial
import platform
import time
import zephyr
from zephyr.testing import simulation_workflow
import requests
import simplejson as json
from collections import deque

import threading
import numpy as np
from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

import biosigcorr


HOST_NAME = '172.31.32.38'

rri_buffer = deque()
hrv_buffer = deque()
winlen = 30 #number of RR intervals to calculate HRV over

eegpower_buffer = deque()
lock = threading.Lock() #create global lock on queue

def ecgcallback(value_name, value):
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
        curtime = time.time()
        data = {"heart": value, "time":curtime}
        rri_buffer.append(data)
        print "RR {0:1.4f} at {1}".format(value, curtime)
        if len(rri_buffer) > winlen:
            rri = [x['heart'] for x in rri_buffer]
            hrv = biosigcorr.getSDNN(rri, winlen, offset=1)[0]
            print "HRV {0:.2f} from {1} RRIs".format(hrv, len(rri_buffer))
            hrv_buffer.append( {"hrv": hrv, "time":curtime} )
            #jsn = json.dumps(data)
            #st = 'http://%s:8000/update_data?update=%s' % (HOST_NAME, jsn)
            #requests.post(st)
            rri_buffer.popleft()
            
class RunMWM(threading.Thread):
    def __init__(self):
        #self._target = target
        #self._args = args
        self.isRunning = True
        threading.Thread.__init__(self)
        self._eegpower = deque()
        self.mindwaveDataPointReader=None

    #def run(self):
    #    self._target(*self._args)

    def connectMWM(self, target_address):
        """
        make the MWM connection
        """
        print "Connecting to MWM...",
        try:
            self.mindwaveDataPointReader = MindwaveDataPointReader(target_address)
            self.mindwaveDataPointReader.start() # connect to the mindwave mobile headset
        except IOError as e:
            print e
            print "Couldn't connect to MWM device. Check address? Is it turned on?";
            raise e
        
        print " connected"
    

    def run(self):
        """
        run a while loop to capture data and push it into a queue
        """
        while(self.isRunning):
            dataPoint = self.mindwaveDataPointReader.readNextDataPoint()
            if dataPoint.__class__ is PoorSignalLevelDataPoint:
                count=0
                if not dataPoint.headSetHasContactToSkin():
                    #chek the first one, and if no contact, loop until dies
                    count+=1
                    dataPoint = mindwaveDataPointReader.readNextDataPoint()
                    print "waiting for signal quality"
                    while(not dataPoint.headSetHasContactToSkin() or count>10000):
                        count+=1
                        dataPoint = self.mindwaveDataPointReader.readNextDataPoint()
                    if count>10000:
                        print "No contact, quitting"
                        raise ValueError("no EEG contact")
                    else:
                        print "Contact detected"
            elif (dataPoint.__class__ is EEGPowersDataPoint):
                eegpower = np.log(dataPoint.asList()) / np.log(float(dataPoint.maxint))
                data = {'brain':eegpower, 'timestamp': time.time()}
                with lock:
                    eegpower_buffer.append(data) #append to global queue
                print "alphaH {0} --> {1:1.4f} at {2}".format(dataPoint.highAlpha, data['brain'][3], data['timestamp'])
                print "\n"
                
        mindwaveDataPointReader.close()
        print "Closed MWM session."
        
            
def main():
    """
    do things
    """
    # ## start catching data from the zephyr
    
    # zephyr.configure_root_logger()
    # z_serial_port_dict = {"Darwin": "/dev/tty.HXM016473-BluetoothSeri",
                        # "Windows": 23}

    # z_serial_port = z_serial_port_dict[platform.system()]
    # z_ser = serial.Serial(z_serial_port)

    # print "running the zephyr"
    # simulation_workflow([ecgcallback], z_ser)


    ## start catching data from MWM
    target_address = ""
    if platform.system() == 'Windows':
        #target_address = 'COM4'
        target_address = 'COM5'
    elif platform.system() == 'Darwin':
        target_address = '/dev/tty.MindWaveMobile-DevA'
        #target_address = '/dev/tty.MindWaveMobile-DevA-1'
    if not target_address:
        raise IOError("No valid serial port address")

    
    
    t1 = RunMWM()
    t1.connectMWM(target_address)
    t1.start()
    
    while(True):
        try:
            # do data science things here, like read queue data
            if len(eegpower_buffer)>0:
                bandpower = eegpower_buffer.popleft()
                print "bands: {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}".format(*bandpower['brain'])
            if len(eegpower_buffer)>0:
                hrv = hrv_buffer.popleft()
                print "hrv: {0}".format(hrv)
        
        except KeyboardInterrupt:
            print "caught ctrl-C, attempting stop"
            t1.isRunning = False
            pause(1)
            t1.join()
            #find way to kill zephyr thread?
            break; #get out of game loop
        


    

if __name__ == "__main__":
    main()