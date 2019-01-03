from __future__ import division

import inspect
import types
from functools import wraps

function_type = type(lambda x: x)  # using this instead of callable() because classes are callable, for instance


class NoDefault(object):
    def __repr__(self):
        return 'no_default'


no_default = NoDefault()


def arg_dflt_dict_of_callable(f):
    """
    Get a {arg_name: default_val, ...} dict from a callable.
    See also :py:mint_of_callable:
    :param f: A callable (function, method, ...)
    :return:
    """
    argspec = inspect.getfullargspec(f)
    args = argspec.args or []
    defaults = argspec.defaults or []
    return {arg: dflt for arg, dflt in zip(args, [no_default] * (len(args) - len(defaults)) + list(defaults))}


def inject_method(self, method_function, method_name=None):
    if isinstance(method_function, function_type):
        if method_name is None:
            method_name = method_function.__name__
        setattr(self,
                method_name,
                types.MethodType(method_function, self))
    else:
        if isinstance(method_function, dict):
            method_function = [(func, func_name) for func_name, func in method_function.items()]
        for method in method_function:
            if isinstance(method, tuple) and len(method) == 2:
                self = inject_method(self, method[0], method[1])
            else:
                self = inject_method(self, method)

    return self


def add_self_as_first_argument(func):
    @wraps(func)
    def wrapped_func(self, *args, **kwargs):
        return func(*args, **kwargs)

    return wrapped_func


def add_cls_as_first_argument(func):
    @wraps(func)
    def wrapped_func(cls, *args, **kwargs):
        return func(*args, **kwargs)

    return wrapped_func


def infer_if_function_might_be_intended_as_a_classmethod_or_staticmethod(func):
    """
    Tries to infer if the input function is a 'classmethod' or 'staticmethod' (or just 'normal')
    When is that? When:
    * the function's first argument is called 'cls' and has no default: 'classmethod'
    * the function's first argument is called 'self' and has no default: 'staticmethod'
    * otherwise: 'normal'

    >>> def a_normal_func(x, y=None):
    ...     pass
    >>> def a_func_that_is_probably_a_classmethod(cls, y=None):
    ...     pass
    >>> def a_func_that_is_probably_a_staticmethod(self, y=None):
    ...     pass
    >>> def a_func_that_is_probably_a_classmethod_but_is_not(cls=3, y=None):
    ...     pass
    >>> def a_func_that_is_probably_a_staticmethod_but_is_not(self=None, y=None):
    ...     pass
    >>> list_of_functions = [
    ...     a_normal_func,
    ...     a_func_that_is_probably_a_classmethod,
    ...     a_func_that_is_probably_a_staticmethod,
    ...     a_func_that_is_probably_a_classmethod_but_is_not,
    ...     a_func_that_is_probably_a_staticmethod_but_is_not,
    ... ]
    >>>
    >>> for func in list_of_functions:
    ...     print("{}: {}".format(func.__name__,
    ...                           infer_if_function_might_be_intended_as_a_classmethod_or_staticmethod(func)))
    ...
    a_normal_func: normal
    a_func_that_is_probably_a_classmethod: classmethod
    a_func_that_is_probably_a_staticmethod: staticmethod
    a_func_that_is_probably_a_classmethod_but_is_not: normal_with_cls
    a_func_that_is_probably_a_staticmethod_but_is_not: normal_with_self
    """
    argsspec = inspect.getfullargspec(func)
    if len(argsspec.args) > 0:
        first_element_has_no_defaults = bool(len(argsspec.args) > len(argsspec.defaults))
        if argsspec.args[0] == 'cls':
            if first_element_has_no_defaults:
                return 'classmethod'
            else:
                return 'normal_with_cls'
        elif argsspec.args[0] == 'self':
            if first_element_has_no_defaults:
                return 'staticmethod'
            else:
                return 'normal_with_self'
    return 'normal'


def decorate_as_staticmethod_or_classmethod_if_needed(func):
    type_of_func = infer_if_function_might_be_intended_as_a_classmethod_or_staticmethod(func)
    if type_of_func == 'classmethod':
        return classmethod(func)
    elif type_of_func == 'staticmethod':
        return staticmethod(func)
    elif type_of_func == 'normal':
        return func


if __name__ == '__main__':
    import os
    import re

    key_file_re = re.compile('setup.py')


    def dir_is_a_pip_installable_dir(dirpath):
        return any(filter(key_file_re.match, os.listdir(dirpath)))


    rootdir = '/D/Dropbox/dev/py/proj'
    cumul = list()
    for f in filter(lambda x: not x.startswith('.'), os.listdir(rootdir)):
        filepath = os.path.join(rootdir, f)
        if os.path.isdir(filepath):
            if dir_is_a_pip_installable_dir(filepath):
                cumul.append(filepath)

    for f in cumul:
        print(f)
