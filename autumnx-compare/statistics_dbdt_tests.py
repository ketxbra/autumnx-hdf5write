#!/usr/bin/env python
import numpy as np
import pandas as pd
import tables, math, csv
import datetime as dt
import matplotlib.pyplot as plt

dBevent = []

#bfile = tables.open_file('/Users/Kyle/Data/mag/AUTUMNX-Mag.h5',mode='r',title='Mag Data')
bfile = tables.open_file('/home/reiter/Data/Mag/AUTUMNX-Mag.h5',mode='r',title='Mag Data')
#stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
stationlist = ['SALU']
dB = {}
table = {}

for station in stationlist:
    dB[station] = []
    # should probably clean this up, this is pretty bad right now
    if station == 'SALU':
        table[station] = bfile.root.magnetometer.SALU
    elif station == 'AKUL':
        table[station] = bfile.root.magnetometer.AKUL
    elif station == 'PUVR':
        table[station] = bfile.root.magnetometer.PUVR
    elif station == 'INUK':
        table[station] = bfile.root.magnetometer.INUK
    elif station == 'KJPK':
        table[station] = bfile.root.magnetometer.KJPK
    elif station == 'RADI':
        table[station] = bfile.root.magnetometer.RADI
    elif station == 'VLDR':
        table[station] = bfile.root.magnetometer.VLDR
    elif station == 'STFL':
        table[station] = bfile.root.magnetometer.STFL
    elif station == 'SEPT':
        table[station] = bfile.root.magnetometer.SEPT
    elif station == 'SCHF':
        table[station] = bfile.root.magnetometer.SCHF

    #print list, len(limit)
    print 'starting'
    now = dt.datetime.now()
    Bx = table[station].cols.Bx
    By = table[station].cols.By
    Bz = table[station].cols.Bz
    dx = np.log(np.gradient(Bx) / 0.5)
    dy = np.log(np.gradient(By) / 0.5)
    dz = np.log(np.gradient(Bz) / 0.5)
    d = np.sqrt(dx**2+dy**2+dz**2)
    print 'total time to read',dt.datetime.now() - now
    try:
        '''Bx = [ x['Bx'] for x in table[station]]
        By = [ x['By'] for x in table[station]]
        Bz = [ x['Bz'] for x in table[station]]
        t = [ x['time'] for x in table[station]]
        dx = np.gradient(Bx)/0.5
        dy = np.gradient(By)/0.5
        dz = np.gradient(Bz)/0.5
        d = np.sqrt(dx**2+dy**2+dz**2)
        maxdB = np.amax(d)
        ind = np.argmax(d)'''
    except:
        continue

plt.hist(d)
plt.show()

bfile.close()