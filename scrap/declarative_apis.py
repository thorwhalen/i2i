from __future__ import division

from requests import request
from i2i.util import inject_method


def insert_path_params(path, input_values):
    split_path = path.split('/')
    for index, segment in enumerate(split_path[:]):
        if segment.startswith(':'):
            key = segment[1:]
            if key not in input_values:
                raise Exception('missing input argument: {}'.format(key))
            split_path[index] = input_values[key]
    return '/'.join(split_path)


def add_remote_method(self,
                      endpoint_name,
                      service,
                      method,
                      path,
                      input_mapper=None,
                      has_file=False):
    """Add an HTTP request method to the object based on a JSON route definition

    Keyword arguments:
    endpoint_name -- the name of the method that will be injected
    service -- the microservice to call (as a URL prefix)
    method -- the HTTP method to use (GET, PUT, POST, DELETE)
    path -- the endpoint path
    input_mapper -- a dict describing the required input
    has_file -- a boolean value

    To make our API design slightly more convenient and memory-friendly,
    this wrapper currently supports request bodies in either JSON format
    or binary files, and no other content-types. If a file is included,
    there may not be any key-value pairs in the body and all arguments must be
    in the query or route parameters.

    The idacc must also include a method, yet to be implemented,
    to generate a valid JWT with a specific set of keys for authentication,
    or (more likely) to return one from a set of pre-generated JWTs.

    Example usage:

    example_schema = {
        "endpoint_name": "upload_segment",
        "service": "audio",
        "method": "PUT",
        "path": "/segment/:channel_hwid/:bt",
        "has_file": True,
        "input_mapper": {
            "account": "token.account",
            "device": "token.device_id",
            "channel": "params.channel_hwid",
            "bt": "params.bt",
            "session_bt": "query.session_bt",
            "sr": "query.sr",
            "bitrate": "query.bitrate",
        }
    }

    idacc.add_remote_method(**example_schema)

    """
    if input_mapper is None:
        input_mapper = {}

    input_keys = {'body': [], 'params': [], 'query': [], 'token': []}
    for prop in input_mapper.itervalues():
        source, key = tuple(prop.split('.'))
        input_keys[source].append(key)

    def mk_url(self, kwargs):
        resolved_path = insert_path_params(path, kwargs)
        query = '?'
        for key in input_keys['query']:
            if key not in kwargs:
                raise Exception('missing input argument: {}'.format(key))
            query += '{}={}&'.format(key, kwargs[key])
        query = query[:-1]
        url = getattr(self, 'base_url', '') + service + resolved_path + query
        return url

    def mk_body_kwargs(self, kwargs):
        body_kwargs = {'headers': {}}
        # headers = {}
        if method != 'GET':
            if len(input_keys['body']) > 0:
                body_json = {}
                for key in input_keys['body']:
                    if key not in kwargs:
                        raise Exception('missing input argument: {}'.format(key))
                    body_json[key] = kwargs[key]
                body_kwargs['json'] = body_json
                body_kwargs['headers']['Content-type'] = 'application/json'
            elif input_keys.get('has_file', None):
                if 'input_file' not in kwargs:
                    raise Exception('missing input argument: input_file')
                body_kwargs['data'] = kwargs['input_file']
                body_kwargs['headers']['Content-type'] = 'application/octet-stream'
        token = input_keys.get('token', None)
        if token and hasattr(self, 'get_jwt'):
            body_kwargs['headers']['Authorization'] = self.get_jwt(input_keys['token'])
        return body_kwargs

    def _func(self, **kwargs):
        url = mk_url(self, kwargs)
        # print url

        body_kwargs = mk_body_kwargs(kwargs, self)

        return request(method, url, **body_kwargs)

    return inject_method(self, _func, endpoint_name)


def mk_url(base_url, service, query=(), path='', **kwargs):
    resolved_path = insert_path_params(path, kwargs)
    query_url_snippet = '?'
    for key in query:
        if key not in kwargs:
            raise Exception('missing input argument: {}'.format(key))
        query_url_snippet += '{}={}&'.format(key, kwargs[key])
    query_url_snippet = query_url_snippet[:-1]
    url = base_url + service + resolved_path + query_url_snippet
    return url
