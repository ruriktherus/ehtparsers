#!/usr/bin/env python


from re import match, compile
from datetime import datetime
from warnings import warn_explicit

from vlbidata.core import AbstractScan, AbstractList
from vlbidata.errors import FieldNotFoundError, ConflictingValuesError


__all__ = [
    'SMATsysScan',
    'SMATsysList',
    'parse_sma',
    ]


ACC_RE = compile('#\s.+ACC(?P<ant>[0-9]{1,2})')


class SMATsysScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {name} @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def __getattr__(self, attr):
        try:
            return AbstractScan.__getattr__(self, attr)
        except FieldNotFoundError:
            if match('tsys_sma[0-9]+', str(attr)):
                self.logger.warning("'%s' not found, returning None", attr)
                return None
            else:
                raise FieldNotFoundError(self, attr)

    def _merge_scans(self, other):
        return SMATsysScan(dict(self, **other))

    def merge(self, other):
        try:
            return AbstractScan.merge(self, other)
        except ConflictingValuesError:
            self.logger.warning('** attempt to merge duplicate Tsys value!')
            return AbstractScan.merge(self, self)


class SMATsysList(AbstractList):

    def __init__(self, iter_):
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, iter_, merge=True, repr_format=self.repr_format)

    def _list_from_scans(self, iter_):
        SMATsysList(iter_, merge=True, repr_format=self.repr_format)

    def _interpolate_attr(self, pivot, attr):
        last_key = self.__iter__().next()
        last_value = self[last_key]
        for key, value in self.iteritems():
            if value.__getattr__(attr):
                if pivot>key and pivot>last_key:
                    last_key = key
                    last_value = value
                elif abs(pivot-last_key) <= abs(pivot-key):
                    closest = self.__getitem__(last_key)
                    return SMATsysScan({'datetime': pivot, attr: closest[attr]})
                elif abs(pivot-last_key) > abs(pivot-key):
                    closest = self.__getitem__(key)
                    return SMATsysScan({'datetime': pivot, attr: closest[attr]})
        closest = self.__getitem__(key)
        if closest.has_key(attr):
            return SMATsysScan({'datetime': pivot, attr: closest[attr]})
        else:
            return SMATsysScan({'datetime': pivot, attr: None})

    def _interpolate_scan(self, pivot):
        required = iter('tsys_sma%s'%a for a in range(1,9))
        scans = [self._interpolate_attr(pivot, tsys) for tsys in required]
        return sum(scans, SMATsysScan({'datetime': pivot}))


def parse_smafile(filename):
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


def parse_sma(filename):
    return SMATsysList(parse_smafile(filename))
