#!/usr/bin/env python

import re
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

dir = '/Users/Kyle/Data/compare/'

stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
hqlist = ['Nicolet', 'Outaouais', 'Tilly', 'LG2', 'Rimouski', 'Chateauguay', 'Chibougamau', 'Boucherville', 'Micoua']

nx = 'Tilly'
ny = 'Nicolet'

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
    dbdt = [[dt.datetime.strptime(x[0],'%Y-%m-%d %H:%M:%S.%f'),float(x[1])] for x in dbdt if (x[0] != 'NaN' and float(x[1]) < 100)]
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
        temp.append([abs((item[0]-line[0]).total_seconds()),line[0],line[1]])
    temp = np.array(temp)
    i = np.argmin(temp[:,0])
    if temp[i,0] < 600:
        pairs.append([item[1],temp[i,2]])

pairs = np.array(pairs)

r = stats.pearsonr(pairs[:,0],pairs[:,1])
print r
print len(pairs[:,0]), len(dbdt)
plt.scatter(pairs[:,0],pairs[:,1])
if nsx == 1:
    plt.xlabel('{0} (nT/s)'.format(nx))
else:
    plt.xlabel('{0} %HD'.format(nx))
if nsy == 1:
    plt.ylabel('{0} (nT/s)'.format(ny))
else:
    plt.ylabel('{0} %HD'.format(ny))
plt.title('r = {0} p = {1} N = {2}'.format(round(r[0],3),r[1],len(pairs[:,0])))
plt.ylim(0,max(pairs[:,1]))
plt.xlim(0,max(pairs[:,0]))

plt.savefig('/Users/Kyle/Data/compare/{0}-{1}.png'.format(nx,ny),dpi=200)


#print dbdt[0][0]-thd[0][0]

#print dbdt

#print thd