#!/usr/bin/env python
#####################################################################
#SCRIPT:  dataframe_dbdt_builder.py
#
#AUTHOR:  Kyle Reiter
#         University of Calgary
#         Department of Physics and Astronomy
#
#DATE:    Jan 11, 2017
#
#PURPOSE: Processes B field AUTUMNX data sequentially over specified
#         data range and writes to pytable.
#####################################################################

import numpy as np
import pandas as pd
import HQ, re, urllib2, datetime, optparse, tables


def urlwrite(url,filename):
    try:
        response = urllib2.urlopen(url)
    except:
        return

def main():
    h5file = tables.open_file("/home/reiter/Data/Mag/AUTUMNX-Mag.h5", mode="a", title="Mag Data for AUTUMNX")
    stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
    table = {}
    date =  datetime.datetime.utcnow()-datetime.timedelta(days=1)
    strd = date.strftime('%Y_%m_%d')
    year, month, day = re.split('_', strd)

    for station in stationlist:
        if station == 'SALU':
            table[station] = h5file.root.magnetometer.SALU
        elif station == 'AKUL':
            table[station] = h5file.root.magnetometer.AKUL
        elif station == 'PUVR':
            table[station] = h5file.root.magnetometer.PUVR
        elif station == 'INUK':
            table[station] = h5file.root.magnetometer.INUK
        elif station == 'KJPK':
            table[station] = h5file.root.magnetometer.KJPK
        elif station == 'RADI':
            table[station] = h5file.root.magnetometer.RADI
        elif station == 'VLDR':
            table[station] = h5file.root.magnetometer.VLDR
        elif station == 'STFL':
            table[station] = h5file.root.magnetometer.STFL
        elif station == 'SEPT':
            table[station] = h5file.root.magnetometer.SEPT
        elif station == 'SCHF':
            table[station] = h5file.root.magnetometer.SCHF
        print station
        url = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{4}_PT0,5S.txt'.format(station, year, month, day, strd)
        try:
            response = urllib2.urlopen(url)
        except:
            continue
        cd = re.split('\n',response.read())
        del cd[0:13]
        data = []
        for line in cd:
            ld = re.split('\s+',line)
            try:
                datet = ld[0]+' '+ld[1]+'000'
                datet = (datetime.datetime.strptime(datet,'%Y-%m-%d %H:%M:%S.%f')-datetime.datetime.utcfromtimestamp(0)).total_seconds()
                ld = [datet,float(ld[3]),float(ld[4]),float(ld[5])]
                data.append(ld)
            except:
                continue
        mag = table[station].row
        then = datetime.datetime.now()
        print "Starting Data append..."
        for line in data:
            mag['time'] = line[0]
            mag['Bx'] = line[1]
            mag['By'] = line[2]
            mag['Bz'] = line[3]
            mag.append()
        table[station].flush()
        print "{0} s to complete".format(datetime.datetime.now()-then)
    h5file.close()

if __name__ == '__main__':
    main()