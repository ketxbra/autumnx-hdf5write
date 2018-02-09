import numpy as np
import pandas as pd
import tables, math, csv
import datetime as dt

dBevent = []
thdevend = []

h5file = pd.read_hdf("/Users/Kyle/Data/sorted_files/thd_data.h5",key='thd')
#h5file = pd.read_hdf("/Users/Kyle

limit = [h5file['t'].iloc[0]]
for i, row in h5file.iterrows():
    try:
        if row['t'] > old['t'] + 10:
            limit.extend([old['t']-200, np.nan, row['t']+200])
    except:
        old = row
    old = row
limit.append(h5file['t'].iloc[-1])

bfile = tables.open_file('/Users/Kyle/Data/mag/AUTUMNX-Mag.h5',mode='r',title='Mag Data')
#bfile = tables.open_file('/home/Data/Mag/AUTUMNX-Mag.h5',mode='r',title='Mag Data')
stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
thdstations = list(h5file)
thdstations.remove('t')
dB = {}
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

    for item in total:
        #print list, len(limit)
        try:
            Bx = [ x['Bx'] for x in table[station].where("""(time >= {0}) & (time <= {1})""".format(item[0],item[1]))]
            By = [ x['By'] for x in table[station].where("""(time >= {0}) & (time <= {1})""".format(item[0],item[1]))]
            Bz = [ x['Bz'] for x in table[station].where("""(time >= {0}) & (time <= {1})""".format(item[0],item[1]))]
            t = [ x['time'] for x in table[station].where("""(time >= {0}) & (time <= {1})""".format(item[0],item[1]))]
            dx = np.gradient(Bx)/0.5
            dy = np.gradient(By)/0.5
            dz = np.gradient(Bz)/0.5
            d = np.sqrt(dx**2+dy**2+dz**2)
            maxdB = np.amax(d)
            ind = np.argmax(d)
            tmax = dt.datetime.utcfromtimestamp(t[ind]).strftime('%Y-%m-%d %H:%M:%S.%f')
            dB[station].append([tmax,str(maxdB)])
        except:
            continue


thdmax = {}
for station in thdstations:
    thdmax[station] = []
    for item in total:
        mask = (h5file['t'] > item[0]) & (h5file['t'] <= item[1])
        thdata = h5file.loc[mask]
        mi = np.argmax(thdata['LG2'])
        m = np.amax(thdata['LG2'])
        thdmax[station].append([dt.datetime.utcfromtimestamp(thdata['t'][mi]).strftime('%Y-%m-%d %H:%M:%S.%f'),str(m)])

#print thdmax['LG2']
#print len(dB['VLDR'])

dbdtm = np.array(dB['SALU'])
thdm = np.array(thdmax['Tilly'])


#total = [[dt.datetime.utcfromtimestamp(x) for x in line] for line in total]

for station in stationlist:
    with open('/Users/Kyle/Data/compare/{0}-max.csv'.format(station),'w') as file:
        for line in dB[station]:
            file.writelines(','.join(line) + '\n')
        #np.savetxt('/Users/Kyle/Data/compare/{0}-max.csv'.format(station),dB[station],delimiter=',')
for station in thdstations:
    with open('/Users/Kyle/Data/compare/{0}-max.csv'.format(station),'w') as file:
        for line in thdmax[station]:
            file.writelines(','.join(line) + '\n')
    #np.savetxt('/Users/Kyle/Data/compare/{0}-max.csv'.format(station),thdmax[station],delimiter=',')

bfile.close()