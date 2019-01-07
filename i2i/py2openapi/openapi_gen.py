import inspect
import json
import yaml

from i2i.pymint import mint_many


default_bad_request_description = 'Generic bad request response.'


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
            if not str_list_or_dict(input_item):
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


def make_openapi_path(mint, **kwargs) -> dict:
    bad_request_description = kwargs.get('bad_request_description', default_bad_request_description)
    name = mint.get('name')
    path_dict = {
        'post': {
            'description': mint['description'],
            'operationId': name,
            'tags': mint.get('tags', []),
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
            },
            'responses': {
                '200': {
                    'description': mint['output']['description'],
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': mint['output']['type']
                            }
                        }
                    }
                },
                '400': {
                    'description': bad_request_description,
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'string'
                            }
                        }
                    }
                },
                '401': {
                    'description': 'Unauthorized request',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
    return name, path_dict


def make_openapi_spec(input_construct, title, **kwargs) -> dict:
    minted = mint_many(input_construct)
    paths = {}
    for mint in minted:
        pathname, spec = make_openapi_path(mint, **kwargs)
        paths[pathname] = spec
    openapi_details = make_openapi_root_spec(title, **kwargs)
    openapi_spec = dict(openapi_details, paths=paths)
    return openapi_spec


def make_and_save_openapi_json(input_construct, title, target_path='openapi.json', **kwargs):
    spec = make_openapi_spec(input_construct, title, **kwargs)
    serialized = json.dumps(spec)
    with open(target_path, 'w') as fp:
        fp.write(serialized)


def make_and_save_openapi_yaml(input_construct, title, target_path='openapi.yml', **kwargs):
    spec = make_openapi_spec(input_construct, title, **kwargs)
    serialized = yaml.dump(spec)
    with open(target_path, 'w') as fp:
        fp.write(serialized)
