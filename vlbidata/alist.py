#!/usr/bin/env python


from csv import reader
from datetime import datetime

from core import AbstractScan, AbstractList


# Taken from Haystack's aformat.doc
#       = ( (FIELD_NAME, TYPE_FUNC), 
#           ...
#           )
AFIELDS = (
    ('format', int),  # >=5 implies Mk4
    ('root', str),  # 6-char lower case
    ('type', int),  # General format for fringe data
    ('fileset', int),  # Part of filename
    ('duration', int),  # Nominal duration (sec)
    ('length', int),  # Seconds of data represented.
    ('offset', int),  # Offset (sec) of mean time of data 
    ('experiment', int),  # Part of filename
    ('scan', str),  # From obsvex, blanks trimmed
    ('procdate', str),  # FRNGE/fourfit processing time
    ('year', int),  # Four-digit year.
    ('timetag', str),  # Nominal start time of data record
    ('scan_offset', int),  # Scan time to time tag (sec)
    ('source', str),  # Blank-padded ascii string
    ('baseline', str),  # 2-char baseline id 
    ('errcode', str),  # 2-char qcode and errcode
    ('band', str),  # e.g. X08 for X-band 8 freqs
    ('pol', str),  # RR, LL, RL, LR
    ('lags', int),  # Number of lags in correlation
    ('amp', float),  # In units of 1/10000
    ('snr', float),  # 4 significant digits
    ('phase_deg', float),  # Can be of various type
    ('phase_snr', float),  # 4 significant digits
    ('data_type', str  ),  # First char is data origin
    ('sbd', float),  # Microseconds
    ('mbd', float),  # Microseconds
    ('mbd_amb', float),  # Microseconds
    ('rate', float),  # Picoseconds/second
    ('ref_el', float),  # At reference epoch, degrees
    ('rem_el', float),  # At reference epoch, degrees
    ('ref_az', float),  # At reference epoch, degrees
    ('rem_az', float),  # At reference epoch, degrees
    ('u', float),  # precision 4 sig. digits
    ('v', float),  # precision 4 sig. digits
    ('ESDESP', str),  # E=ref.tape error rate exponent: 
    ('epoch', str),  # mmss 
    ('freq', float),  # Precision 10 KHz
    ('ecphase', float),  # Regardless of field 21
    ('drate', float),  # At ref epoch, microsec/sec
    ('total_mbd', float),  # At ref epoch, microsec
    ('total_sbdmbd', float),  # At ref epoch, microsec
    ('scotime', int),  # Seconds
    ('ncotime', int),  # Seconds
    )


# A list of fields to add on to the standard ones that are dependent
# on other fields, i.e. their callback functions require some previous
# field
#          = ( (SHORT_NAME, CALLBACK),
#              ...
#              )
DEP_AFIELDS = (
    ('datetime', lambda F: datetime.strptime(str(F['year'])+F['timetag'], "%y%j-%H%M%S")),
    )


class AScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {source}/{baseline} @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def _merge_scans(self, other):
        return AScan(dict(self, **other))


class AList(AbstractList):

    def __init__(self, filename, baseline, comment='*'):
        self.comment = comment
        self.filename = filename
        self.baseline = baseline
        self.repr_format = "** {name} of Experiment(s) {0.experiment_s} **"
        AbstractList.__init__(self, self._parse_baseline(self.filename, self.baseline),
                              merge=False, repr_format=self.repr_format)

    def _parse_baseline(self, filename, baseline):
        for row in reader(open(filename, 'r'), delimiter=' ', skipinitialspace=True):
            if not row[0]==self.comment:
                assert len(row)==len(AFIELDS)
                scan = AScan((field, func(row.pop(0))) for field, func in AFIELDS)
                scan.update((field, func(scan)) for field, func in DEP_AFIELDS)
                if scan.baseline==baseline:
                    yield scan
