## collect ECG and EEG data to find correlations

import numpy as np
#import os
#from scipy.signal import medfilt #eventually use this?

import matplotlib.pyplot as plt

def createWindowMatrix(data, winlen=15, offset=4):
    if type(data).__module__ is not np.__name__:
        data = np.array(data)
    ix = np.arange(0, data.size, offset)
    ix = ix[ix+winlen<=data.size]
    return ix[:,np.newaxis] + np.arange(1,winlen)*np.ones(ix.shape, dtype=int)[:,np.newaxis]



def getHR(rri, winlen=15, offset=4):
    """
    calculate smoothed heart rate as the median value over a window with length winlen
    expects RRIs in seconds
    """
    rria = np.array(rri)
    W = createWindowMatrix(rria, winlen, offset)
    instantHR = 60 / rria[W]
    smoothHR = np.median(instantHR, axis=1)
    return smoothHR


def getSDNN(rri, winlen=15, offset=4):
    """
    calculate the HRV using the SDNN method, standard deviation over a fixed window
    median filter the output
    """
    #as_strided = np.lib.stride_tricks.as_strided
    rria = np.array(rri)
    W = createWindowMatrix(rria, winlen, offset)
    
    M = rria[W]
    sdnn = np.std(M, axis=1)
    return sdnn
    
def getRMSSD(rri, winlen=15, offset=4):
    """
    another variation on HRV
    """
    rria = np.array(rri)
    W = createWindowMatrix(rria, winlen, offset)
    M = rria[W]
    
    return np.sqrt(np.sum(np.diff(M, axis=1)**2, axis=1) * 1/(len(rri)-1), axis=1 )



def removeOutliers(data, threshold=3):
    """
    expecting np.array in, removes outliers beyond threshold (in Standard Deviations)
    """
    m = np.mean(data)
    s = np.std(data)
    dataout = [ x for x in data if x<=m+s*threshold and x>= m-s*threshold]
    return (dataout, m, s)
    




if __name__ == "__main__":
    
    datafile = open("ecg_rri_test.txt","r")
    #indata = datafile.read().splitlines()
    indata = datafile.read().rsplit("\n")
    rri = [int(x.strip()) for x in indata if x ]
    datafile.close()
    
    # use subarray to start
    rri = rri[:1000]
    

    
    plt.figure()
    plt.plot(rri,'o')
    thresh=3
    m = np.mean(rri)
    s = np.std(rri)
    plt.axhline(m+thresh*s, color='r')
    plt.axhline(m-thresh*s, color='r')
    plt.show()
    
   
    
    Norig = len(rri)
    print "found %i RRIs" % Norig
    (rri, m, s) = removeOutliers(rri)
    print "removed %i bad values" % int(Norig - len(rri))
    
  
    
    winlen=30
    offset=10
    hr = getHR( rri, winlen, offset)
    hrv = getSDNN( rri, winlen, offset)
    
    t = np.arange(0, len(rri), offset)
    t = t[t+winlen<=len(rri)]  
    
    plt.close("all")
    fig = plt.figure()
    plt.subplot(3,1,1)
    plt.plot(rri,'o')
    plt.ylabel("RRI (ms)")
    plt.subplot(3,1,2)
    plt.plot(t, hr, linewidth=2)
    plt.ylabel("Heart Rate (bpm)")
    plt.subplot(3,1,3)
    plt.plot(t, hrv, linewidth=2)
    plt.ylabel("HRV (ms)")
    
    plt.show()
    