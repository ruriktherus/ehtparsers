#!/usr/bin/env python


from re import finditer, X, M
from datetime import datetime

from core import AbstractScan, AbstractList


__all__ = [
    'SKDScan',
    'SKDList',
    ]


SCAN_RE = r"""scan\ (?P<scan_spec>\w+);\n     # scan specifier
              \*.+\n\*\ +(?P<pant>[1-8]*)     # get the PA antenna
              (?P<conf>[dDfFwWaApP]*)         # get the configuration
              \(x\)(?P<comp>[0-9]).+\n        # get the comparison antenna
              \ +start=(?P<time>\w+);         # start time
              \ mode=(?P<mode>\w+);           # freq. def used
              \ source=(?P<source>.+);\n      # source name
              (?:\*.+\n)?(?:^.+;\n){0,3}      # skips two (or three) lines
              endscan;$"""


DEP_SKDFIELDS = (
    ('pants', lambda F: [int(a) for a in F['pant']]),     # List of phased antennas in the sum
    ('total_pants', lambda F: len(F['pants'])),           # Total number of phased antennas
    ('comparison', lambda F: int(F['comp'][0])),          # Comparison antenna (if recorded)
    ('configuration', lambda F: list(F['conf'].upper())), # Phased array configuration
    ('datetime', lambda F: datetime.strptime(F['time'], '%Yy%jd%Hh%Mm%Ss')),
    )


class SKDScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {source}({total_pants} pants) @ {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)

    def _merge_scans(self, other):
        return SKDScan(dict(self, **other))


class SKDList(AbstractList):

    def __init__(self, filename):
        self.filename = filename
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, self._parse_skd(self.filename), merge=False,
                              repr_format=self.repr_format)

    def _parse_skd(self, filename):
        with open(filename, 'r') as file_:
            for match in finditer(SCAN_RE, file_.read(), X|M):
                scan = SKDScan(match.groupdict())
                scan.update((field, func(scan)) for field, func in DEP_SKDFIELDS)
                yield scan
