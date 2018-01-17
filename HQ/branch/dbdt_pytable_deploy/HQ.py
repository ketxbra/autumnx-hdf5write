#!/usr/bin/env python
#####################################################################
#SCRIPT:  ./HQparse.py
#
#AUTHOR:  Kyle Reiter
#         Athabasca University
#         Faculty of Science / Physics
#
#DATE:    Dec 1, 2016
#
#PURPOSE: Library for HQ parser and plotter scripts
#####################################################################
import matplotlib
matplotlib.use('Agg')
import sys,glob2, re,pytz, os, string, wget
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from cycler import cycler
import seaborn as sb
import matplotlib.lines as mlines
import traceback

#Used for clearing up strings with extraneous whitespace
def remove_all(seq, value):
    pos = 0
    for station in seq:
        if station != value:
            seq[pos] = station
            pos += 1
    del seq[pos:]
    return seq

#A clutch of functions to list various nested file types
def readdir(directory):
    dirs = glob2.glob(directory+'*')
    return dirs

def readdirxls(directory):
    dirs = glob2.glob(directory+'**/*.xls')
    return dirs

def readdir2(directory):
    files = glob2.glob(directory+'HA*Harmonique.csv')
    return files

def readlist(directory):
    files = glob2.glob(directory+'**/HA*Harmonique.csv')
    return files

def readnpy(directory):
    '''files = glob2.glob(directory+'**/HA*Harmonique.csv')'''
    files = glob2.glob(directory+'*-allharmonics*.npy')
    return files

def readthd(directory):
    files = glob2.glob(directory+'*-thd*.npy')
    return files

def readdbdt(directory):
    files = glob2.glob(directory+'*-dbdt*.npy')
    return files

def readkv(directory):
    files = glob2.glob(directory+'**/HA*ResumeHarmFreq_seb.csv')
    return files

#Reads csv files and returns pertinent harmonic data as a numpy array
def fileread(fin):
    harm = []
    try:
        with open(fin, 'rb') as file:
            for line in file.xreadlines():
                newline = re.split(',',line[0:len(line)-1])
                if newline[0] == 'NOM_TRANS':
                    continue
                try:
                    dt = re.split(' ',newline[9])
                except:
                    print " does not fit format"
                    continue
                datetime = dt[1][0:len(dt[1])-1]+' - '+dt[0][1:len(dt[0])]
                ndt = dumbtimeparser(datetime)
                dt = re.split(' - ',ndt)
                ntime = dt[0]
                ndate = dt[1]
                try:
                    times = re.split(':',ntime)
                    time = float(times[0])+float(times[1])/60.0+float(times[2])/3600.0
                except IndexError:
                    continue
                appender = [newline[0],ndate,time,float(newline[77]),float(newline[78]),float(newline[79]),float(newline[80]),float(newline[81]),float(newline[82]),float(newline[83]),float(newline[85]),float(newline[86]),float(newline[87]),float(newline[88]),float(newline[89]),float(newline[90]),float(newline[91]),float(newline[93]),float(newline[94]),float(newline[95]),float(newline[96]),float(newline[97]),float(newline[98]),float(newline[99]),ntime]
                harm.append(appender)
    except:
        return 0
    harm = np.array(harm)
    return harm

#Reads numpy binary file. Used, but seems pretty useless/redundant right now.
def npyread(pyfile):
    np.load(pyfile)

#This reads line voltage level from csv files. Not currently used
def kVread(fin):
    data = []
    kV = []
    with open(fin, 'rb') as file:
        for line in file.xreadlines():
            newline = re.split(',',line[0:len(line)-1])
            data.append(newline)
            if newline[0] == 'Heure':
                continue
            try:
                dt = re.split(' ',newline[30])
                times = re.split(':',dt[1][0:len(dt[1])-1])
                time = float(times[0])+float(times[1])/60.0+float(times[2])/3600.0
            except IndexError:
                continue
            kV.append([newline[5],dt[0][1:len(dt[0])],time,float(newline[3]),float(newline[36]),float(newline[4]),float(newline[37]),float(newline[38]),dt[1][0:len(dt[1])-1]])
    harm = np.array(kV)
    return kV

