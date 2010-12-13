#!/usr/bin/env python


from re import compile
from datetime import datetime

from vlbidata.core import AbstractScan, AbstractList
from vlbidata.errors import ConflictingValuesError


__all__ = [
    'SMTOTsysScan',
    'SMTOTsysList',
    'parse_smto',
    ]


TSYS_RE = compile('TSYS\s+(?P<utctime>[0-9]{3}:[0-9]{2}:[0-9]{2})\s+'
                  '(?P<tsys_smto1>[0-9]+)\s+'
                  '(?P<tsys_smto2>[0-9]+)\s+'
                  '(?P<tsys_smto3>[0-9]+)\s+'
                  '(?P<tsys_smto4>[0-9]+)\s+'
                  'VLBI scan\s+(?P<smto_scan>[0-9]+)')


class SMTOTsysScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {name} @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def _merge_scans(self, other):
        return SMTOTsysScan(dict(self, **other))

    def merge(self, other):
        try:
            return AbstractScan.merge(self, other)
        except ConflictingValuesError:
            self.logger.warning('** attempt to merge duplicate Tsys value!')
            return AbstractScan.merge(self, self)


class SMTOTsysList(AbstractList):

    def __init__(self, iter_):
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, iter_, merge=True, repr_format=self.repr_format)

    def _list_from_scans(self, iter_):
        return SMTOTsysList(iter_)

    def _interpolate_scan(self, pivot):
        closest = AbstractList._interpolate_scan(self, pivot)
        return SMTOTsysScan(dict(closest, datetime=pivot))


def parse_smtofile(filename, year):
    with open(filename, 'r') as file_:
        for line in file_:
            match = TSYS_RE.match(line)
            if match:
                scan = SMTOTsysScan(match.groupdict())
                dt = datetime.strptime(str(year)+scan['utctime'], '%Y%j:%H:%M')
                scan.update({'datetime': dt})
                yield scan


def parse_smto(filename, year):
    return SMTOTsysList(parse_smtofile(filename, year))
