"""
Won't show the details here, but if you are used to it's not that hard, you just need to find the definition of the API, read it, figure out what part of the request you need in the URL and what you need to put in the "payload", figure out how those _inputs_ of the request need to be formated, construct the URL and the payload according to your newly acquired knowledge of this specific API, make a web request (say with `urllib.request` or `requests`), extract the information you need from the response object (often in `.contents` or `.json()`), and often process the data further to get it in the format you can use it directly (say a list, a dict, a dataframe, a numpy array, etc.).

And if you're experienced, and have felt the pain of needing to reuse or adapt your code, you'll clean things up as soon as you figure this puzzle out. You'll divide your code into separate concerns, encapsulate these concerns in functions and classes, and offer a simple, intuitive, python-like interface that reflects the simplicity of what you're actually doing: Just getting some data. Something like:

```
nice_python_obj_I_can_use_directly = get_that_darn_data(query, using, my, words, values, and, defaults='here')
```

The details being hidden away, as they should.

And that's fine. You've done well. Congratulate yourself, you deserve it.

Now do that again and again and again, and sometimes under the pressure of a deadline that depends on this data being acquired.

Are you enjoying yourself?

There must be a better way...
"""
from functools import wraps
from requests import request
import string
from i2i.util import inject_method, imdict
from py2mint.signatures import set_signature_of_func

from warnings import warn

warn('Deprecated: Use the one in https://github.com/i2mint/py2misc instead!')

DFLT_PORT = 5000
DFLT_BASE_URL = 'http://localhost:{port}'.format(port=DFLT_PORT)
DFLT_REQUEST_KWARGS = imdict({'method': 'GET', 'url': ''})


def identity_func(x):
    return x


class DebugOptions:
    print_request_kwargs = 'print_request_kwargs'
    return_request_kwargs = 'return_request_kwargs'


def mk_default_completion_validator(dflt_kwargs=DFLT_REQUEST_KWARGS):
    def default_completion_validator(kwargs):
        return dict(dflt_kwargs, **kwargs)

    return default_completion_validator


def all_necessary_fields_validator(kwargs):
    assert 'method' in kwargs and 'url' in kwargs, "Need both a method and a url field!"
    return kwargs


def _ensure_list(x):
    if isinstance(x, str):
        return [x]
    return x


def mk_request_function(method_spec):
    """
    Makes function that will make http requests for you, on your own terms.

    Specify what API you want to talk to, and how you want to talk to it (and it talk back to you), and
    get a function that does exactly that.

    Essentially, this factory function allows you to take an API specification, specify how you want it to
    relate to python objects (how to convert input arguments to API elements, and how to convert the response of
    the request, for instance), and get a method that is ready to be used.

    :param method_spec: Specification of how to convert arguments of the function that is being made to an http request.
    :return: A function.
        Note: I say "function", but the function is meant to be a method, so the function has a self as first argument.
        That argument is ignored.

    """
    # defaults
    method_spec = method_spec.copy()
    method_spec['request_kwargs'] = method_spec.get('request_kwargs', {})
    method_spec['request_kwargs']['method'] = method_spec['request_kwargs'].get('method', 'GET')
    arg_order = _ensure_list(method_spec.get('args', []))

    # TODO: inject a signature, and possibly a __doc__ in this function
    def request_func(self, *args, **kwargs):

        # absorb args in kwargs
        if len(args) > len(arg_order):
            raise ValueError(
                f"The number ({len(args)}) of unnamed arguments was greater than "
                f"the number ({len(arg_order)}of specified arguments in arg_order")

        kwargs = dict(kwargs, **{argname: argval for argname, argval in zip(arg_order, args)})

        # convert argument types TODO: Not efficient. Might could be revised.
        for arg_name, converter in method_spec.get('input_trans', {}).items():
            if arg_name in kwargs:
                kwargs[arg_name] = converter(kwargs[arg_name])

        json_data = {}
        for arg_name in method_spec.get('json_arg_names', []):
            if arg_name in kwargs:
                json_data[arg_name] = kwargs.pop(arg_name)

        # making the request_kwargs ####################################################################################
        request_kwargs = method_spec['request_kwargs']
        if 'url_template' in method_spec:
            request_kwargs['url'] = method_spec['url_template'].format(**kwargs)
        elif 'url' in method_spec:
            request_kwargs['url'] = method_spec['url']

        if json_data:
            request_kwargs['json'] = json_data

        if 'debug' in method_spec:
            debug = method_spec['debug']
            if debug == 'print_request_kwargs':
                print(request_kwargs)
            elif debug == 'return_request_kwargs':
                return request_kwargs

        r = request(**request_kwargs)
        if 'output_trans' in method_spec:
            r = method_spec['output_trans'](r)
        return r

    if 'wraps' in method_spec:
        return wraps(method_spec['wraps'])(request_func)
    else:
        all_args = method_spec.get('args', []) + method_spec.get('json_arg_names', [])
        if all_args:
            set_signature_of_func(request_func, ['self'] + all_args)

    return request_func


