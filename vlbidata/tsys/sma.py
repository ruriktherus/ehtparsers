#!/usr/bin/env python


from re import compile
from datetime import datetime
from warnings import warn_explicit

from vlbidata.core import AbstractScan, AbstractList
from vlbidata.errors import ConflictingValuesError


__all__ = [
    'SMATsysScan',
    'SMATsysList',
    ]


ACC_RE = compile('#\s.+ACC(?P<ant>[0-9]{1,2})')


class SMATsysScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {name} @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def _merge_scans(self, other):
        return SMATsysScan(dict(self, **other))

    def merge(self, other):
        try:
            return AbstractScan.merge(self, other)
        except ConflictingValuesError:
            self.logger.warning('** attempt to merge duplicate Tsys value!')
            return AbstractScan.merge(self, self)


class SMATsysList(AbstractList):

    def __init__(self, filename):
        self.filename = filename
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, self._parse_tsys(self.filename), merge=True,
                              repr_format=self.repr_format)

    def _parse_tsys(self, filename):
        with open(filename, 'r') as file_:
            for line in file_:
                if line.startswith('#'):
                    match = ACC_RE.match(line)
                    if match:
                        antenna = match.groupdict()['ant']
                else:
                    columns = line.split()
                    if columns:
                        tsys = float(columns[-1])
                        dt = datetime.utcfromtimestamp(int(columns[0]))
                        yield SMATsysScan({'datetime': dt, 'tsys_sma%s'%antenna: tsys})

    def _interpolate_scan(self, pivot):
        closest = AbstractList._interpolate_scan(self, pivot)
        return SMATsysScan(dict(closest, datetime=pivot))
