""" Provides general utility functions """
from __future__ import print_function
import sys


def eprint(*args, **kwargs):
    """ Prints to stderr """
    print(*args, file=sys.stderr, **kwargs)