def mk_request_method(method_spec):
    """
    Makes function that will make http requests for you, on your own terms.

    Specify what API you want to talk to, and how you want to talk to it (and it talk back to you), and
    get a function that does exactly that.

    Essentially, this factory function allows you to take an API specification, specify how you want it to
    relate to python objects (how to convert input arguments to API elements, and how to convert the response of
    the request, for instance), and get a method that is ready to be used.

    :param method_spec: Specification of how to convert arguments of the function that is being made to an http request.
    :return: A function.
        Note: I say "function", but the function is meant to be a method, so the function has a self as first argument.
        That argument is ignored.

    """
    # defaults
    method_spec = method_spec.copy()
    method_spec['request_kwargs'] = method_spec.get('request_kwargs', {})
    method_spec['request_kwargs']['method'] = method_spec['request_kwargs'].get('method', 'GET')
    arg_order = _ensure_list(method_spec.get('args', []))

    # TODO: inject a signature, and possibly a __doc__ in this function
    def request_method(self, *args, **kwargs):

        # absorb args in kwargs
        if len(args) > len(arg_order):
            raise ValueError(
                f"The number ({len(args)}) of unnamed arguments was greater than "
                f"the number ({len(arg_order)}of specified arguments in arg_order")

        kwargs = dict(kwargs, **{argname: argval for argname, argval in zip(arg_order, args)})

        # convert argument types TODO: Not efficient. Might could be revised.
        for arg_name, converter in method_spec.get('input_trans', {}).items():
            if arg_name in kwargs:
                kwargs[arg_name] = converter(kwargs[arg_name])

        json_data = {}
        for arg_name in method_spec.get('json_arg_names', []):
            if arg_name in kwargs:
                json_data[arg_name] = kwargs.pop(arg_name)

        # making the request_kwargs ####################################################################################
        request_kwargs = method_spec['request_kwargs']
        if 'url_template' in method_spec:
            request_kwargs['url'] = method_spec['url_template'].format(**kwargs)
        elif 'url' in method_spec:
            request_kwargs['url'] = method_spec['url']

        if json_data:
            request_kwargs['json'] = json_data

        if 'debug' in method_spec:
            debug = method_spec['debug']
            if debug == 'print_request_kwargs':
                print(request_kwargs)
            elif debug == 'return_request_kwargs':
                return request_kwargs

        r = request(**request_kwargs)
        if 'output_trans' in method_spec:
            r = method_spec['output_trans'](r)
        return r

    if 'wraps' in method_spec:
        wraps(method_spec['wraps'])(request_method)
    else:
        all_args = method_spec.get('args', []) + method_spec.get('json_arg_names', [])
        if all_args:
            set_signature_of_func(request_method, ['self'] + all_args)

    return request_method


DFLT_METHOD_FUNC_FROM_METHOD_SPEC = mk_request_function

str_formatter = string.Formatter()


