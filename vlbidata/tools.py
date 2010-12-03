
import sys
import logging
import os.path as path
from csv import DictWriter
from datetime import datetime

import vlbidata


__all__ = [
    'filter',
    'print_table',
    'process_day',
]


def filter(list_, expression=None, **conditions):
    return list_.__filter__(expression=expression, **conditions)


def process_day(day, baseline, year=datetime.now().year, rootdir='/data'):
    datadir = path.join(rootdir, '{0}-{1:0>3}'.format(year, day))
    print 'Will check in %s/ for scan lists...'% datadir
    sys.stdout.write('Parsing alist... ')
    sys.stdout.flush()
    all = vlbidata.parse_alist(path.join(datadir, 'pa.alist'), baseline)
    sys.stdout.write('done!\r\nParsing schedule file (to extract phased array configuration... ')
    sys.stdout.flush()
    skd = vlbidata.parse_skd(path.join(datadir, 'pa.skd'))
    sys.stdout.write('done!\r\nParsing SMA and SMTO Tsys files (this may take a while)... ')
    sys.stdout.flush()
    sma = vlbidata.parse_sma(path.join(datadir, 'sma.tsys'))
    smto = vlbidata.parse_smto(path.join(datadir, 'smto.tsys'), year)
    sys.stdout.write('done!\r\nMerging into single AList (will take even longer)... ')
    sys.stdout.flush()
    final = all + skd + sma + smto
    sys.stdout.write('done!\r\n')
    sys.stdout.flush()
    return final


def print_table(list_, output_filename, keys=None, **kwargs):
    if keys==None:
        keys = list_[0].iterkeys()
    writer = DictWriter(open(output_filename, 'w'), keys, extrasaction='ignore', **kwargs)
    writer.writerows(list_.itervalues())
