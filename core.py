
from errors import *


class AbstractRepr:

    def __init__(self, repr_format="<{name}>", **kwargs):
        self.name = self.__class__.__name__
        self.repr_format = repr_format
        self.__dict__.update(self)

    def __repr__(self):
        return self.repr_format.format(**self.__dict__)


class AbstractScan(AbstractRepr, dict):

    def __init__(self, dict_, **kwargs):
        dict.__init__(self, dict_, **kwargs)
        AbstractRepr.__init__(self, **kwargs)

    def __eq__(self, other):
        """ inst == other -> bool
        Checks that 'self' and 'other' both have the same
        pivot variable and that their values are equal."""
        return bool(self.pivot and other.pivot) and \
               self.get(self.pivot) == other.get(other.pivot)

    def __add__(self, other):
        if self == other:
            return self.merge(other)
        else:
            raise PivotError, 'Operands do not share a pivot!'

    def merge(self, other):
        return self


class AbstractList(AbstractRepr, dict):

    def __init__(self, list_, **kwargs):
        dict.__init__(self, self._scancheck(list_), **kwargs)
        AbstractRepr.__init__(self, repr_format="[{name}]", **kwargs)
        if self.__len__() != len(list_):
            raise DataOverriddenError(list_, self)

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
