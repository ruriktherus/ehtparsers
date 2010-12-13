
import sys
import logging
import os.path as path

from math import sqrt
from datetime import datetime

import vlbidata


__all__ = [
    'filter',
    'print_table',
    'process_day',
    'calc_phringes_sefd',
    'calc_calibrated_flux',
]


def filter(list_, expression=None, **conditions):
    return list_.__filter__(expression=expression, **conditions)


def process_day(day, baseline, year=datetime.now().year, rootdir='/data', **kwargs):
    datadir = path.join(rootdir, '{0}-{1:0>3}'.format(year, day))
    print 'Will check in %s/ for scan lists...'% datadir
    sys.stdout.write('Parsing alist... ')
    sys.stdout.flush()
    all = vlbidata.parse_alist(path.join(datadir, 'pa.alist'), baseline)
    sys.stdout.write('done!\r\nParsing schedule file (to extract phased array configuration... ')
    sys.stdout.flush()
    skd = vlbidata.parse_skd(path.join(datadir, 'pa.skd'), ignore_pants='38')
    sys.stdout.write('done!\r\nParsing SMA and SMTO Tsys files (this may take a while)... ')
    sys.stdout.flush()
    sma = vlbidata.parse_sma(path.join(datadir, 'sma.tsys'))
    smto = vlbidata.parse_smto(path.join(datadir, 'smto.tsys'), year)
    sys.stdout.write('done!\r\nMerging into single AList (will take even longer)... ')
    sys.stdout.flush()
    final = all + skd + sma + smto
    sys.stdout.write('done!\r\nCalibrating local amplitudes by system temperatures...')
    sys.stdout.flush()
    calc_calibrated_flux(final)
    sys.stdout.write('done!\r\n')
    sys.stdout.flush()
    return filter(final, **kwargs)


def calc_phringes_sefd(list_):
    for scan in list_.itervalues():
        sma_dish_gain = 130. #Jy/K
        sefd = 1./sum(1./(2*sma_dish_gain*scan['tsys_sma{0}'.format(pant)]) for pant in scan.pants)
        scan['phringes_sefd'] = sefd


def calc_calibrated_flux(list_):
    calc_phringes_sefd(list_)
    for scan in list_.itervalues():
        sma_dish_gain = 130. #Jy/K
        smto_dish_gain = 50. #Jy/K
        phringes_sefd = scan['phringes_sefd']
        comp_sefd = 2*sma_dish_gain*scan['tsys_sma{0}'.format(scan.comp)]
        smto_sefd = 2*smto_dish_gain*int(scan['tsys_smto2'])
        if scan.baseline == 'PZ':
            hawaii_sefd = phringes_sefd
            other_sefd = comp_sefd
        elif scan.baseline == 'SZ':
            hawaii_sefd = comp_sefd
            other_sefd = smto_sefd
        elif scan.baseline == 'SP':
            hawaii_sefd = phringes_sefd
            other_sefd = smto_sefd
        scan['cal_flux'] = scan.amp * sqrt(other_sefd*hawaii_sefd) / 10000.


def print_table(list_, output_filename, keys=None,
                header=None, column_width=15, **kwargs):
    if keys==None:
        keys = list_[0].iterkeys()
    if header==None:
        header = keys
    header_fmt = ''.join('{{{key}:<{column_width}}} ' \
                         .format(key=key, column_width=column_width) \
                         for key in range(len(header)))
    with open(output_filename, 'w') as file_:
        file_.write(header_fmt.format(*header) + '\n')
        for scan in list_.itervalues():
            file_.write(header_fmt.format(*list(scan[field] for field in keys)) + '\n')