#Generates date/time bounds for dataset. Not used currently.
def bound(data):
    dates = data[0,1]
    datee = data[len(data)-1,1]
    times = data[0,24]
    timee = data[len(data)-1,24]
    return dates, datee, times, timee

#Function to read IAGA files
def read_IAGA(datafile):
    dataf = open(datafile, "rb")
    data = []
    datap = []
    for line in dataf.xreadlines():
        newline = re.split('\s',line[0:len(line)])
        data.append(newline)
    del data[0:13]
    for line in data:
        line = remove_all(line, '\s')
        line = remove_all(line,'')
        try:
            dline = float(line[1][0:2])+float(line[1][3:5])/60+float(line[1][6:8])/3600, float(line[3]), float(line[4]), float(line[5])
            datap.append(dline)
        except ValueError:
            print line
    return datap

#Time string parsing functions
def dumbtimezones(indate):
    timeobj = datetime.strptime(indate,'%H:%M:%S - %Y/%m/%d')
    eastern = pytz.timezone('US/Eastern')
    timeobj = eastern.localize(timeobj)
    timeobj = timeobj.astimezone(pytz.utc)
    return timeobj

def dumbtimeparser(datetime):
    dumbtimeobj = dumbtimezones(datetime)
    output = dumbtimeobj.strftime('%H:%M:%S - %Y/%m/%d')
    return output

def smarttimezones(datetime):
    timeobj = datetime.strptime(datetime,'%H:%M:%S - %Y/%m/%d')
    utc = pytz.utc
    timeobj = utc.localize(timeobj)
    return timeobj

#Reads magnetometer files
def readGMAG(start,end,date1,date2):
    #######Screwing around with time zones because of course not all of our data uses the same time zone#######
    time1 = start+' - '+date1
    time2 = end+' - '+date2
    time1 = dumbtimezones(time1)
    time2 = dumbtimezones(time2)
    basedir = '/media/hq/AUTUMNX/'
    gmagd = read_IAGA(filename)

#Plots individual harmonic data for various HQ stations
def plotter(data,directory,outdir):
    #H2n = np.sqrt(np.square(data[:,3])+np.square(data[:,10])+np.square(data[:,17]))
    #H2n = np.add(np.add(data[:,3],data[:,10]),data[:,17])
    H = []
    try:
        for element in range(2,9):
            H.append((data[:,1+element].astype(float)+data[:,8+element].astype(float)+data[:,15+element].astype(float))/3)
    except:
        return 0
    Hx = 2
    for item in H:
        plt.plot(data[:,2],item,label=str(Hx)+' Harmonic')
        Hx = Hx + 1
    Hx = 2
    date1 = re.split('/',data[0,1])
    date = date1[0]+'-'+date1[1]+'-'+date1[2]
    plt.xlabel('Time [h]')
    plt.ylabel('Harmonic Distortion')
    plt.legend()
    try:
        plt.savefig(outdir+'/'+data[0,0]+'-allharmonics'+date+'-'+data[0,24]+'.png')
    except IOError:
        os.mkdir(outdir+'/')
        plt.savefig(outdir+'/'+data[0,0]+'-allharmonics'+date+'-'+data[0,24]+'.png')
    plt.clf()
    #plt.show()
    return H

#Saves harmonic data to numpy binary file
def datasave(harm,directory,outdir):
    date1 = re.split('/',harm[0,1])
    date = date1[0]+'-'+date1[1]+'-'+date1[2]
    filename = outdir+'/'+harm[0,0]+'-allharmonics'+date+'-'+harm[0,24]+'.npy'
    np.save(filename,harm)

