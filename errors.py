
class Error(Exception):

    def __init__(self, msg, **kwargs):
        Exception.__init__(self, msg.format(**kwargs))


class AbstractTypeError(Error):

    def __init__(self, object_name):
        Error.__init__(self, "'{object_name}' does not support item assignment",
                       object_name=object_name)


class PivotError(Error):

    def __init__(self, msg, **kwargs):
        Error.__init__(self, msg, **kwargs)

class NoPivotError(PivotError):

    def __init__(self, index, scan):
        PivotError.__init__(self, "entry #{index}, '{scan}', has no pivot field!",
                            index=index, scan=scan)

class InconsistentPivotError(PivotError):

    def __init__(self, index, scan, pivot):
        PivotError.__init__(self, "entry #{index}, '{scan}', has inconsistent pivot '{pivot}'!",
                            index=index, scan=scan, pivot=pivot)

class PivotNotFoundError(PivotError):

    def __init__(self, index, scan, pivot):
        PivotError.__init__(self, "pivot '{pivot}' not found for entry #{index}, '{scan}'!",
                            index=index, scan=scan, pivot=pivot)


class AbstractScanError(Error):

    def __init__(self, msg, **kwargs):
        Error.__init__(self, msg, **kwargs)

class ImproperScanError(AbstractScanError):

    def __init__(self, index, scan):
        AbstractScanError.__init__(self, "entry #{index}, '{scan}', is not a proper scan object!",
                                   index=index, scan=scan)

class FieldNotFoundError(AbstractScanError):

    def __init__(self, scan, field):
        AbstractScanError.__init__(self, "entry '{scan}' lacks a value for '{field}'",
                                   scan=scan, field=field)

class AttributeCannotBeSetError(AbstractScanError, AttributeError):

    def __init__(self, attr):
        AbstractScanError.__init__(self, "attribute '{attr}' cannot be set, it would mask "
                                   "a field of the same name!", attr=attr)


class CannotMergeError(AbstractScanError):

    def __init__(self, msg, **kwargs):
        AbstractScanError.__init__(self, msg, **kwargs)

class DifferentScansError(CannotMergeError):

    def __init__(self, scana, scanb):
        CannotMergeError.__init__(self, "scans '{scana}' and '{scanb}' cannot be merged, "
                                  "check that they share a pivot!", scana=scana, scanb=scanb)

class ConflictingValuesError(CannotMergeError):

    def __init__(self, scana, scanb, field):
        CannotMergeError.__init__(self, "scans '{scana}' and '{scanb}' have different "
                                  "values for '{field}'!", scana=scana, scanb=scanb,
                                  field=field)


class DataOverriddenError(Error):

    def __init__(self, scan, pivot):
        Error.__init__(self, "scan '{scan}' would override another scan at {pivot}!",
                       scan=scan, pivot=pivot)
