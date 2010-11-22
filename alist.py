#!/usr/bin/env python


from csv import reader
from time import asctime, strptime, gmtime
from datetime import datetime
from calendar import timegm


# Taken from Haystack's aformat.doc
#       = ( (FIELD_NAME, TYPE_FUNC, SHORT_NAME),
#           ...
#           )
AFIELDS = ( ('Format version #', int, 'format'), # >=5 implies Mk4
            ('Root id code', str, 'root'), # 6-char lower case
            ('File type (2)', int, 'type'), # General format for fringe data
            ('Fileset #', int, 'fileset'), # Part of filename
            ('Duration', int, 'duration'), # Nominal duration (sec)
            ('Length', int, 'length'), # Seconds of data represented.
            ('Offset', int, 'offset'), # Offset (sec) of mean time of data 
            ('Expt serial #', int, 'experiment'), # Part of filename
            ('Scan ID', str, 'scan'), # From obsvex, blanks trimmed
            ('Procdate', str, 'procdate'), # FRNGE/fourfit processing time
            ('Year of scan', int, 'year'), # Four-digit year.
            ('Time tag', str, 'timetag'), # Nominal start time of data record
            ('Scan offset', int, 'scan_offset'), # Scan time to time tag (sec)
            ('Source name', str, 'source'), # Blank-padded ascii string
            ('Baseline', str, 'baseline'), # 2-char baseline id 
            ('QF/errcode', str, 'errcode'), # 2-char qcode and errcode
            ('Band/#freq', str, 'band'), # e.g. X08 for X-band 8 freqs
            ('Polarization', str, 'pol'), # RR, LL, RL, LR
            ('Lags', int, 'lags'), # Number of lags in correlation
            ('Amplitude', float, 'amp'), # In units of 1/10000
            ('Ampl. SNR', float, 'snr'), # 4 significant digits
            ('Phase(deg)', float, 'phase_deg'), # Can be of various type
            ('Phase SNR', float, 'phase_snr'), # 4 significant digits
            ('Data type', str, 'data_type'), # First char is data origin
            ('Resid SBD', float, 'sbd'), # Microseconds
            ('Resid MBD', float, 'mbd'), # Microseconds
            ('MBD ambiguity', float, 'mbd_amb'), # Microseconds
            ('Resid rate', float, 'rate'), # Picoseconds/second
            ('Ref. elevation', float, 'ref_el'), # At reference epoch, degrees
            ('Rem. elevation', float, 'rem_el'), # At reference epoch, degrees
            ('Ref. azimuth', float, 'ref_az'), # At reference epoch, degrees
            ('Rem. azimuth', float, 'rem_az'), # At reference epoch, degrees
            ('u (megalambda)', float, 'u'), # precision 4 sig. digits
            ('v (megalambda)', float, 'v'), # precision 4 sig. digits
            ('ESDESP', str, 'ESDESP'), # E=ref.tape error rate exponent: 
            ('Reference epoch', str, 'epoch'), # mmss 
            ('Reference frequency', float, 'freq'), # Precision 10 KHz
            ('Total e.c. phase', float, 'ecphase'), # Regardless of field 21
            ('Total drate', float, 'drate'), # At ref epoch, microsec/sec
            ('Total mbdelay', float, 'total_mbd'), # At ref epoch, microsec
            ('Total SBD-MBD', float, 'total_sbdmbd'), # At ref epoch, microsec
            ('Search coh. time', int, 'scotime'), # Seconds
            ('Zero-loss coh. time', int, 'ncotime'), # Seconds
            )

# Callback functions required by DEP_FIELDS
def get_time(year=2009, timetag='323-000000'):
    return asctime(strptime(str(year+2000)+timetag, "%Y%j-%H%M%S"))
def get_unixtime(time=get_time()):
    return float(timegm(strptime(time)))
def get_datetime(time=get_unixtime()):
    return datetime(*strptime(time)[:6])

# A list of fields to add on to the standard ones that are dependent
# on other fields, i.e. their callback functions require some previous
# field
#          = ( (FIELD_NAME, CALLBACK, SHORT_NAME, FIELDS_NEEDED),
#              ...
#              )
DEP_FIELDS = ( ('Time of scan', get_time, 'time', ['year','timetag']),
               ('Unix time of scan', get_unixtime, 'unixtime', ['time']),
               ('Python datetime of scan', get_datetime, 'datetime', ['time']),
               )


