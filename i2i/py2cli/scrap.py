from __future__ import division

from itertools import zip_longest
import inspect



def subparser_for_func(funcname, func, subparser_handle):
    #print "adding handler for", funcname
    argspec = inspect.getargspec(func)
    func_parser = subparser_handle.add_parser(func.__name__, help=inspect.getdoc(func))
    for arg, dflt in zip_longest((argspec.args or [])[::-1], (argspec.defaults or [])[::-1], fillvalue=None):
        if dflt:
            func_parser.add_argument("--" + arg, nargs='?', default=dflt)
        else:
            func_parser.add_argument("--" + arg)