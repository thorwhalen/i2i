from __future__ import division

import inspect

from i2i.util import no_default

NO_NAME = '_no_name'


def name_of_obj(o):
    if hasattr(o, '__name__'):
        return o.__name__
    elif hasattr(o, '__class__'):
        return name_of_obj(o.__class__)
    else:
        return NO_NAME


# TODO: Expand so that user can specify what to include in the mint
def mint_of_callable(f):
    """
    Get meta-data about a callable.
    :param f: A callable (function, method, ...)
    :return: A dict containing information about the interface of f, that is, name, module, doc, and input and output
    information.
    """
    mint = {
        'name': name_of_obj(f),  # TODO: Better NO_NAME or just not the name field?
        'module': f.__module__,
        'doc': inspect.getdoc(f)
    }

    argspec = inspect.getfullargspec(f)
    annotations = argspec.annotations
    input_specs = {}
    args = argspec.args or []
    defaults = argspec.defaults or []
    for arg_name, dflt in zip(args, [no_default] * (len(args) - len(defaults)) + list(defaults)):
        input_specs[arg_name] = {}
        if dflt is not no_default:
            input_specs[arg_name]['default'] = dflt
        if arg_name in annotations:
            input_specs[arg_name]['type'] = annotations[arg_name]

    mint['input'] = input_specs

    if 'return' in annotations:
        mint['output'] = {'type': annotations['return']}

    return mint
