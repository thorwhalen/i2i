from __future__ import division

import requests


def mk_request_function(method_spec):
    def request_func(self, **kwargs):

        # convert argument types TODO: Not efficient. Might could be revised.
        for arg_name, converter in method_spec.get('input_trans', {}).items():
            if arg_name in kwargs:
                kwargs[arg_name] = converter(kwargs[arg_name])

        json_data = {}
        for arg_name in method_spec.get('json_arg_names'):
            if arg_name in kwargs:
                json_data[arg_name] = kwargs.pop(arg_name)

        if 'url_template' in method_spec:
            request_kwargs = dict(method_spec['request_kwargs'], url=method_spec['url_template'].format(**kwargs))
        else:
            request_kwargs = method_spec['request_kwargs']

        if json_data:
            request_kwargs = dict(request_kwargs, json=json_data)
        # kwargs = input_trans(kwargs)
        # kwargs = kwargs_validator(kwargs)
        # kwargs['url'] = base_url + kwargs['url']  # prepend url with base_url TODO: Consider other name (suff_url?)
        r = requests.request(**request_kwargs)
        if 'output_trans' in method_spec:
            r = method_spec['output_trans'](r)
        return r

    return request_func
