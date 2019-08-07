from __future__ import division

from i2i.util import inject_method


class Py2i(object):
    def __init__(self, **obj_kwargs):
        for k, v in obj_kwargs.items():
            setattr(self, k, v)


def mk_python_binder_from_method_funcs(method_specs, obj=None):
    """
    Inject the the methods specified by method_specs in the obj.
    Create a obj if not specified.
    If obj is a dict, use it as contructor arguments to create a Py2i binder_obj
    :param method_specs: A {method_name: method_func, ...} dict or a list of method_funcs.
    :param obj: An object to inject methods into or a dict specifying constructor arguments for a Py2i object.
    :return:
    """
    if obj is None:
        obj = {}
    if isinstance(obj, dict):
        obj = Py2i(**obj)

    if not isinstance(method_specs, dict):  # if not a dict assume it's a sequence of method_funcs
        # and make a {method_name: method_func, ...} dict from it
        method_specs = {method_func.__name__: method_func for method_func in method_specs}

    for method_name, method_func in method_specs.items():
        assert callable(method_func), "Your method_func (values of method_specs) needs to be a callable"
        inject_method(obj, method_func, method_name)

    return obj