class Py2Request(object):
    """ Make a class that has methods that offer a python interface to web requests """

    def __init__(self, method_specs=None,
                 method_func_from_method_spec=DFLT_METHOD_FUNC_FROM_METHOD_SPEC):
        """
        Initialize the object with web request calling methods.
        You can also just make an empty Py2Request object, and inject methods later on, one by one.


        :param method_specs:  A {method_name: method_spec,...} dict that specifies
            what methods to create (the method_name part) and what that method should do (the method_spec part).
            Notice that there's no restriction on method_specs, but by default (becauise
        :param method_func_from_method_spec: The function that makes an actual method (function, which will be bounded)
            from the method_specs

        Notice that there's no restriction on the method_spec (singular) values of the method_specs dict.
        Indeed, it could be any object that is understood by the method_func_from_method_spec function, that
        would result in a function that can be "injected" as a method of Py2Request.

        >>> import re
        >>> from collections import Counter
        >>> # Defining the functions we'll use
        >>> def print_content(r):
        ...     print(r.text)
        >>> def dict_of_json(r):
        ...     return json.loads(r.content)
        >>> tokenizer = re.compile('\w+').findall
        >>> # Defining the specs
        >>> method_specs = {
        ...     'google_google': {
        ...         'request_kwargs': {
        ...             'url': 'https://www.google.com/search?q=google'
        ...         }
        ...     },
        ...     'search_google': {
        ...         'url_template': 'https://www.google.com/search?q={search_term}',
        ...         'args': ['search_term'],  # only needed if you want to use unnamed arguments in your method
        ...         'output_trans': lambda r: r.text,
        ...     },
        ...     'search_google_and_count_tokens': {
        ...         'url_template': 'https://www.google.com/search?q={search_term}',
        ...         'output_trans': lambda r: Counter(tokenizer(r.text)).most_common()
        ...     },
        ...     'my_ip': {
        ...         'url_template': 'https://api.ipify.org?format=json',
        ...         'output_trans': dict_of_json
        ...     },
        ...     'print_ip_location': {
        ...         'url_template': 'http://ip-api.com/#{ip_address}',
        ...         'output_trans': print_content
        ...     },
        ... }
        >>> pr = Py2Request(method_specs=method_specs)
        >>> html = pr.search_google('convention over configuration')
        >>> html[:14]
        '<!doctype html'
        >>> # And I'll let the reader try the other requests, whose results are not stable enough to test like this

        """
        self._method_specs = method_specs
        self._dflt_method_func_from_method_spec = method_func_from_method_spec
        self._process_method_specs()

        for method_name, method_spec in self._method_specs.items():
            self._inject_method(method_name, method_spec, method_func_from_method_spec)

    def _process_method_specs(self):
        if self._dflt_method_func_from_method_spec == mk_request_function:
            for method_name, method_spec in self._method_specs.items():
                if 'args' not in method_spec and 'url_template' in method_spec:
                    method_spec['args'] = list(filter(bool,
                                                      (x[1] for x in str_formatter.parse(method_spec['url_template']))))


    def _inject_method(self, method_name, method_spec, method_func_from_method_spec=None):
        if not callable(method_spec):
            if method_func_from_method_spec is None:
                method_func_from_method_spec = self._dflt_method_func_from_method_spec
            method_spec = method_func_from_method_spec(method_spec)
        inject_method(self, method_spec, method_name)


class UrlMethodSpecsMaker:
    """
    Utility to help in making templated method_specs dicts to be used to define a Py2Request object.
    """

    def __init__(self, url_root, constant_url_query=None, **constant_items):
        """
        Make a method_spec factory.

        Args:
            url_root: The absolute prefix of all 'url_template' keys
            constant_url_query: The dict specifying the query part of the url_template that should appear in
                all url_templates (used for example, to specify api keys)
            **constant_items: Other dict entries that should be systematically created

        >>> mk_specs = UrlMethodSpecsMaker(
        ...     url_root='http://myapi.com',
        ...     constant_url_query={'apikey': 'SECRET', 'fav': 42},
        ...     output_trans=lambda response: response.json())
        >>>
        >>> s = mk_specs(route='/search', url_queries={'q': 'search_term', 'limit': 'n'})
        >>> assert list(s.keys()) == ['url_template', 'args', 'output_trans']
        >>> s['url_template']
        'http://myapi.com/search?apikey=SECRET&fav=42&q={search_term}&limit={n}'
        >>> s['args']
        ['search_term', 'n']
        >>>
        >>> s = mk_specs(route='/actions/poke', url_queries='user')
        >>> s['url_template']
        'http://myapi.com/actions/poke?apikey=SECRET&fav=42&user={user}'
        >>> s['args']
        ['user']
        >>>
        >>> s = mk_specs('/actions/msg', ['user', 'msg'])
        >>> s['url_template']
        'http://myapi.com/actions/msg?apikey=SECRET&fav=42&user={user}&msg={msg}'
        >>> s['args']
        ['user', 'msg']
        """
        self.url_root = url_root
        if constant_url_query is None:
            self.constant_url_suffix = ''
        else:
            self.constant_url_suffix = '?' + '&'.join(
                map(lambda kv: f'{kv[0]}={kv[1]}', constant_url_query.items()))
        self.constant_items = constant_items

    def __call__(self, route, url_queries=None):
        url_template = self.url_root + route + self.constant_url_suffix
        if url_queries is None:
            d = {'url_template': url_template}
        if url_queries is not None:
            if isinstance(url_queries, str):
                url_queries = {url_queries: url_queries}
            elif isinstance(url_queries, (list, tuple, set)):
                url_queries = {name: name for name in url_queries}
            # assert the general case where url query (key) and arg (val) names are different
            assert isinstance(url_queries, dict), "url_queries should be a dict"
            url_template += '&' + '&'.join(
                map(lambda kv: f'{kv[0]}={{{kv[1]}}}', url_queries.items()))
            d = {'url_template': url_template, 'args': list(url_queries.values())}
        return dict(d, **self.constant_items)

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