class list_:

    def __init__(self, OBJ):
        if hasattr(OBJ, '__iter__'):
            self.list = list(OBJ)
        else:
            self.list = [OBJ,]

    def __repr__(self):
        return repr(self.list)

    def __contains__(self, OBJ):
        valid = True
        for i in self.list:
            if i <> OBJ:
                valid = False
        return valid

    def arestrings(self):
        valid = True
        for i in self.list:
            if type(i) <> str:
                valid = False
        return valid

    def arenumbers(self):
        pass

class isnot:

    def __init__(self, OBJ):
        self.obj = OBJ

    def __repr__(self):
        return "<is not %s>" %self.obj

    def __eq__(self, OBJ):
        return self.obj <> OBJ

    def __ne__(self, OBJ):
        return self.obj == OBJ


class greaterthan:
    
    def __init__(self, OBJ):
        self.obj = OBJ

    def __repr__(self):
        return "<greater than %s>" %self.obj

    def __eq__(self, OBJ):
        return OBJ >= self.obj

    def __ne__(self, OBJ):
        return OBJ < self.obj

class lessthan:
    
    def __init__(self, OBJ):
        self.obj = OBJ

    def __repr__(self):
        return "<greater than %s>" %self.obj

    def __eq__(self, OBJ):
        return OBJ <= self.obj

    def __ne__(self, OBJ):
        return OBJ > self.obj


class AScan:

    def __init__(self, entry):
        for field in range(len(AFIELDS)):
            setattr(self, AFIELDS[field][2],
                    AFIELDS[field][1](entry[field]))
        for field in range(len(DEP_FIELDS)):
            kwargs = dict((key,getattr(self, key)) \
                          for key in DEP_FIELDS[field][3])
            setattr(self, DEP_FIELDS[field][2],
                    DEP_FIELDS[field][1](**kwargs))

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        for mbr in dir(self):
            if not mbr.startswith('_'):
                yield mbr

    def __repr__(self):
        return "<AScan %s: %s/%s, %d sec, SNR %0.2f>"\
            %(self.scan, self.baseline, self.source,
              self.duration, self.snr)

    def get(self, k, d=None):
        try:
            return getattr(self, k)
        except AttributeError:
            return d


class AList:

    def __init__(self, OBJ):
        self.data = []
        if isinstance(OBJ, file):
            self.parse(OBJ)
        else:
            try:
                data = list(OBJ)
            except TypeError:
                self.data += data

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return "<AList %s: %d entries>"\
            %(set(self.experiment), len(self.data))

    def __getattr__(self, attr):
        out = []
        for scan in self.data:
            out.append(getattr(scan, attr))
        return list(out)
    
    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __add__(self, other):
        if isinstance(other, AList):
            return AList(self.data+other.data)
        else:
            print "AList addition only supported for AList instances"

    def parse(self, OBJ):
        for entry in reader(OBJ, delimiter=' ', skipinitialspace=True):
            self.data.append(AScan(entry))

    def combine(self, OBJ):
        obj_type = type(OBJ)
        if obj_type == list:
            self.data += OBJ
        elif isinstance(OBJ, AList):
            print "Please use AList addition to combine ALists"
            self.data += OBJ.data

    def filter(self, **kwargs):
        valid_scans = []
        for scan in self.data:
            valid = True
            for k,v in kwargs.iteritems():
                if getattr(scan, k) not in list_(v):
                    valid = False
            if valid: valid_scans.append(scan)
        return AList(valid_scans)


if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
                      help='read input FILE using A-list format',
                      metavar='FILE')
    parser.add_option('-s', '--snrmin', dest='snrmin', type='float',
                      help='only show scans with strengths of SNR or better',
                      metavar='SNR')
    (options, args) = parser.parse_args()
    print "Reading from: %s" %options.filename
    if options.filename.endswith('.alist'):
        AFILE = open(options.filename)
        expname = 'e' + options.filename.strip('.alist')
    else:
        NameError('Filename must end with .alist!')

    globals_ = globals()
    exp = AList(AFILE)

    globals_[expname] = exp
    globals_.update(dict(('s%s'%s,exp.filter(source=s)) for s in exp.source))
