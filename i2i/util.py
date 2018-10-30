from __future__ import division

import types
import inspect

function_type = type(lambda x: x)  # using this instead of callable() because classes are callable, for instance


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
    a_func_that_is_probably_a_classmethod_but_is_not: normal
    a_func_that_is_probably_a_staticmethod_but_is_not: normal
    """
    argsspec = inspect.getargspec(func)
    if len(argsspec.args) > 0:
        first_element_has_no_defaults = bool(len(argsspec.args) > len(argsspec.defaults))
        if argsspec.args[0] == 'cls' and first_element_has_no_defaults:
            return 'classmethod'
        elif argsspec.args[0] == 'self' and first_element_has_no_defaults:
            return 'staticmethod'
    return 'normal'


def decorate_as_staticmethod_or_classmethod(func):
    pass


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

