import inspect


def method_for_func(func, self_attrs=(), excluded_args=()):
    """
    A function that will make an 'intended to be bounded method' from a function.
    The intention is to be able to take a "normal" function, and use it as a method.
    For this, the first argument of the "method" function needs to refer to a class (cls) or instance thereof (self).

    For now, nothing difficult: A simple decorator inserting (and ignoring) a cls or self argument would do.
    But what if we want the created "method" function to grab it's needed arguments not from the arguments of the
    function itself, but from the attributes of cls or self.

    There lies the rub, and the present function is the ointment.

    For example, if we have
        def func(a, b, c='default_of_c', d=0): ...
    then
        method_for_func(func, self_attrs=('a', 'c'), excluded_args=('d',))
    would give us a function with the signature
        method(self, a, b): ...
    that would simply return
        func(a=self.a, b=b, c=getattr(self, 'c', 'default_of_c'), d=0)

    >>> from collections import namedtuple
    >>>
    >>> def func(a, b=0, greeting='Hello'):
    ...     ''' The doc of the func '''
    ...     return "{}! The sum is {}.".format(greeting, a + b)
    ...
    >>> func(a=10, b=1, greeting='hi there')
    'hi there! The sum is 11.'
    >>>
    >>> A = namedtuple('A', ('b', 'greeting'))
    >>> self = A(b=1, greeting='hi there')
    >>> print(self)
    A(b=1, greeting='hi there')
    >>>
    >>> method_func = method_for_func(func, ('b', 'greeting'))
    >>> method_func(self, a=10)
    'hi there! The sum is 11.'
    """
    self_attrs = set(self_attrs)
    excluded_args = set(excluded_args)
    signature = inspect.signature(func)

    def method(self, *args, **kwargs):
        # func_kwargs = {}
        for self_attr in self_attrs:
            kwargs[self_attr] = getattr(self, self_attr)
            # kwargs[self_attr] = getattr(self, self_attr, kwargs[self_attr]) # fall back on kwargs
        return func(**kwargs)

    return method

# NOTE: A version where I started to try to handle excluded_args and args
#
# from functools import wraps
#
# def method_for_func(func, self_attrs=(), excluded_args=()):
#     """
#     A function that will make an 'intended to be bounded method' from a function.
#     The intention is to be able to take a "normal" function, and use it as a method.
#     For this, the first argument of the "method" function needs to refer to a class (cls) or instance thereof (self).
#
#     For now, nothing difficult: A simple decorator inserting (and ignoring) a cls or self argument would do.
#     But what if we want the created "method" function to grab it's needed arguments not from the arguments of the
#     function itself, but from the attributes of cls or self.
#
#     There lies the rub, and the present function is the ointment.
#
#     For example, if we have
#         def func(a, b, c='default_of_c', d=0): ...
#     then
#         method_for_func(func, self_attrs=('a', 'c'), excluded_args=('d',))
#     would give us a function with the signature
#         method(self, a, b): ...
#     that would simply return
#         func(a=self.a, b=b, c=getattr(self, 'c', 'default_of_c'), d=0)
#
#     >>> from collections import namedtuple
#     >>>
#     >>> def func(a, b=0, greeting='Hello'):
#     ...     ''' The doc of the func '''
#     ...     return "{}! The sum is {}.".format(greeting, a + b)
#     ...
#     >>> func(a=10, b=1, greeting='hi there')
#     'hi there! The sum is 11.'
#     >>>
#     >>> A = namedtuple('A', ('b', 'greeting'))
#     >>> self = A(b=1, greeting='hi there')
#     >>> print(self)
#     A(b=1, greeting='hi there')
#     >>>
#     >>> method_func = method_for_func(func, ('b', 'greeting'))
#     >>> method_func(self, a=10)
#     'hi there! The sum is 11.'
#     """
#     self_attrs = set(self_attrs)
#     excluded_args = set(excluded_args)
#     signature = inspect.signature(func)
#
#     def method(self, *args, **kwargs):
#         # func_kwargs = {}
#         for self_attr in self_attrs:
#             kwargs[self_attr] = getattr(self, self_attr)
#             # kwargs[self_attr] = getattr(self, self_attr, kwargs[self_attr]) # fall back on kwargs
#         return func(**kwargs)
#
#     return method
#
#
