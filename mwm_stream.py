# -*- coding: utf-8 -*-
"""
Created on Sat Oct 04 15:22:15 2014

@author: mpesavento
"""

import numpy as np
import matplotlib.pyplot as plt

import sys

from scipy import signal

from mindwavemobile.MindwaveDataPoints import *
from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader

import datetime
from collections import deque

    
    
plotdata=False


#def main():
if __name__ == "__main__":
    
    
    if sys.platform == 'win32':
        #target_COM = 'COM4' #use this to identify correct address?
        #target_name = "MindWave Mobile"
        #target_address = '74:e5:43:B1:96:18' #mjp work MWM
        #target_address = '74:e5:43:be:3f:9e' #mjp home MWM
        target_address = 'COM4'

    elif sys.platform == 'darwin':
        target_address = "MindWave Mobile-devA"
        
    
    
        
    
    
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
                count=0;
                
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
    
            if (dataPoint.__class__ is RawDataPoint):
                #print dataPoint
                rawdatastream.append(dataPoint.rawValue)
    			
            if (dataPoint.__class__ is AttentionDataPoint):
                attentiondata.append(dataPoint.attentionValue)
                
            if (dataPoint.__class__ is MeditationDataPoint):
                meditationdata.append(dataPoint.meditationValue)
                
            if (dataPoint.__class__ is EEGPowersDataPoint):
                #bwdata.append(dataPoint.asDict())
                out['name'] = "EEGPowers"
                out['timestamp'] = datetime.datetime.now()
                out['value'] = [float(x)/dataPoint.maxint for x in dataPoint.asList()]
                bwdata.append(out)
                print bwdata[-1]
        
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