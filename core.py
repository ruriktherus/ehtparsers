

class PivotError(Exception):
    pass


class AbstractScan(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.name = self.__class__.__name__
        self.repr_format = "<{name}({pivot})>"
        self.__dict__.update(self)

    def __repr__(self):
        return self.repr_format.format(**self.__dict__)

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
