#!/usr/bin/env python


from json import load
from re import finditer, X, M
from datetime import datetime, timedelta

from core import AbstractScan, AbstractList


__all__ = [
    'SwarmCalScan',
    'SwarmCalList',
    'parse_swarmcal',
    ]


DEP_SWARMCALFIELDS = (
    ('duration', lambda F: timedelta(seconds=float(F['int_length']))),
    ('datetime', lambda F: datetime.utcfromtimestamp(F['int_time']) - F['duration']),
    ('time', lambda F: datetime.strftime(F['datetime'], '%H:%M:%S')),
    )


class SwarmCalScan(AbstractScan):

    def __init__(self, dict_):
        self.repr_format = "< {datetime} >"
        AbstractScan.__init__(self, dict_, pivot='datetime', repr_format=self.repr_format)


class SwarmCalList(AbstractList):

    def __init__(self, iter_):
        self.repr_format = "** {name} of {0.length} scans **"
        AbstractList.__init__(self, iter_, merge=False, repr_format=self.repr_format)

    def _list_from_scans(self, iter_):
        return SwarmCalList(iter_)


def parse_swarmcalfile(filename):
    with open(filename, 'r') as file_:
        for entry in load(file_):
            scan = SwarmCalScan(entry)
            scan.update((field, func(scan)) for field, func in DEP_SWARMCALFIELDS)
            yield scan


def parse_swarmcal(filename):
    return SwarmCalList(parse_swarmcalfile(filename))
