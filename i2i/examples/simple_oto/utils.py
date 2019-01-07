from functools import wraps, lru_cache
import os
from typing import Union


########################################################################################################################
# decorators

def resolve_filepath_of_name(rootdir='', name_arg: Union[int, str] = 0):
    """
    Make a decorator that applies a function to an argument before using it.
    For example:
        * original argument: a relative path --> used argument: a full path
        * original argument: a pickle filepath --> used argument: the loaded object
    :param rootdir: rootdir to be used for all name arguments of target function
    :param name_arg: the position (int) or argument name of the argument containing the name
    :return: a decorator
    >>> def f(a, b, c):
    ...     return "a={a}, b={b}, c={c}".format(a=a, b=b, c=c)
    >>>
    >>> print(f('foo', 'bar', 3))
    a=foo, b=bar, c=3
    >>> ff = resolve_filepath_of_name()(f)
    >>> print(ff('foo', 'bar', 3))
    a=foo, b=bar, c=3
    >>> ff = resolve_filepath_of_name('ROOT')(f)
    >>> print(ff('foo', 'bar', 3))
    a=ROOT/foo, b=bar, c=3
    >>> ff = resolve_filepath_of_name('ROOT', 1)(f)
    >>> print(ff('foo', 'bar', 3))
    a=foo, b=ROOT/bar, c=3
    >>> ff = resolve_filepath_of_name('ROOT', 'b')(f)
    >>> print(ff('foo', b='bar', c=3))
    a=foo, b=ROOT/bar, c=3
    """
    def _resolve_filepath_of_name(func):
        if not rootdir:
            return func
        else:
            @wraps(func)
            def __resolve_filepath_of_name(*args, **kwargs):
                if isinstance(name_arg, int):
                    args = list(args)
                    args[name_arg] = os.path.join(rootdir, args[name_arg])
                else:
                    kwargs[name_arg] = os.path.join(rootdir, kwargs[name_arg])
                return func(*args, **kwargs)

            return __resolve_filepath_of_name

    return _resolve_filepath_of_name


def use_loader(func, load_func=None):
    if load_func is None:
        return func
    else:
        @wraps(func)
        def wrapped_func(first_arg, *args, **kwargs):
            first_arg = load_func(first_arg)
            return func(first_arg, *args, **kwargs)

        return wrapped_func


########################################################################################################################
# chunker

def simple_fixed_step_chunker(seq, chk_size, chk_step=None):
    """
      a function to get (an iterator of) segments [bt, tt) of chunks from an seqquence seq
      of size chk_size, with a step of chk_step

      :param seq: sequence of elements
      :param chk_size: length of the chunks
      :param chk_step: step between chunks
      :return: an iterator of the chunks
    >>> seq = list(range(19))
    >>> seq
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    >>> print(list(simple_fixed_step_chunker(seq, 5)))
    [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14]]
    >>> print(list(simple_fixed_step_chunker(seq, 5, 3)))
    [[0, 1, 2, 3, 4], [3, 4, 5, 6, 7], [6, 7, 8, 9, 10], [9, 10, 11, 12, 13], [12, 13, 14, 15, 16]]
    """

    chk_step = chk_step or chk_size
    seq_minus_chk_length = len(seq) - chk_size
    for bt in range(0, seq_minus_chk_length, chk_step):
        yield seq[bt:(bt + chk_size)]


########################################################################################################################
# featurizers
import numpy as np


def mean_intensity(chk) -> float:
    """
    Mean intensity (mean of abs values)
    :param chk: a waveform (list of numbers)
    :return: the mean intensity
    >>> wf = [1, 2, 3, 4]
    >>> mean_intensity(wf)
    2.5
    >>> wf = [10, -10, 10, -10, 10, -10]
    >>> mean_intensity(wf)
    10.0
    >>> wf = [5, 10, 20, -10, -20, 9, -10]
    >>> mean_intensity(wf)
    12.0
    """
    return np.mean(np.abs(chk))


def mean_zero_crossing(chk) -> float:
    """
    Mean zero crossing
    :param chk: a waveform (list of numbers)
    :return: mean zero crossing
    >>> wf = [1, 2, 3, 4]
    >>> mean_zero_crossing(wf)  # if all numbers are positive (or negative), the mean zero crossing is zero
    0.0
    >>> wf = [10, -10, 10, -10, 10, -10]  # if changing signs at every new element, the mean crossing is 1
    >>> mean_zero_crossing(wf)
    1.0
    >>> wf = [5, 10, 20, -10, -20, 9, -10]  # example where the sign changes half of the time
    >>> mean_zero_crossing(wf)
    0.5
    """
    return np.mean(np.diff(np.array(chk) > 0))


seq = list(range(19))
print(list(simple_fixed_step_chunker(seq, 5)))
print(list(simple_fixed_step_chunker(seq, 5, 3)))
