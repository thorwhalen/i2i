from __future__ import division

from i2i.util import inject_method
from requests import request
from i2i.util import imdict

DFLT_PORT = 5000
DFLT_BASE_URL = 'http://localhost:{port}'.format(port=DFLT_PORT)
DFLT_REQUEST_KWARGS = imdict({'method': 'GET', 'url': ''})


def mk_default_completion_validator(dflt_kwargs=DFLT_REQUEST_KWARGS):
    def default_completion_validator(kwargs):
        return dict(dflt_kwargs, **kwargs)

    return default_completion_validator


def all_necessary_fields_validator(kwargs):
    assert 'method' in kwargs and 'url' in kwargs, "Need both a method and a url field!"
    return kwargs


def mk_request_function(method_spec):
    # defaults
    method_spec['request_kwargs'] = method_spec.get('request_kwargs', {})
    method_spec['request_kwargs']['method'] = method_spec['request_kwargs'].get('method', 'GET')

    def request_func(self, **kwargs):

        # convert argument types TODO: Not efficient. Might could be revised.
        for arg_name, converter in method_spec.get('input_trans', {}).items():
            if arg_name in kwargs:
                kwargs[arg_name] = converter(kwargs[arg_name])

        json_data = {}
        for arg_name in method_spec.get('json_arg_names', []):
            if arg_name in kwargs:
                json_data[arg_name] = kwargs.pop(arg_name)

        if 'url_template' in method_spec:
            request_kwargs = dict(method_spec['request_kwargs'],
                                  url=method_spec['url_template'].format(**kwargs))
        else:
            request_kwargs = method_spec['request_kwargs']

        if json_data:
            request_kwargs = dict(request_kwargs, json=json_data)

        r = request(**request_kwargs)
        if 'output_trans' in method_spec:
            r = method_spec['output_trans'](r)
        return r

    return request_func


DFLT_METHOD_FUNC_FROM_METHOD_SPEC = mk_request_function


class Py2Request(object):
    def __init__(self, method_specs, method_func_from_method_spec=DFLT_METHOD_FUNC_FROM_METHOD_SPEC):
        for method_name, method_spec in method_specs.items():
            self.inject_method(method_name, method_spec, method_func_from_method_spec)

    def inject_method(self, method_name, method_spec, method_func_from_method_spec=None):
        if not callable(method_spec):
            if method_func_from_method_spec is None:
                raise ValueError("You need a method_func_from_method_spec")
            method_spec = method_func_from_method_spec(method_spec)
        inject_method(self, method_spec, method_name)

# def mk_python_binder(method_specs,
#                      method_func_from_method_spec=DFLT_METHOD_FUNC_FROM_METHOD_SPEC,
#                      obj_kwargs=None
#                      ):
#     if obj_kwargs is None:
#         obj_kwargs = {}
#     binder = Py2Req(**obj_kwargs)
#
#     for method_name, method_spec in method_specs.iteritems():
#         if not callable(method_spec):
#             if method_func_from_method_spec is None:
#                 raise ValueError("You need a method_func_from_method_spec")
#             method_spec = method_func_from_method_spec(method_spec)
#         inject_method(binder, method_spec, method_name)
#
#     return binder

# def mk_request_kwargs(base_url, input_trans=None):
#
#     if input_trans is None:
#         input_trans = lambda x: x

# def mk_request_function(base_url, input_trans=None, kwargs_validator=None, output_trans=None):
#     if kwargs_validator is None:
#         kwargs_validator = mk_default_completion_validator()
#
#     def request_func(self, **kwargs):
#         kwargs = input_trans(kwargs)
#         kwargs = kwargs_validator(kwargs)
#         kwargs['url'] = base_url + kwargs['url']  # prepend url with base_url TODO: Consider other name (suff_url?)
#         return request(**kwargs)
#
#     return request_func

# class Py2Request(object):
#     def __init__(self, base_url=DFLT_BASE_URL, kwargs_validator=None):
#         self.base_url = base_url
#         if kwargs_validator is None:
#             kwargs_validator = mk_default_completion_validator()
#         self.kwargs_validator = kwargs_validator
#
#     def request(self, **kwargs):  # TODO: How to get kwargs spec directly from request (using inspect)?
#         kwargs = self.kwargs_validator(kwargs)
#         kwargs['url'] = self.base_url + kwargs['url']  # prepend url with base_url
#         return request(**kwargs)
