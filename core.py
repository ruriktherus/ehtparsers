
from errors import *


class AbstractRepr:

    def __init__(self, repr_format="<{name}>"):
        self.name = self.__class__.__name__
        self.repr_format = repr_format

    def __repr__(self):
        repr_dict = dict(self.__dict__, **self)
        return self.repr_format.format(**repr_dict)


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
            return AbstractScan(dict(self, **other), pivot=self.pivot,
                                repr_format=self.repr_format)
        else:
            raise DifferentScansError(self, other)


class AbstractList(AbstractRepr, dict):

    def __init__(self, list_):
        dict.__init__(self, self._scancheck(list_))
        AbstractRepr.__init__(self, repr_format="[{name}]")
        if self.__len__() != len(list_):
            raise DataOverriddenError(list_, self)

    def __iter__(self):
        for key in sorted(dict.keys(self)):
            yield key

    def __getitem__(self, key):
        if isinstance(key, int):
            pivot = self.keys()[key]
        else:
            pivot = key
        return dict.__getitem__(self, pivot)

    def __getattr_iter__(self, attr):
        for value in self.itervalues():
            yield getattr(value, attr)

    def __getattr__(self, attr):
        return list(self.__getattr_iter__(attr))

    def _scancheck(self, list_):
        """ dict = inst._merge_list(list_)
        This function produces a dictionary where the keys
        are the pivot variables and the values are the scan
        instances of the given list of scans."""
        for index, entry in enumerate(list_):
            if index==0:
                pivot = entry.pivot
            if not isinstance(entry, AbstractScan):
                raise ImproperScanError(index, entry)
            if not hasattr(entry, 'pivot'):
                raise NoPivotError(index, entry)
            if not hasattr(entry, entry.pivot):
                raise PivotNotFoundError(index, entry, pivot)
            if entry.pivot != pivot:
                raise InconsistentPivotError(index, entry, pivot)
            yield entry[pivot], entry

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
