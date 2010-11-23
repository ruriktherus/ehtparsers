
class Error(Exception):

    def __init__(self, msg, **kwargs):
        Exception.__init__(self, msg.format(**kwargs))


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


class DataOverriddenError(Error):

    def __init__(self, input_list, output_list):
        msg = """ {dict.name}:
        Scan list has length {list_len} but resulting '{dict.name}'
        has length {dict_len}. Scans have overlapping pivots and data may
        have been lost!"""
        Error.__init__(self, msg, list_len=len(input_list),
                       dict_len=len(output_list), dict=output_list)
