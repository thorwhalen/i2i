from aiohttp import web
import inspect

# valid inputs:
# - a list of callables
# - a dict with string keys and callable values
# - TODO: a class

app = web.Application()


def make_method_handler(constructor, method_name):
    constructor_arg_spec = inspect.getfullargspec(constructor.__init__).args

    async def handler(request):
        request_body = await request.json()
        constructor_kwargs = {arg: request_body.pop(arg) for arg in constructor_arg_spec}
        obj = constructor(**constructor_kwargs)
        method = getattr(obj, method_name)
        function_result = method(**request_body)
        return web.json_response(body=function_result)
    return handler


def make_handler(fn):
    async def handler(request):
        request_body = await request.json()
        function_result = fn(**request_body)
        return web.json_response(body=function_result)
    return handler


def generate_routes(input_construct):
    if inspect.isclass(input_construct):
        methods = inspect.getmembers(input_construct, predicate=inspect.ismethod)
        routes = [web.post('/' + method.__name__, make_method_handler(input_construct, method.__name__, constructor_kwargs))
                  for method in methods]
    elif isinstance(input_construct, dict):
        routes = [web.post('/' + key, make_handler(fn))
                  for key, fn in input_construct if callable(fn)]
    else:
        routes = [web.post('/' + fn.__name__, make_handler(fn))
                  for fn in input_construct if callable(fn)]
    app.add_routes(routes)
