#!/usr/bin/env python

import re
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

dir = '/Users/Kyle/Data/compare/'

stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
hqlist = ['Nicolet', 'Outaouais', 'Tilly', 'LG2', 'Rimouski', 'Chateauguay', 'Chibougamau', 'Boucherville', 'Micoua']

nx = 'RADI'
ny = 'LG2'

if nx in stationlist:
    nsx = 1
elif nx in hqlist:
    nsx = 0
if ny in stationlist:
    nsy = 1
elif ny in hqlist:
    nsy = 0

dbdtf = dir+nx+'-max.csv'
thdf = dir+ny+'-max.csv'

print dbdtf,thdf

dbdt = []
thd = []

with open(dbdtf,'r') as file:
    for line in file.xreadlines():
        newline = re.split(',', line[0:len(line) - 1])
        dbdt.append(newline)

with open(thdf,'r') as file:
    for line in file.xreadlines():
        newline = re.split(',', line[0:len(line) - 1])
        thd.append(newline)

if nsx == 1:
    dbdt = [[dt.datetime.strptime(x[0],'%Y-%m-%d %H:%M:%S.%f'),float(x[1])] for x in dbdt if  (x[0] != 'NaN' and float(x[1]) < 100)]
else:
    dbdt = [[dt.datetime.strptime(x[0],'%Y-%m-%d %H:%M:%S.%f'),float(x[1])*100] for x in dbdt if x[0] != 'NaN']
if nsy == 1:
    thd = [[dt.datetime.strptime(x[0],'%Y-%m-%d %H:%M:%S.%f'),float(x[1])] for x in thd if (x[0] != 'NaN' and float(x[1]) < 100)]
else:
    thd = [[dt.datetime.strptime(x[0],'%Y-%m-%d %H:%M:%S.%f'),float(x[1])*100] for x in thd if x[0] != 'NaN']

pairs = []

for item in dbdt:
    temp = []
    for line in thd:
        temp.append([abs(line[0]-item[0]).total_seconds(),(line[0]-item[0]).total_seconds()])
    temp = np.array(temp)
    i = np.argmin(temp[:,0])
    if temp[i,0] < 200:
        pairs.append(temp[i,1])

pairs = np.array(pairs)

print pairs
plt.hist(pairs)
plt.xlabel('time difference (s)'.format(nx))
plt.ylabel('# events'.format(ny))

plt.title('Max {0} - Max {1} Time Difference'.format(ny,nx))
'''plt.ylim(0,max(pairs[:,1]))
plt.xlim(0,max(pairs[:,0]))'''

plt.savefig('/Users/Kyle/Data/compare/{0}-{1}-DeltaT.png'.format(nx,ny),dpi=200)


#print dbdt[0][0]-thd[0][0]

#print dbdt

#print thd