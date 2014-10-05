# -*- coding: utf-8 -*-
"""
Created on Sat Oct 04 15:22:15 2014

@author: mpesavento
"""

import numpy as np
import matplotlib.pyplot as plt

import sys

from scipy import signal
from math import log

from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

import time
from collections import deque
import requests
import simplejson as json
    
HOST_NAME = '172.31.32.38'
plotdata=False

playername = 'player1_val'

#def main():
if __name__ == "__main__":
    
    if len(sys.argv)==1:
        argin = str(sys.argv[1]).lower()
        if "player" not in argin:
            playername = 'player' + argin
        else:
            playername = argin
        if '_val' not in playername:
            playername += '_val'
    
        
    
    if sys.platform == 'win32':
        #target_COM = 'COM4' #use this to identify correct address?
        #target_name = "MindWave Mobile"
        #target_address = '74:e5:43:B1:96:18' #mjp work MWM
        #target_address = '74:e5:43:be:3f:9e' #mjp home MWM
        if playername is 'player1_val':
            target_address = 'COM4'
        elif playername is 'player2_val':
            target_address = 'COM5'

    elif sys.platform == 'darwin':
        if playername is 'player1_val':
            target_address = '/dev/tty.MindWaveMobile-DevA'
        elif playername is 'player2_val':
            target_address = '/dev/tty.MindWaveMobile-DevA-1'
        #target_address = "/dev/tty.MindWaveMobile-DevA"

    print "running " + playername
    print "Connecting to MWM...",
    try:
        mindwaveDataPointReader = MindwaveDataPointReader(target_address)
        mindwaveDataPointReader.start() # connect to the mindwave mobile headset
    except IOError as e:
        print e
        print "Couldn't connect to MWM device. Check address? Is it turned on?";
        sys.exit(-1)
        
    print " connected"
    
    # datastream = collections.deque;
    rawdatastream = deque()
    attentiondata = deque()
    meditationdata = deque()
    bwdata = deque()
    # elta (0.5 - 2.75Hz), theta (3.5 - 6.75Hz), low-alpha (7.5 - 9.25Hz), 
    # high-alpha (10 - 11.75Hz), low-beta (13 - 16.75Hz), high-beta (18 - 29.75Hz), 
    # low-gamma (31 - 39.75Hz), and mid-gamma (41 - 49.75Hz)
    
    if plotdata:
        fig=plt.figure()
        axdata=plt.axis()
        plt.ion()
        plt.show()    
    
    while(True):
        try:
            dataPoint = mindwaveDataPointReader.readNextDataPoint()
            
            if dataPoint.__class__ is PoorSignalLevelDataPoint:
                count=0
                
                if not dataPoint.headSetHasContactToSkin():
                    #chek the first one, and if no contact, loop until dies
                    count+=1
                    dataPoint = mindwaveDataPointReader.readNextDataPoint()
                    print "waiting for signal quality"
                    while(not dataPoint.headSetHasContactToSkin() or count>10000):
                        count+=1
                        dataPoint = mindwaveDataPointReader.readNextDataPoint()
                    if count>10000:
                        print "No contact, quitting"
                        sys.exit(-2)
                    else:
                        print "Contact dectected"
    
#            elif (dataPoint.__class__ is RawDataPoint):
#                #print dataPoint
#                rawdatastream.append(dataPoint.rawValue)
#    			
#            elif (dataPoint.__class__ is AttentionDataPoint):
#                attentiondata.append(dataPoint.attentionValue)
#                
#            elif (dataPoint.__class__ is MeditationDataPoint):
#                meditationdata.append(dataPoint.meditationValue)
#                
            
            elif (dataPoint.__class__ is EEGPowersDataPoint):
                scaledHighAlpha = 1000 * dataPoint.highAlpha/float(dataPoint.maxint)
                scaledLowAlpha = 1000 * dataPoint.lowAlpha/float(dataPoint.maxint)
                scaledBeta = 1000 * ((dataPoint.lowBeta + dataPoint.lowBeta)/2.)/float(dataPoint.maxint)
                #scaledval = 1 * dataPoint.highAlpha/float(dataPoint.maxint)
                #scaledval = np.log(dataPoint.highAlpha)/np.log(float(dataPoint.maxint))
                #scaledval = log(dataPoint.highAlpha)/log(float(2**20)+1e-8)
                data = {playername: scaledHighAlpha}#, scaledLowAlpha }
                #data = {'brain': scaledBeta}
                
                out = {'brain':scaledBeta, 'timestamp': time.time()}
                
                
                #values = [float(x)/dataPoint.maxint for x in dataPoint.asList()]
                #data['value'] = values
                jsn = json.dumps(data)
                st = 'http://%s:8000/update_data?update=%s' % (HOST_NAME, jsn)
                requests.post(st)
                bwdata.append(out)
                if len(bwdata)==1:
                    prevtime=0
                else:
                    prevtime=bwdata[-2]['timestamp']
                print "alphaH {0} --> {1:1.4f} at {2}".format(dataPoint.highAlpha, out['brain'], out['timestamp'])
        
    #        if len(rawdatastream) > Fs:
    #            plt.plot(rawdatastream)
    #            plt.show()
    #            pass
        
            if plotdata:
                plt.axis(axdata)
                if datalines:
                    axdata.lines.remove(datalines[0])
                #datalines = plt.plot(localdata,'b')
                datalines = plt.plot(bwdata['value'])
                plt.axis('tight')
                plt.ylabel('EEG bandwidths')
                plt.xlabel('sample')
                
        except KeyboardInterrupt:
            break;
    
    
    #close it down    
    mindwaveDataPointReader.close()
    print "Closed MWM session."
    
    
    
                
#if __name__ == "__main__": 
#    main()