#Does the actual dbdt work for dataset (taken from dbdt script library)
def dbdt(data):
    #data = np.array(data)
    dim = data.shape
    dmag = [(station[1]**2+station[2]**2+station[3]**2)**0.5 for station in data]
    dmag = np.array(dmag)
    print data[:,0]
    print data[:,1]
    print data[:,2]
    print data[:,3]
    print dmag
    datac = np.vstack((data[:,0],data[:,1],data[:,2],data[:,3],dmag))
    datac = np.swapaxes(datac,0,1)
    '''if cadence == 'sec':
        datac = datac.tolist()
        datac = average(datac,2)
        datac = numpy.array(datac)'''
    datac = np.swapaxes(datac,0,1)
    diff = np.diff(datac,axis=1)
    tdiff = np.log(np.sqrt(np.square(diff[1,:])+np.square(diff[2,:])+np.square(diff[3,:])))
    tdnl = np.sqrt(np.square(diff[1,:])+np.square(diff[2,:])+np.square(diff[3,:]))
    dbdt = np.vstack(([datac[0,0:len(datac[0,:])-1],diff[1,:],diff[2,:],diff[3,:],tdiff,tdnl]))
    dbdt = np.swapaxes(dbdt,0,1)

    return dbdt

#generates even/odd harmonic plots
def evenodd(data,station,time,plotloc):
    home = '/Users/Kyle/Data/'
    index = 0
    fig4, (totes) = plt.subplots(nrows = 1)
    fig3, (mag2) = plt.subplots(nrows = 1)
    fig2, (mag) = plt.subplots(nrows = 1)
    fig, (ax0,ax1) = plt.subplots(nrows=2)
    for item in data:
        evens = np.zeros(len(item[:,0]))
        odds = np.zeros(len(item[:,0]))
        for i in range(0,2):
            evens = np.square((item[:,3+i*2].astype(float)+item[:,10+i*2].astype(float)+item[:,17+i*2].astype(float))/3)+evens
            odds = np.square((item[:,4+i*2].astype(float)+item[:,10+i*2].astype(float)+item[:,17+i*2].astype(float))/3)+odds
        evens  = evens + np.square((item[:,9].astype(float)+item[:,16].astype(float)+item[:,23].astype(float))/3)
        total = np.sqrt(evens+odds)
        evens = np.sqrt(evens)
        odds = np.sqrt(odds)
        totes.plot(item[:,2],total, label=station[index])
        ax0.plot(item[:,2],evens, label=station[index])
        ax1.plot(item[:,2],odds, label=station[index])
        index = index+1
    date = re.split('/',data[0][0,1])
    dates = date[0]+'-'+date[1]+'-'+date[2]
    ################Let's Work on some GMAG Stuff####################
    stationlist = ['SALU','AKUL','PUVR','INUK','KJPK','RADI','VLDR','STFL','SEPT','SCHF']
    year = date[0]
    month = date[1]
    day = date[2]
    enddate = re.split('/',data[0][0,1])
    endyear = enddate[0]
    endmonth = enddate[1]
    endday = enddate[2]
    #doing some time bound stuff
    start = float(data[0][0,2])
    end = float(data[0][len(data[0])-1,2])
    for item in stationlist:
        GMAGfile1 = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item,year,month,day)
        GMAGfile2 = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item,endyear,endmonth,endday)
        #Now we have start and end time/date, wget and load data files using read_IAGA
        GMagdest1 = home+'HQdata/AUTUMNX/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item,year,month,day)
        GMagdest2 = home+'HQdata/AUTUMNX/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item,endyear,endmonth,endday)
        dataf = []
        handles = []
        print item
        try:
            if GMAGfile2 == GMAGfile1:
                if os.path.exists(GMagdest1) == False:
                    wget.download(GMAGfile1,GMagdest1)
                data1 = read_IAGA(GMagdest1)
                for line in data1:
                    if start - 2.1 / 3600 < line[0] < end + 2.1 / 3600:
                        dataf.append(line)
            else:
                if os.path.exists(GMagdest1) == False:
                    wget.download(GMAGfile1,GMagdest1)
                if os.path.exists(GMagdest2) == False:
                    wget.download(GMAGfile2,GMagdest2)
                data1 = read_IAGA(GMagdest1)
                data2 = read_IAGA(GMagdest2)
                for line in data1:
                    if line[0] > start - 2.1/3600:
                        dataf.append(line)
                for line in data2:
                    if line[0]+2.1/3600 < end:
                        dataf.append(line)
            dataf = np.array(dataf)
            print "DATAF"
            print dataf
            print "DATAF END"
            dbdtf = dbdt(dataf)
            gmagp = mag.plot(dbdtf[:,0],dbdtf[:,4],label=item)
            mag2.plot(dbdtf[:,0],dbdtf[:,5]/np.linalg.norm(dbdtf[:,5]),label=item)
            handles.append(gmagp)
        except IndexError:
            traceback.print_exc(file=sys.stdout)
            print "GMAG Data Missing?"
            continue

    #################################################################
    cmap=sb.hls_palette(10,l=.3,s=.8)
    sb.set_palette(cmap,n_colors=10)
    plt.legend(bbox_to_anchor=(1.05, 1.7), loc=2, borderaxespad=0.)
    leg = ax1.get_legend()
    for i in range(0,len(leg.legendHandles)):
        leg.legendHandles[i].set_color(cmap[i])
    ax0.set_title('Even Harmonics '+data[0][0,1])
    ax1.set_title('Odd Harmonics '+data[0][0,1])
    plt.subplots_adjust(hspace=0.3)
    plt.tight_layout()
    fig.savefig(plotloc+dates+'-'+time, bbox_inches='tight')
    totes.legend()
    plt.legend(bbox_to_anchor=(1.05, 1.7), loc=2, borderaxespad=0.)
    legt = totes.get_legend()
    for i in range(0,len(legt.legendHandles)):
        legt.legendHandles[i].set_color(cmap[i])
        totes.set_title('Total Harmonics '+data[0][0,1])
    fig4.savefig(plotloc+dates+'-totalharm-'+time,bbox_inches='tight')
    try:
        mag.legend()
        leg2 = mag.get_legend()
        for i in range(0,len(leg2.legendHandles)):
            leg2.legendHandles[i].set_color(cmap[i])
        fig2.savefig(plotloc+dates+'-'+time+'gmag', bbox_inches='tight')
        mag2.legend()
        leg3 = mag2.get_legend()
        for i in range(0,len(leg3.legendHandles)):
            leg3.legendHandles[i].set_color(cmap[i])
        fig3.savefig(plotloc+dates+'-'+time+'gmagnolog', bbox_inches='tight')
    except:
        print "NOPE STILL NO DATA"
    #plt.show()

