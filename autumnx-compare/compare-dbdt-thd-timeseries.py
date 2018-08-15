import numpy as np
import pandas as pd
import math, urllib2, re, os
import datetime as dt

def iagaread(station,time):
    strd = dt.datetime.utcfromtimestamp(time[0]).strftime('%Y_%m_%d')
    date1 = re.split('_',strd)
    strd2 = dt.datetime.utcfromtimestamp(time[1]).strftime('%Y_%m_%d')
    date2 = re.split('_', strd)
    url = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{4}_PT0,5S.txt'.format(station, date1[0], date1[1], date1[2], strd)
    try:
        response = urllib2.urlopen(url)
    except:
        return 0
    cd = re.split('\n', response.read())
    # delete header
    del cd[0:13]
    data = []
    # convert data from datetime object to time from epoch
    for line in cd:
        ld = re.split('\s+', line)
        try:
            datet = ld[0] + ' ' + ld[1] + '000'
            datet = (dt.datetime.strptime(datet, '%Y-%m-%d %H:%M:%S.%f') - dt.datetime.utcfromtimestamp(0)).total_seconds()
            ld = [datet, float(ld[3]), float(ld[4]), float(ld[5])]
            data.append(ld)
        except:
            continue
    if strd != strd2:
        url = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{4}_PT0,5S.txt'.format(station, date2[0], date2[1], date2[2], strd2)
        try:
            response = urllib2.urlopen(url)
        except:
            return
        cd = re.split('\n', response.read())
        # delete header
        del cd[0:13]
        for line in cd:
            ld = re.split('\s+', line)
            try:
                datet = ld[0] + ' ' + ld[1] + '000'
                datet = (dt.datetime.strptime(datet, '%Y-%m-%d %H:%M:%S.%f') - dt.datetime.utcfromtimestamp(0)).total_seconds()
                ld = [datet, float(ld[3]), float(ld[4]), float(ld[5])]
                data.append(ld)
            except:
                continue
    return data

dBevent = []
thdevend = []

h5file = pd.read_hdf("/Users/Kyle/Data/sorted_files/thd_data.h5",key='thd')
#h5file = pd.read_hdf("/Users/Kyle

limit = [h5file['t'].iloc[0]]
for i, row in h5file.iterrows():
    try:
        if row['t'] > old['t'] + 10:
            limit.extend([old['t']+200, np.nan, row['t']-200])
    except:
        old = row
    old = row
limit.append(h5file['t'].iloc[-1])

#stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
stationlist = ['RADI','VLDR','STFL','SEPT','SCHF']
thdstations = list(h5file)
thdstations.remove('t')
table = {}

tl = []
total = []
while len(limit) > 0:
    total.append(tl)
    tl = []
    for i in limit:
        if math.isnan(i):
            del limit[0:3]
            break
        tl.append(i)
        if len(tl) < 3 and len(limit) < 3:
            del (limit[0:2])
            break
del total[0]
print total
print len(total)


for station in stationlist:
    print station
    for item in total:
        date = dt.datetime.utcfromtimestamp(item[0]).strftime('%Y_%m_%d_%H_%M_%S')
        print date
        dir = '/Users/Kyle/Data/mag/npy/{0}/'.format(date)
        tempd = iagaread(station, item)
        if tempd == 0:
            continue
        try:
            tempd = [x for x in tempd if (item[0] <= x[0] and item[1] >= x[0])]
        except:
            continue
        data = np.array(tempd)
        try:
            np.save('{0}{1}.npy'.format(dir,station),data)
        except:
            os.makedirs(dir)
            np.save('{0}{1}.npy'.format(dir, station), data)


for station in thdstations:
    for item in total:
        date = dt.datetime.utcfromtimestamp(item[0]).strftime('%Y_%m_%d_%H_%M_%S')
        dir = '/Users/Kyle/Data/mag/npy/{0}/'.format(date)
        mask = (h5file['t'] > item[0]) & (h5file['t'] <= item[1])
        thdata = h5file[station].loc[mask]
        time = h5file['t'].loc[mask]
        thdata = np.vstack((time,thdata)).T
        try:
            np.save('{0}{1}.npy'.format(dir,station),thdata)
        except:
            os.makedirs(dir)
            np.save('{0}{1}.npy'.format(dir,station),thdata)