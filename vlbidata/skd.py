#!/usr/bin/env python


from re import finditer, X, M
from datetime import datetime, timedelta

from core import AbstractScan, AbstractList


__all__ = [
    'SKDScan',
    'SKDList',
    'parse_skd',
    ]


SCAN_RE = r"""scan\ (?P<scan_spec>\w+);[\r\n]+     # scan specifier
              \*.+[\r\n]+\*\ +(?P<pant>[1-8]*)     # get the PA antenna
              (?P<conf>[dDfFwWaApP]*)              # get the configuration
              \(x\)(?P<comp>[0-9]).*[\r\n]+        # get the comparison antenna
              \ +start=(?P<time>\w+);              # start time
              \ mode=(?P<mode>\w+);                # freq. def used
              \ source=(?P<source>.*);[\r\n]+      # source name
              (?:\*.+[\r\n]+)?                     # skip comment (if present)
              \ +station=(?P<station>.+);[\r\n]+   # grab the first station line
              (?:^.+;[\r\n]+)+?                    # skip the rest
              endscan;[\r\n]+"""


DEP_SKDFIELDS = (
    ('pant', lambda F: ''.join(a for a in F['pant'] if a not in F['ignore'])),
    ('pants', lambda F: [int(a) for a in F['pant']]),
    ('total_pants', lambda F: len(F['pants'])),           # Total number of phased antennas
    ('comparison', lambda F: int(F['comp'][0])),          # Comparison antenna (if recorded)
    ('configuration', lambda F: list(F['conf'].upper())), # Phased array configuration
    ('duration', lambda F: timedelta(seconds=int(F['station'].split(':')[2].rstrip('sec')))),
    ('datetime', lambda F: datetime.strptime(F['time'], '%Yy%jd%Hh%Mm%Ss')),
    ('time', lambda F: datetime.strftime(F['datetime'], '%H:%M:%S')),
    )


class SKDScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {source}({total_pants} pants) @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def _merge_scans(self, other):
        return SKDScan(dict(self, **other))


class SKDList(AbstractList):

    def __init__(self, iter_):
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, iter_, merge=False, repr_format=self.repr_format)

    def _list_from_scans(self, iter_):
        return SKDList(iter_)


def parse_skdfile(filename, ignore_pants):
    with open(filename, 'r') as file_:
        for match in finditer(SCAN_RE, file_.read(), X|M):
            scan = SKDScan(match.groupdict())
            scan['ignore'] = ignore_pants
            scan.update((field, func(scan)) for field, func in DEP_SKDFIELDS)
            yield scan


def parse_skd(filename, ignore_pants=''):
    return SKDList(parse_skdfile(filename, ignore_pants=ignore_pants))
