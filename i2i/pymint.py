import inspect


class Empty(object):
    def __repr__(self):
        return 'Empty'


EMPTY = Empty()


class AnyType(object):
    def __repr__(self):
        return 'AnyType'


ANY_TYPE = AnyType()


class NoTypeSpecified(object):
    def __repr__(self):
        return 'NoTypeSpecified'


NO_TYPE_SPECIFIED = NoTypeSpecified()


class NoDefault(object):
    def __repr__(self):
        return 'no_default'


no_default = NoDefault()

NO_NAME = '_no_name'

import re
import sys

PARAM_OR_RETURNS_REGEX = re.compile(":(?:param|returns)")
RETURNS_REGEX = re.compile(":returns: (?P<doc>.*)", re.S)
PARAM_REGEX = re.compile(":param (?P<name>[\*\w]+): (?P<doc>.*?)"
                         "(?:(?=:param)|(?=:return)|(?=:raises)|\Z)", re.S)


def trim(docstring):
    """trim function from PEP-257"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Current code/unittests expects a line return at
    # end of multiline docstrings
    # workaround expected behavior from unittests
    if "\n" in docstring:
        trimmed.append("")

    # Return a single string:
    return "\n".join(trimmed)


def reindent(string):
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def parse_docstring(docstring):
    """Parse the docstring into its components.
    :returns: a dictionary of form
              {
                  "short_description": ...,
                  "long_description": ...,
                  "params": [{"name": ..., "doc": ...}, ...],
                  "returns": ...
              }
    """

    short_description = long_description = returns = ""
    params = []

    if docstring:
        docstring = trim(docstring)

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            if params_returns_desc:
                params = [
                    {"name": name, "doc": trim(doc)}
                    for name, doc in PARAM_REGEX.findall(params_returns_desc)
                    ]

                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))

    return {
        "short_description": short_description,
        "long_description": long_description,
        "params": params,
        "returns": returns
    }


valid_json_types = [str, dict, list, float, int, bool]

name_of_pytype = {
    str: 'string',
    dict: 'object',
    list: 'array',
    float: 'float',
    int: 'int',
    bool: 'boolean',
    ANY_TYPE: '{}',
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
            param_type = ANY_TYPE
            reading = PARAMS
            split_line = line.split(':')
            param_def = split_line[1]
            split_param_def = param_def.split(' ')
            param_name = ''
            if len(split_param_def) >= 3:
                param_type = split_param_def[1]
                param_name = split_param_def[2]

                # TODO: Put validation externally, and avoid eval if possible
                # try:
                #     assert len(param_type) <= 5
                #     param_type = eval(param_type)
                #     assert param_type in valid_json_types
                # except Exception:
                #     pass
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

            # TODO: Put validation externally, and avoid eval if possible
            # try:
            #     assert len(return_type) <= 5
            #     return_type = eval(return_type)
            #     assert return_type in valid_json_types
            # except Exception:
            #     return_type = ANY_TYPE
            return_value = {'type': return_type}
            return_value['description'] = ':'.join(split_line[2:]) \
                if len(split_line) > 2 else ''
        elif line.startswith(':tags'):  # TODO: Doesn't seem to be a valid spider doc key
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


def mint_of_instance_method(base_class, method):
    constructor_mint = mint_of_callable(base_class.__init__, ismethod=True)
    method_mint = mint_of_callable(method, ismethod=True)
    return dict(method_mint, input=dict(method_mint['input'], **constructor_mint['input']))


def mint_of_callable(f, ismethod=False):
    """
    Get meta-data about a callable.
    :param f: A callable (function, method, ...)
    :return: A dict containing information about the interface of f, that is, name, module, doc, and input and output
    information.
    """
    raw_doc = inspect.getdoc(f)
    # parsed_doc = parse_mint_doc(raw_doc)
    # doc_inputs = parsed_doc['inputs']
    # doc_return = parsed_doc['return']
    mint = {
        'name': name_of_obj(f),  # TODO: Better NO_NAME or just not the name field?
        'module': f.__module__,
        'doc': raw_doc,
        # 'description': parsed_doc['description'] or '',
        # 'summary': parsed_doc['summary'],
        # 'tags': parsed_doc['tags']
    }

    argspec = inspect.getfullargspec(f)
    annotations = argspec.annotations
    input_specs = {}
    args = argspec.args or []
    if len(args) > 0 and (ismethod or inspect.ismethod(f)):
        args = args[1:]
    defaults = argspec.defaults or []
    for arg_name, dflt in zip(args, [no_default] * (len(args) - len(defaults)) + list(defaults)):
        input_specs[arg_name] = {}
        if dflt is not no_default:
            input_specs[arg_name]['default'] = dflt
        # if arg_name in doc_inputs:
        #     doc_input_arg = doc_inputs[arg_name]
        #     input_specs[arg_name]['type'] = doc_input_arg['type']
        #     input_specs[arg_name]['description'] = doc_input_arg['description']

        # TODO: It's probaby better to keep the ming closer to the original data
        # TODO: For example, an annotation could be something else than a type
        if arg_name in annotations:
            input_specs[arg_name]['type'] = annotations[arg_name]
        if input_specs[arg_name].get('type', None):
            input_specs[arg_name]['type'] = name_of_pytype.get(input_specs[arg_name]['type'], '{}')

    mint['input'] = input_specs

    mint['output'] = {}
    # if doc_return:
    #     mint['output'] = doc_return
    if 'return' in annotations:
        mint['output']['type'] = annotations['return']
    if mint['output'].get('type'):
        mint['output']['type'] = name_of_pytype[mint['output']['type']]
    return mint


def parsed_parameters(parameters):
    return [{'name': pp.name,
             'annotation': pp.annotation,
             'default': pp.default} for pp in parameters.values()]


## Note: Alternatively, a version that uses a custom "empty" variable instead of inspect._empty
## Note: Another alternative would be to not include the field if it's value is empty
# explicit_empty = lambda x: EMPTY if x == inspect._empty else x
# def parsed_parameters(parameters):
#     return [{'name': pp.name,
#              'annotation': explicit_empty(pp.annotation),
#              'default': explicit_empty(pp.default)} for pp in p.values()]


def parsed_signature(obj):
    signature = inspect.signature(obj)
    return {'name': name_of_obj(obj),
            'type': type(obj),
            'parameters': parsed_parameters(signature.parameters),
            'return_annotation': signature.return_annotation
            }


""" TODO:
    - indicate required/optional or nullable input arguments
    - indicate input argument constraints (min, max, enum, etc)
    - allow listing properties of complex objects as input arguments
        (eg argument a1 type is a dict with expected properties p1, p2, p3)
    - allow description of complex return types (nested dicts)
"""


def mint_many(input_construct) -> list:
    if isinstance(input_construct, dict):
        minted = [dict(mint_of_callable(item), name=name)
                  for name, item in input_construct.items() if callable(item)]
    elif inspect.isclass(input_construct):
        method_list = [getattr(input_construct, funcname) for funcname in dir(input_construct)
                       if callable(getattr(input_construct, funcname)) and
                       not funcname.startswith('__')]
        minted = [mint_of_instance_method(input_construct, method) for method in method_list]
    else:
        minted = [mint_of_callable(item) for item in input_construct
                  if callable(item)]
    return minted
