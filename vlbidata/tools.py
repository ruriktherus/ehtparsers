
from csv import DictWriter


__all__ = [
    'filter',
    'print_table',
]


def filter(list_, expression=None, **conditions):
    return list_.__filter__(expression=expression, **conditions)


def print_table(list_, output_filename, keys=None, **kwargs):
    if keys==None:
        keys = list_[0].iterkeys()
    writer = DictWriter(open(output_filename, 'w'), keys, extrasaction='ignore', **kwargs)
    writer.writerows(list_.itervalues())
