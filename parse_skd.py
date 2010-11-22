#!/usr/bin/env python


import re
import time


TIME_FMT = '%Yy%jd%Hh%Mm%Ss'


SCAN_RE = r"""scan\ (?P<name>\w+);\n          # scan specifier
              \*.+\n\*\ +(?P<pant>[1-8]*)     # get the PA antenna
              (?P<conf>[dDfFwWaApP]*)         # get the configuration
              \(x\)(?P<comp>[0-9]).+\n             # get the comp. antenna
               \ +start=(?P<time>\w+);        # start time
              \ mode=(?P<mode>\w+);           # freq. def used
              \ source=(?P<source>.+);\n      # source name
              (?:\*.+\n)?(?:^.+;\n){0,3}      # skips two (or three) lines
              endscan;$"""

def parse_skd(FILE, debug=False):
    SCANS = []
    STR = ''.join(FILE.readlines())
    ITER = re.finditer(SCAN_RE, STR, re.X | re.M)
    for match in ITER:
        SCAN = match.groupdict()
        SCAN['pant'] = [int(a) for a in SCAN['pant']]
        SCAN['comp'] = int(SCAN['comp'][0])
        SCAN['conf'] = list(SCAN['conf'].upper())
        SCAN['time'] = time.asctime(\
            time.strptime(SCAN['time'], TIME_FMT))
        SCANS.append(SCAN)
        if debug:
            print "FOUND SCAN", SCAN['name']
            print "  PA ANT", SCAN['pant']
            print "  COMP ANT", SCAN['comp']
            print "  CONFIG", ''.join(SCAN['conf'])
            print "  USING", SCAN['mode']
            print "  AT", SCAN['time']
            print "  ON SOURCE", SCAN['source']
    if debug:
        print "TOTAL: %d scans" %len(SCANS)
    return SCANS
    

if __name__ == '__main__':

    import sys

    if len(sys.argv) <> 2:
        raise AttributeError, "No .skd file specified!"
    elif not sys.argv[1].endswith('.skd'):
        raise AttributeError, "File given is not .skd!"
    else:
        print "PARSING:", sys.argv[1]

    FILE = open(sys.argv[1])
    scans = parse_skd(FILE, debug=True)