def writedbdt(data, time, plotloc,stationlist):
    #setting up date/time to read from GMAG IAGA files
    home = '/home/reiter/'
    date = re.split('/',data[0][0,1])
    year = date[0]
    month = date[1]
    day = date[2]
    enddate = re.split('/', data[0][0, 1])
    endyear = enddate[0]
    endmonth = enddate[1]
    endday = enddate[2]
    # doing some time bound stuff
    start = float(data[0][0, 2])
    end = float(data[0][len(data[0]) - 1, 2])
    dates = date[0]+'-'+date[1]+'-'+date[2]

    #writing the thd for each station for the event
    for item in data:
        evens = np.zeros(len(item[:,0]))
        odds = np.zeros(len(item[:,0]))
        for i in range(0,2):
            evens = np.square((item[:,3+i*2].astype(float)+item[:,10+i*2].astype(float)+item[:,17+i*2].astype(float))/3)+evens
            odds = np.square((item[:,4+i*2].astype(float)+item[:,10+i*2].astype(float)+item[:,17+i*2].astype(float))/3)+odds
        evens  = evens + np.square((item[:,9].astype(float)+item[:,16].astype(float)+item[:,23].astype(float))/3)
        total = np.sqrt(evens+odds)
        #evens = np.sqrt(evens)
        #odds = np.sqrt(odds)
        thd = np.vstack((item[:,1],item[:,2],total)).T
        filename = plotloc +  item[0,0]+'-'+ dates + '-' + time  + '-' + 'thd.npy'
        np.save(filename,thd)

    for item in stationlist:
        GMAGfile1 = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item, year, month, day)
        GMAGfile2 = 'http://autumn.athabascau.ca/magdata/L1/{0}/fluxgate/{1}/{2}/{3}/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item, endyear, endmonth, endday)
        # Now we have start and end time/date, wget and load data files using read_IAGA
        GMagdest1 = home+'HQdata/AUTUMNX/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item, year, month, day)
        GMagdest2 = home+'HQdata/AUTUMNX/AUTUMNX_{0}_TGBO_{1}_{2}_{3}_PT0,5S.txt'.format(item, endyear, endmonth, endday)

        dataf = []
        try:
            if GMAGfile2 == GMAGfile1:
                if os.path.exists(GMagdest1) == False:
                    wget.download(GMAGfile1, GMagdest1)
                data1 = read_IAGA(GMagdest1)
                for line in data1:
                    if start - 2.1 / 3600 < line[0] < end + 2.1 / 3600:
                        dataf.append(line)
            else:
                if os.path.exists(GMagdest1) == False:
                    wget.download(GMAGfile1, GMagdest1)
                if os.path.exists(GMagdest2) == False:
                    wget.download(GMAGfile2, GMagdest2)
                data1 = read_IAGA(GMagdest1)
                data2 = read_IAGA(GMagdest2)
                for line in data1:
                    if line[0] > start - 2.1 / 3600:
                        dataf.append(line)
                for line in data2:
                    if line[0] + 2.1 / 3600 < end:
                        dataf.append(line)
            dataf = np.array(dataf)
            dbdtf = dbdt(dataf)
            filename = plotloc +item+'-' + dates + '-' + time +'-dbdt.npy'
            #print filename
            np.save(filename, dbdtf)
        except IndexError:
            traceback.print_exc(file=sys.stdout)
            print "GMAG Data Missing?"
            continue
    return 1

