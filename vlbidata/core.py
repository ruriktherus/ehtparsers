
import logging
from errors import *


__all__ = [ 
    'AbstractRepr',
    'AbstractScan',
    'AbstractList',
    ]


class AbstractRepr:

    def __init__(self, repr_format="<{name}>"):
        self.module = self.__module__
        self.name = self.__class__.__name__
        self.log_name = '{module}.{name}'.format(**self.__dict__)
        self.logger = logging.getLogger(self.log_name)
        self.repr_format = repr_format

    def __repr__(self, extra=None, quit=False):
        repr_dict = dict(self.__dict__, **self)
        repr_dict[extra] = '$$$'
        try:
            return self.repr_format.format(self, **repr_dict)
        except KeyError, e:
            key = e.args[0]
            return AbstractRepr.__repr__(self, extra=key, quit=True)


class AbstractScan(AbstractRepr, dict):

    def __init__(self, dict_, pivot, repr_format="<{name}>"):
        self.pivot = pivot
        dict.__init__(self, dict_)
        AbstractRepr.__init__(self, repr_format=repr_format)

    def __getattr__(self, attr):
        try:
            return dict.__getitem__(self, attr)
        except KeyError:
            raise FieldNotFoundError(self, attr)

    def __setattr__(self, attr, value):
        if not dict.has_key(self, attr):
            dict.__setattr__(self, attr, value)
        else:
            raise AttributeCannotBeSetError(attr)

    def __eq__(self, other):
        """ inst == other -> bool
        Checks that 'self' and 'other' both have the same
        pivot variable and that their values are equal."""
        return bool(self.pivot and other.pivot) and \
               self.get(self.pivot) == other.get(other.pivot)

    def __add__(self, other):
        return self.merge(other)

    def _merge_scans(self, other):
        return AbstractScan(dict(self, **other), pivot=self.pivot,
                            repr_format=self.repr_format)

    def merge(self, other):
        """ inst.merge(other) -> new_inst
        Attempts to merge two scans that have the same
        pivot value (generally scans occurring at the same
        time. This involves comparing all shared fields and
        raising errors on conflicts. """ 
        if self == other:
            for field, value in other.iteritems():
                if dict.has_key(self, field) and \
                       dict.__getitem__(self, field) != value:
                    raise ConflictingValuesError(self, other, field)
            return self._merge_scans(other)
        else:
            raise DifferentScansError(self, other)


class AbstractList(AbstractRepr, dict):

    def __init__(self, iter_, merge=False, repr_format="[{name}({0.length})]"):
        dict.__init__(self, self._scancheck(iter_, merge))
        AbstractRepr.__init__(self, repr_format=repr_format)

    def __iter__(self):
        for key in sorted(dict.keys(self)):
            yield key

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self.values()[key]
        else:
            return dict.__getitem__(self, key)

    def __setitem__(self, *args):
        raise AbstractTypeError(self.name)

    def __getattr_iter__(self, attr):
        for value in self.itervalues():
            yield getattr(value, attr)

    def __getattr__(self, attr):
        if attr=='length':
            return dict.__len__(self)
        elif attr.endswith('_s'):
            return set(self.__getattr__(attr.rstrip('_s')))
        elif attr.endswith('_sl'):
            return list(self.__getattr__(attr.rstrip('l')))
        elif attr.endswith('_sj'):
            return '/'.join(self.__getattr__(attr.rstrip('j')))
        else:
            return list(self.__getattr_iter__(attr))

    def __call__(self, approx):
        return self._interpolate_scan(approx)

    def __add__(self, other):
        return self._merge_lists(other)

    def __filter__(self, scans=None, **conditions):
        if scans==None:
            scans = self.itervalues()
        try:
            field, condition = conditions.popitem()
            scans = [scan for scan in self.itervalues() if scan[field]==condition]
            return self.__filter__(scans, **conditions)
        except KeyError:
            return self._list_from_scans(scans)
        
    def _list_from_scans(self, scans):
        return AbstractList(scans, merge=False, repr_format=self.repr_format)

    def _interpolate_scan(self, pivot):
        last_key = self.__iter__().next()
        for key in self.__iter__():
            if pivot>key and pivot>last_key:
                last_key = key
            elif abs(pivot-last_key) <= abs(pivot-key):
                return self.__getitem__(last_key)
            elif abs(pivot-last_key) > abs(pivot-key):
                return self.__getitem__(key)
        return self.__getitem__(key)

    def _merge_lists(self, other):
        return self._list_from_scans(self[key]+other(key) for key in self)

    def _scancheck(self, iter_, merge):
        """ dict = inst._merge_list(iter_)
        This function produces a dictionary where the keys
        are the pivot variables and the values are the scan
        instances of the given list of scans."""
        for index, entry in enumerate(iter_):
            if index==0:
                self.pivot = entry.pivot
            if not isinstance(entry, AbstractScan):
                raise ImproperScanError(index, entry)
            if not hasattr(entry, 'pivot'):
                raise NoPivotError(index, entry)
            if not hasattr(entry, entry.pivot):
                raise PivotNotFoundError(index, entry, entry.pivot)
            if entry.pivot != self.pivot:
                raise InconsistentPivotError(index, entry, self.pivot)
            pivot = entry[self.pivot]
            if dict.has_key(self, pivot):
                if merge:
                    dict.__setitem__(self, pivot, self[pivot]+entry)
                else:
                    raise DataOverriddenError(entry, pivot)
            else:
                yield pivot, entry

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default

    def iterkeys(self):
        for key in self.__iter__():
            yield key

    def itervalues(self):
        for key in self.__iter__():
            value = dict.__getitem__(self, key)
            yield value

    def iteritems(self):
        for key in self.__iter__():
            value = dict.__getitem__(self, key)
            yield key, value

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def popitem(self):
        first = self.__iter__().next()
        return dict.pop(self, first)

    def update(self, iter_, merge=True):
        dict.update(self, self._scancheck(iter_, merge))
