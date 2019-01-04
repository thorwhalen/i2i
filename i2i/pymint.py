import inspect


class NoDefault(object):
    def __repr__(self):
        return 'no_default'


no_default = NoDefault()

NO_NAME = '_no_name'

valid_json_types = [str, dict, list, float, int, bool]

name_of_pytype = {
    str: 'string',
    dict: 'object',
    list: 'array',
    float: 'float',
    int: 'int',
    bool: 'boolean',
    '{}': '{}',
    None: '{}'
}


def name_of_obj(o):
    if hasattr(o, '__name__'):
        return o.__name__
    elif hasattr(o, '__class__'):
        return name_of_obj(o.__class__)
    else:
        return NO_NAME


def parse_mint_doc(doc: str) -> dict:
    DESCRIPTION = 0
    PARAMS = 1
    RETURN = 2
    split_doc = doc.split('\n')
    summary = ''
    description_lines = []
    inputs = {}
    return_value = {}
    tags = []
    reading = DESCRIPTION
    cur_item_name = ''
    for line in split_doc:
        if line.startswith(':param'):
            reading = PARAMS
            split_line = line.split(':')
            param_def = split_line[1]
            split_param_def = param_def.split(' ')
            param_name = ''
            if len(split_param_def) >= 3:
                param_type = split_param_def[1]
                param_name = split_param_def[2]
                try:
                    assert len(param_type) <= 5
                    param_type = eval(param_type)
                    assert param_type in valid_json_types
                except Exception:
                    param_type = '{}'
            elif len(split_param_def) == 2:
                param_name = split_param_def[1]
            if param_name:
                cur_item_name = param_name
                inputs[param_name] = {'type': param_type}
                inputs[param_name]['description'] = ':'.join(split_line[2:]) \
                    if len(split_line) > 2 else ''
        elif line.startswith(':return'):
            reading = RETURN
            split_line = line.split(':')
            return_type = split_line[1]
            try:
                assert len(return_type) <= 5
                return_type = eval(return_type)
                assert return_type in valid_json_types
            except Exception:
                return_type = '{}'
            return_value = {'type': return_type}
            return_value['description'] = ':'.join(split_line[2:]) \
                if len(split_line) > 2 else ''
        elif line.startswith(':tags'):
            split_line = line.split(':')
            tags = split_line[1].replace(' ', '').split(',')
        else:
            if reading == DESCRIPTION:
                if not summary:
                    summary = line
                else:
                    description_lines.append(line)
            elif reading == PARAMS:
                inputs[cur_item_name]['description'] += ' ' + line
            elif reading == RETURN:
                return_value['description'] += ' ' + line
    return {
        'description': ' '.join(description_lines),
        'inputs': inputs,
        'return': return_value,
        'summary': summary,
        'tags': tags,
    }


# TODO: Expand so that user can specify what to include in the mint
# TODO: Include doctests (see below for inspiration)
#     >>> import json
#     >>> mint = mint_of_callable(mint_of_callable)
#     >>> print(json.dumps(mint), indent=2)
#     {
#       "name": "mint_of_callable",
#       "module": "i2i.i2i.pymint",
#       "doc": "    Get meta-data about a callable.\n    :param f: A callable (function, method, ...)\n    :return: A dict containing information about the interface of f, that is, name, module, doc, and input and output\n    information.\n    >>> mint = mint_of_callable(mint_of_callable)\n    >>> expected_mint = {\n    ...     'name': 'mint_of_callable',\n    ...     'module': 'i2i.i2i.pymint',\n    ...     'doc': 'Get meta-data about a callable.\n:param f: A callable (function, method, ...)\n:return: A dict containing information about the interface of f, that is, name, module, doc, and input and output\ninformation.', 'input': {'f': {}}}\n\n    ",
#       "input": {
#         "f": {}
#       }
#     }
def mint_of_callable(f):
    """
    Get meta-data about a callable.
    :param f: A callable (function, method, ...)
    :return: A dict containing information about the interface of f, that is, name, module, doc, and input and output
    information.
    """
    raw_doc = inspect.getdoc(f)
    parsed_doc = parse_mint_doc(raw_doc)
    doc_inputs = parsed_doc['inputs']
    doc_return = parsed_doc['return']
    mint = {
        'name': name_of_obj(f),  # TODO: Better NO_NAME or just not the name field?
        'module': f.__module__,
        'doc': raw_doc,
        'description': parsed_doc['description'] or '',
        'summary': parsed_doc['summary'],
        'tags': parsed_doc['tags']
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
        if arg_name in doc_inputs:
            doc_input_arg = doc_inputs[arg_name]
            input_specs[arg_name]['type'] = doc_input_arg['type']
            input_specs[arg_name]['description'] = doc_input_arg['description']
        if arg_name in annotations:
            input_specs[arg_name]['type'] = annotations[arg_name]
        if input_specs[arg_name]['type']:
            input_specs[arg_name]['type'] = name_of_pytype.get(input_specs[arg_name]['type'], '{}')

    mint['input'] = input_specs

    mint['output'] = {}
    if doc_return:
        mint['output'] = doc_return
    if 'return' in annotations:
        mint['output']['type'] = annotations['return']

    return mint


""" TODO:
    - indicate required/optional or nullable input arguments
    - indicate input argument constraints (min, max, enum, etc)
    - allow listing properties of complex objects as input arguments
        (eg argument a1 type is a dict with expected properties p1, p2, p3)
"""