#Function for comparative THD/DBDT Plot and correlations
def harmonics(data,station,dbdt,ddbtlist,time,plotloc):
    #Initialize Plot
    fig1, (mag,THD) = plt.subplots(nrows=2)
    #Goes through list of HQ Stations and calculates THD for them for the specific events
    index = 0
    for item in data:
        evens = np.zeros(len(item[:,0]))
        odds = np.zeros(len(item[:,0]))
        for i in range(0,2):
            evens = np.square((item[:,3+i*2].astype(float)+item[:,10+i*2].astype(float)+item[:,17+i*2].astype(float))/3)+evens
            odds = np.square((item[:,4+i*2].astype(float)+item[:,10+i*2].astype(float)+item[:,17+i*2].astype(float))/3)+odds
        total = np.sqrt(evens+odds)
        THD.plot(item[:,2],total, label=station[index])
        index = index+1
    date = re.split('/',data[0][0,1])
    dates = date[0]+'-'+date[1]+'-'+date[2]

#Averages ever 'factor' values of the input 'data' list
def average(data,factor):
    k = 1
    factor = int(factor)
    mean = 0.0
    mdata = []
    for line in data:
        if k < factor:
            k = k+1
            mean = mean + line
        elif k == factor:
            mean = (mean+line)/float(factor)
            mdata.append(mean)
            mean = 0.0
            k = 1
    return np.array(mdata)