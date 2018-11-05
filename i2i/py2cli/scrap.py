from __future__ import division

import argparse
import sys
from itertools import zip_longest
import inspect


# TODO: Separate mint
# TODO: Make minting use a whitelist (inclusion list)

class NoDefault(object):
    pass


no_default = NoDefault()


def subparser_for_func(func, subparser_handle, func_name=None):
    """

    :param func: function object
    :param subparser_handle:
    :param func_name: function name

    :return:
    """
    if func_name is None:
        func_name = func.__name__

    argspec = inspect.getfullargspec(func)
    func_parser = subparser_handle.add_parser(func_name, help=inspect.getdoc(func))
    func_parser.set_defaults(which=func_name)
    for arg, dflt in zip_longest((argspec.args or [])[::-1], (argspec.defaults or [])[::-1],
                                 fillvalue=no_default):
        # TODO: Figure out how to know for sure if we have a method or class method
        if arg == "self" or arg == "cls":  # TODO: Not completely safe. Make safer. See i2i.util
            pass
        elif dflt is no_default:
            func_parser.add_argument("--" + arg)
        else:
            func_parser.add_argument("--" + arg, default=dflt)


def is_method_or_function(o):
    return inspect.ismethod(o) or inspect.isfunction(o)


def parser_for_class(o):
    parser = argparse.ArgumentParser()
    subparser_handle = parser.add_subparsers()
    info = inspect.getmembers(o, predicate=is_method_or_function)
    for func_name, func in info:
        print(func_name)
        subparser_for_func(func, subparser_handle=subparser_handle, func_name=func_name)
    return parser


def py2cli_test(cls, input_string):
    sys.argv = input_string.split(' ')
    parser = parser_for_class(cls)
    cl_in = parser.parse_args()
    # print(cl_in)
    func = getattr(cls, cl_in.which)
    del cl_in.which
    return func(**vars(cl_in))

# TODO: Need for dict filters for arguments of functions
