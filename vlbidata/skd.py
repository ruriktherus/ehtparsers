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
              (?:\*.+[\r\n]+)?                     # skip comment (if present)
              ((?:\*.+)                            #
               (?P<pol>[LR]pol)                    # get pol. state (if present)
               (?:[\r\n]+))?                       #
              \ +start=(?P<time>\w+);              # start time
              \ mode=(?P<mode>\w+);                # freq. def used
              \ source=(?P<source>.*);[\r\n]+      # source name
              (?:\*.+[\r\n]+)?                     # skip comment (if present)
              \ +station=(?P<station>.+);[\r\n]+   # grab the first station line
              (?:^.+;[\r\n]+)+?                    # skip the rest
              endscan;[\r\n]+"""


DEP_SKDFIELDS = (
    ('duration', lambda F: timedelta(seconds=int(F['station'].split(':')[2].rstrip('sec')))),
    ('datetime', lambda F: datetime.strptime(F['time'], '%Yy%jd%Hh%Mm%Ss')),
    ('time', lambda F: datetime.strftime(F['datetime'], '%H:%M:%S')),
    ('n', lambda F: int(F['scan_spec'][2:])),
    )


class SKDScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {source} @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def _merge_scans(self, other):
        return SKDScan(dict(self, **other))


class SKDList(AbstractList):

    def __init__(self, iter_):
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, iter_, merge=False, repr_format=self.repr_format)

    def _list_from_scans(self, iter_):
        return SKDList(iter_)


def parse_skdfile(filename):
    with open(filename, 'r') as file_:
        for match in finditer(SCAN_RE, file_.read(), X|M):
            scan = SKDScan(match.groupdict())
            scan.update((field, func(scan)) for field, func in DEP_SKDFIELDS)
            yield scan


def parse_skd(filename):
    return SKDList(parse_skdfile(filename))
