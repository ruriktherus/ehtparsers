#!/usr/local/bin/python2.6


import sys


# Get the AList for the experiment
# and create a dictionary mapping the time
# of scan to the AScan instance for each scan
from alist import AList, isnot, lessthan, greaterthan
from datetime import datetime
filename = sys.argv[1]
exp = AList(open(filename))
final = exp.filter(baseline='SZ', lags=32, freq=344844.0)
#start = datetime(2010, 2, 26, 10, 20, 00)
#stop = datetime(2010, 2, 26, 11, 26, 00)
time2scan = dict((scan.time,scan) for scan in final)


# Parse the SKD file to determine the status
# of the phased-array at the time of each scan
# and add these parameters to the AList
from parse_skd import parse_skd
filename = sys.argv[2]
scans = parse_skd(open(filename))
for scan in scans:
    if time2scan.has_key(scan['time']):
        for k,v in scan.iteritems():
            if k <> 'time':
                setattr(time2scan[scan['time']], k, v)
        setattr(time2scan[scan['time']], 'config', ''.join([str(a) for a in scan['pant']]) + \
                ''.join(scan['conf']) + '(x)' + str(scan['comp']))
        setattr(time2scan[scan['time']], 'pants', len(scan['pant']))
if locals().has_key('start') and locals().has_key('stop'):
    final = final.filter(pant=isnot([4])).filter(datetime=greaterthan(start)).\
            filter(datetime=lessthan(stop))




# Now parse the SMA's TSys file to get the system
# temperature of each antenna for every minute or
# so, later we will interpolate values and assign to
# the AList
import re
from calendar import timegm
from time import asctime, strptime
filename = sys.argv[3]
curr_ant = 0
ants = []
tsys_unsorted = {}
for line in open(filename):
    if line.startswith('#'):
        search = re.search('ACC(?P<ant>[0-9])', line)
        if search:
            curr_ant = int(search.group('ant'))
            ants.append(curr_ant)
            #print "Found new TSys definition for antenna", curr_ant
    else:
        if line.split():
            splitline = line.split()
            time = timegm(strptime(splitline[1], "%Y-%m-%d,%H:%M"))
            curr_tsys = float(splitline[3])
            if time in tsys_unsorted.keys():
                tsys_unsorted[time]['tsys'+str(curr_ant)] = curr_tsys
            else:
                tsys_unsorted[time] = {}
                tsys_unsorted[time]['tsys'+str(curr_ant)] = curr_tsys
tsys = []
for time in sorted(tsys_unsorted):
    tmp_dict = {'unixtime':time}
    tmp_dict.update(tsys_unsorted[time])
    tsys.append(tmp_dict)
    #print tsys[-1]


# Now go through every scan and add the TSys values
# that are closest to the start time
tsrch = [-1, 1, -2, 2, -3, 3]
for scan in final:
    for i in range(len(tsys)):
        if scan.unixtime >= tsys[i]['unixtime']:
            for a in ants:
                tsysn = 'tsys%d'%a
                if tsysn in tsys[i].keys():
                    setattr(scan, tsysn, tsys[i][tsysn])
                else:
                    for tdel in tsrch:
                        if tsysn in tsys[i+tdel]:
                            setattr(scan, tsysn, tsys[i+tdel][tsysn])
                if not hasattr(scan, tsysn):
                    raise ValueError, "No nearby tsys"


# Calibrate the amplitude of each scan according to the
# equivalent system temperature of the phased-array
# configuraton
from math import sqrt
eff = {1 : 163.,
       2 : 163.,
       3 : 163.,
       4 : 163.,
       5 : 163.,
       6 : 163.,
       7 : 163.,
       8 : 163.,
       }
for scan in final:
    sefd_den = 0
    for a in scan.pant:
        sefd_den += 1./(2*getattr(scan, 'tsys%d'%a)*eff[a])
    sefd = 1./sefd_den
    setattr(scan, 'pant_sefd', sefd)
    setattr(scan, 'comp_sefd', 2*getattr(scan, 'tsys%d'%scan.comp)*eff[scan.comp])
    setattr(scan, 'cal_amp', scan.amp*sqrt(scan.comp_sefd*scan.pant_sefd)*10**-4)


# Now do some plotting
from pylab import *
import numpy as np
from matplotlib.dates import num2date
import matplotlib.ticker as ticker
def format_date(x, pos=None):
    return num2date(x).strftime('%H:%M')
fig = figure()
ax1 = fig.add_subplot(211)
ax1.plot(final.datetime, final.cal_amp, 'g-')
ax1.set_ylabel('Calibrated flux (Jy)')
ax1.set_xticks([])
ax2 = fig.add_subplot(212)
ax2.plot(final.datetime, final.amp, 'b.-')
ax2.plot(final.datetime, final.amp[-1]*sqrt([4, 5, 4, 3, 2, 1]), 'b--')
ax2.set_ylabel('Correlated amplitude (Wh)')
ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
show()


# Write a set of columns to an ASCII file
from csv import DictWriter
if len(sys.argv)==5:
    outfile = sys.argv[4]
    fieldnames = [ 'time',
                   'unixtime',
                   'amp',
                   'snr',
                   'sbd',
                   'mbd',
                   'rate',
                   'config',
                   'pants',
                   'cal_amp',
                   ]
    header = dict((f,f) for f in fieldnames)
    csvfile = DictWriter(open(outfile, 'w'), fieldnames, extrasaction='ignore', delimiter = ' ')
    csvfile.writerow(header)
    for scan in final:
        csvfile.writerow(scan)
