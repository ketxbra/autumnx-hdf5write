#!/usr/bin/env python
#####################################################################
#SCRIPT:  dataframe_B_appender.py
#
#AUTHOR:  Kyle Reiter
#         University of Calgary
#         Department of Physics and Astronomy
#
#DATE:    Jan 17, 2017
#
#PURPOSE: Processes B field AUTUMNX data for yesterday's data. Should
#         be run daily as a cron job.
#####################################################################

import re, datetime, tables, numpy as np

def diff(t,x):
    dxdt = np.gradient(x)/np.gradient(t)
    return dxdt

#main function
def main():
    #reads from hdf5 file (must already exist)
    h5file = tables.open_file("/home/reiter/Data/Mag/AUTUMNX-Mag.h5", mode="a", title="Mag Data for AUTUMNX. 2 Hz Cadence data.")
    stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
    table = {}
    dB = {}

    #initialize dBdt data storage class
    class dBdt(tables.IsDescription):
        time = tables.Float64Col()
        dBx = tables.Float32Col()
        dBy = tables.Float32Col()
        dBz = tables.Float32Col()

    #initialize hdf5 file data is to be stored to, and group within that file (file should not already exist)
    dBfile = tables.open_file("/home/reiter/Data/Mag/AUTUMNX-dBdt.h5", mode="a", title="dBdt Data for AUTUMNX. 2Hz Cadence.")
    group = dBfile.create_group("/", 'dBdt', 'dBdt data for AUTUMNX. 2Hz Cadence.')

    #main loop
    for station in stationlist:
        dB[station] = h5file.create_table(group, station, dBdt, "{0} DBdt Data".format(station))
        #should probably clean this up, this is pretty bad right now
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

        try:
            table[station].cols.time.create_csindex()
        except:
            table[station].cols.time.reindex()

        max_i = table.colindexes['time'][-1]
        i = 0
        while (i+1)*2**20 <= max_i:
            t = np.array([table.cols.time[table.colindexes['time'][v]] for v in range(i*2**20,(i+1)*2**20)])[:len(t)-1]
            x = np.array([table.cols.time[table.colindexes['time'][v]] for v in range(i*2**20,(i+1)*2**20)])[:len(x)-1]
            y = np.array([table.cols.time[table.colindexes['time'][v]] for v in range(i * 2 ** 20, (i + 1) * 2 ** 20)])[:len(y)-1]
            z = np.array([table.cols.time[table.colindexes['time'][v]] for v in range(i * 2 ** 20, (i + 1) * 2 ** 20)])[:len(z)-1]
            dx = diff(t,x)
            dy = diff(t,y)
            dz = diff(t,z)

        #append data to table in hdf5 file
        mag = table[station].row

    #close file
    h5file.close()

if __name__ == '__main__':
    main()