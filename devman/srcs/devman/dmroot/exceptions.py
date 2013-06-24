#!/usr/bin/python

class DMException(Exception):
    pass

class DMIOError(DMException):
    pass

class DMIDError(DMException):
    pass

class DMUnsupportedError(DMException):
    pass

class DMJsonDescMissedError(DMException):
    pass

class DMJsonDescError(DMException):
    pass

class DMEntityError(DMException):
    pass

class DMTextFormatError(DMException):
    pass

class DMPermissionError(DMException):
    pass

class DMParamError(DMException):
    pass

class DMNotLoginError(DMException):
    pass

class DMInvalidUserError(DMException):
    pass

class DMDataBaseError(DMException):
    pass

class DMFormError(DMException):
    pass

class DMValueError(DMException):
    pass

class DMURLError(DMException):
    pass
