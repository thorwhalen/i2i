import inspect

from i2i.pymint import mint_of_callable


def str_list_or_dict(input_item):
    if isinstance(input_item, str):
        return True
    if isinstance(input_item, dict):
        for sub_item in input_item.values():
            if not str_list_or_dict(sub_item):
                return False
        return True
    if isinstance(input_item, list):
        for sub_item in input_item:
            if not str_list_or_dict(item):
                return False
        return True
    return False


def add_extensions(obj, extensions):
    if extensions is None:
        return
    for key, value in extensions.items():
        if not str_list_or_dict(value):
            continue
        x_key = 'x-' + key if not str.startswith(key, 'x-') else key
        obj[x_key] = value


def make_openapi_root_spec(title,
                           openapi_version='3.0.2',
                           description='',
                           api_version='0.0.1',
                           contact=None,
                           tos='',
                           license_object=None,
                           url='http://localhost:3000',
                           server_description='',
                           info_extensions=None,
                           root_extensions=None,
                           server_extensions=None,) -> dict:
    info = {
        'title': title,
        'description': description,
        'version': api_version,
        'termsOfService': tos,
    }
    server_spec = {'url': url, 'description': server_description}
    root_spec = {
        'openapi': openapi_version,
        'info': info,
        'servers': [server_spec],
    }
    add_extensions(info_extensions, info)
    add_extensions(root_extensions, root_spec)
    add_extensions(server_extensions, server_spec)
    if isinstance(contact, dict):
        info['contact'] = contact
    if isinstance(license_object, dict):
        info['license'] = license_object


def format_request_prop(input_param) -> dict:
    return dict(input_param, nullable=True)


def make_openapi_path(mint) -> dict:
    name = mint.get('name')
    path_dict = {
        'post': {
            'description': mint['description'],
            'operationId': name,
            'tags': mint['tags'],
            'summary': mint['summary'],
            'requestBody': {
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                key: format_request_prop(input_param)
                                for key, input_param in mint['input'].items()
                            }
                        }
                    }
                }
            }
        }
    }
    return name, path_dict


def make_openapi_spec(input_construct, title, **kwargs) -> dict:
    if isinstance(input_construct, dict):
        minted = [dict(mint_of_callable(item), name=name)
                  for name, item in input_construct.items() if callable(item)]
    else:
        if inspect.isclass(input_construct):
            input_construct = inspect.getmembers(input_construct, predicate=inspect.ismethod)
        minted = [mint_of_callable(item) for item in input_construct if callable(item)]
    paths = {}
    for mint in minted:
        pathname, spec = make_openapi_path(mint)
        paths[pathname] = spec
    openapi_details = make_openapi_root_spec(title, **kwargs)
    openapi_spec = dict(openapi_details, paths=paths)
    return openapi_spec
