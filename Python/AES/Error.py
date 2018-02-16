from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from future import standard_library

standard_library.install_aliases()

# From https://docs.python.org/3/tutorial/errors.html


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message


# My classes start here


class IncompatibleMatrixError(Error):

    def __init__(self, message):
        self.message = message

if __name__ == '__main__':
    pass
