#-*- coding: UTF-8 -*-

"""
Exceptions for copr-cli
"""


class CoprException(Exception):

    """ Basic exception class for copr-cli. """
    pass


class CoprNoConfException(CoprException):

    """ Exception thrown when no config file is found. """
    pass


class CoprConfigException(CoprException):

    """ Exception thrown when the config file is incomplete or
    malformed.
    """
    pass


class CoprRequestException(Exception):
    """ Exception thrown when the request is bad. For example,
    the user provided wrong project name or build ID. 
    """
    pass


class CoprBuildException(Exception):
    """ Exception thrown when one or more builds fail and Cli is waiting
    for the result.
    """
    pass


class CoprUnknownResponseException(Exception):
    """ Exception thrown when the response is unknown to cli.
    It usualy means that something is broken.
    """
    pass
