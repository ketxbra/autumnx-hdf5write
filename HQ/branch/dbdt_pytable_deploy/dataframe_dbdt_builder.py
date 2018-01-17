#!/usr/bin/env python
#####################################################################
#SCRIPT:  dataframe_dbdt_builder.py
#
#AUTHOR:  Kyle Reiter
#         University of Calgary
#         Department of Physics and Astronomy
#
#DATE:    Jan 17, 2017
#
#PURPOSE: Processes B field AUTUMNX data sequentially over specified
#         data range and writes to pytable.
#####################################################################

import re, urllib2, datetime, optparse, tables

#Runs through range of dates, outputting a datetime object for each between a specified start and and date
def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)+1):
		yield start_date + datetime.timedelta(n)

#parses datetime object into string
def parse_date(date):
	pdate = datetime.datetime.strptime(date,'%Y-%m-%d')
	return pdate

#parses input arguments from command line
def parse_args():
	usage = ("Input date range: %prog [start date] [end date]\n"
			 "Date Format: YYYY-MM-DD\n"
			 "Cadence Format: min or sec\n"
			 )
	args = optparse.OptionParser(usage)
	_,inargs = args.parse_args()
	if len(inargs) < 2:
		print args.format_help()
		args.exit()
	startdate = inargs[0]
	enddate = inargs[1]
	dates = [startdate,enddate]
	procdates = map(parse_date,dates)
	return procdates[0], procdates[1]

#Grabs file from specified url over http
def urlwrite(url,filename):
    try:
        response = urllib2.urlopen(url)
    except:
        return

#main function
def main():
    #initialize magnetic data storage class
    class Magnetics(tables.IsDescription):
        time = tables.Float64Col()
        Bx = tables.Float32Col()
        By = tables.Float32Col()
        Bz = tables.Float32Col()

    #initialize hdf5 file data is to be stored to, and group within that file (file should not already exist)
    h5file = tables.open_file("/home/reiter/Data/Mag/AUTUMNX-Mag.h5", mode="a", title="Mag Data for AUTUMNX")
    group = h5file.create_group("/", 'magnetometer', 'Detector information')

    stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
    table = {}

    #initiilize a new table for each station
    for station in stationlist:
         table[station] = h5file.create_table(group, station, Magnetics, "{0} Magnetic Data".format(station))

    #main loop
    dates = parse_args()
    for date in daterange(dates[0],dates[1]):
        print date
        strd = date.strftime('%Y_%m_%d')
        year, month, day = re.split('_',strd)
        #for each day, get each station's data
        for station in stationlist:
            print station
            #read data from website
            url = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{4}_PT0,5S.txt'.format(station, year, month, day, strd)
            try:
                response = urllib2.urlopen(url)
            except:
                continue
            cd = re.split('\n',response.read())
            #delete header
            del cd[0:13]
            data = []
            #convert data from datetime object to time from epoch
            for line in cd:
                ld = re.split('\s+',line)
                try:
                    datet = ld[0]+' '+ld[1]+'000'
                    datet = (datetime.datetime.strptime(datet,'%Y-%m-%d %H:%M:%S.%f')-datetime.datetime.utcfromtimestamp(0)).total_seconds()
                    ld = [datet,float(ld[3]),float(ld[4]),float(ld[5])]
                    data.append(ld)
                except:
                    continue
            #appends data to table
            mag = table[station].row
            then = datetime.datetime.now()
            print "Starting Data append..."
            for line in data:
                mag['time'] = line[0]
                mag['Bx'] = line[1]
                mag['By'] = line[2]
                mag['Bz'] = line[3]
                mag.append()
            #flush table buffer
            table[station].flush()
            print "{0} s to complete".format(datetime.datetime.now()-then)
    #close hdf5 file
    h5file.close()

if __name__ == '__main__':
    main()