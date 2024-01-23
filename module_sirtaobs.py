"""
This module provides functions to read 
data from SIRTA, in original form or in a 
transformed format, and to plot some of these. 
"""

import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def readanemofile(fname):
    """
    Reads the dates and wind (U, V) from files 
    that have been prepared by Bastien Alonzo. 
    """
    f = open(fname)
    b = f.readlines()
    tt = []; u10=[];v10=[]
    for ll in b[1:]:
        lls = ll.strip().split(',')
        if lls[1]!='nan':
            tt.append(datetime.strptime(lls[0],'%Y-%m-%d %H:%M:%S'))
            u10.append(eval(lls[1]))
            v10.append(eval(lls[2]))
    return tt,u10,v10

def dfreadanemo(fname):
	tt,u10,v10 = readanemofile(fname)
	val = np.transpose(np.asarray([u10,v10]))
	uv = pd.DataFrame(val,index=tt,columns=['u','v'])	
	return uv

def find_indices(lst, condition): 
    return [i for i, elem in enumerate(lst) if condition(elem)]

# The following have been written for lidar data
# one small difficulty has consisted in going 
# from the time values (scalar time) to dates 
# with hours and minutes (10 minutes = 1/6 of an hour)

def readlidarfile(fname="/home/plougon/HM/W/WindEnergy/SIRTA/Doppler-lidar_Wind-profile_SIRTA_2014-2015.txt"):
    """Reads the file for Doppler lidar measurements."""
    f = open(fname)
    b = f.readlines()
    return b

def timelidar(bllin):
    """return a date, taking into account that hour is fractional, 
    by steps of 10 min
    """
    epsilon = 1.e-2
    if type(bllin)==str:
        bll=bllin.strip().split(',')
    elif type(bllin)==list:
        bll=bllin
    else:
        print('Problem in timelidar, not supported format for argument')
    hhr = float(bll[3])
    hh  = int(np.floor(hhr))
    if hhr - np.floor(hhr) < 0+epsilon:
        mi = 0
    elif hhr - np.floor(hhr) < 1./6.+epsilon:
            mi = 10
    elif hhr - np.floor(hhr) < 2./6.+epsilon:
            mi = 20
    elif hhr - np.floor(hhr) < 3./6.+epsilon:
            mi = 30
    elif hhr - np.floor(hhr) < 4./6.+epsilon:
            mi = 40
    elif hhr - np.floor(hhr) < 5./6.+epsilon:
            mi = 50
    elif hhr - np.floor(hhr) > 5./6.+epsilon:
            print("Probleme dans la lecture de l'heure, au-dela de 50 minutes")
    #print([bll[0], bll[1], bll[2], hh, mi])
    return datetime(int(bll[0]), int(bll[1]), int(bll[2]), hh, mi)


def clean_data_time(uh, td): 
    """This function gets rid of erroneous data, with values -999
    or something like that...
    """
    uhn = [uv for uv in uh if uv > -990.]
    tdn = [td[ih] for ih in range(len(uh)) if uh[ih] > -990.]
    return uhn, tdn

def findlidardayline(b,dte):
    """ Find the lines corresponding to a given day """
    bs = b[1].strip().split(',')
    be = b[-1].strip().split(',')
    tbefore = dte-timelidar(bs)
    tafter  = timelidar(be)-dte
    #print(tbefore.days,tafter.days)
    iguess  = int(len(b)*float(tbefore.days)/float(tbefore.days+tafter.days))
    tdif = dte-timelidar(b[iguess].strip().split(','))
    tdifins = tdif.days*86400 + tdif.seconds
    yes_go_on = True
    while tdifins!=0 and yes_go_on:
        tdif = dte-timelidar(b[iguess].strip().split(','))
        tdifins = tdif.days*86400 + tdif.seconds
        iguess += int(tdifins/600)
        yes_go_on = iguess>-1 and iguess<len(b)    
    #print(timelidar(b[iguess].strip().split(',')))
    if timelidar(b[iguess].strip().split(','))!=dte:
        print("Problem in findlidardayline: outside indices")
    return iguess

def plotlidarprofile(b,dte,lco='red',lwidth=1.0,logornot=0):
    """lco is color of line, logornot=1 for a log plot """
    il = findlidardayline(b,dte)    
    print(dte)
    type(dte)
    if il>-1 and il<len(b):
        bl = b[il].strip().split(',')
        uu = [float(v) for v in bl[16:27]]
        liheights=[40., 60., 80., 120., 140., 150., 160., 180., 200., 225., 250.]
        if logornot==1:
            plt.semilogy(uu,liheights,'o',linewidth=1.0,color=lco,linestyle='solid')
        else:  
            if lwidth==2:
                plt.plot(uu,liheights,'o',linewidth=1.0,color=lco,linestyle='solid',label=dte)
            else:
                plt.plot(uu,liheights,'--',linewidth=1.0,color=lco,linestyle='solid')
            plt.axis([0., 20., 0., 265.])
        #plt.legend(loc="lower right")
        #plt.show()
        #plt.grid()
    return np.array(uu), np.array(liheights)


def extracttimeseries(z=80,fname="/home/plougon/HM/W/WindEnergy/SIRTA/Doppler-lidar_Wind-profile_SIRTA_2014-2015.txt"):
    zindex = {40:16, 60:17, 80:18, 120:19, 140:20, 150:21, 160:22, 200:23, 225:24, 250:25}
    il = zindex[z]
    b=readlidarfile(fname)
    uu = []; ti = []
    for bl in b: 
        bv = bl.strip().split(',')
        uu.append(eval(bv[il]))
        ti.append(timelidar(bl))
    uuc, tic = clean_data_time(uu,ti)
    return uuc, tic

def plotadaylidar(dte=datetime(2014,12,1),z=80,lco='black'):
    """
    This function plots one day of lidar data at the height 
    indicated. It is written so that successive plots 
    can be superposed
    """
    uu,tt = extracttimeseries(z)
    b = readlidarfile()
    its = findlidardayline(b,dte)
    oneday = datetime(2014,12,2)-datetime(2014,12,1)
    ite = findlidardayline(b,dte+oneday)
    if ite-its < 144: 
        print('All the observations are not available for that day')
    else: 
        ret = [ttl-dte for ttl in tt[its:ite]]
        print(ret[1],ret[-1])
        retd = [(retl.days*86400.+retl.seconds)/3600. for retl in ret]
        print(retd[1],retd[-1])
        plt.plot(retd,uu[its:ite],lco)
        plt.grid()
    return uu[its:ite]

