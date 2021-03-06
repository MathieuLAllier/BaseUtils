# Collection of Useful Scripting Functions

import functools
from itertools import chain, islice, groupby
from collections.abc import Mapping, Iterable


def default_kwargs(**defaultKwargs):
    """ https://stackoverflow.com/a/50107777/6395612 """

    def actual_decorator(fn):

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            defaultKwargs.update(kwargs)
            return fn(*args, **defaultKwargs)

        return inner
    return actual_decorator


def sort_and_group(iterable, sort_function):
    """ Sort Before Group BY"""
    return groupby(sorted(iterable, key=sort_function), key=sort_function)


def batch(iterable, size):
    """
    :param iterable: Iterable (list, dict, sets, tuples)
    :param size: Size of batch. The size of the iterable to iterate over
    :return: Iterable object

    Use batch function to return an iterable of length 'size' until the 'iterable' is empty
    """
    source_iter = iter(iterable)
    while True:
        batchiter = islice(source_iter, size)
        yield chain([batchiter.__next__()], batchiter)


def complex_update(source, overrides):
    """
    https://stackoverflow.com/a/30655448/6395612

    :param source:      Dictionary      -- Source Dict to Update
    :param overrides:   Dictionary      -- New Dict
    :return: Updated Dictionary

    This Function will update nested dictionary
    """
    for key, value in overrides.items():
        if isinstance(value, Mapping) and value:
            source[key] = complex_update(source.get(key, {}), value)
        else:
            source[key] = overrides[key]
    return source


def flatten(iterable):
    """ Flatten a simple List of List """
    return [val for sublist in iterable for val in sublist]


def complex_flatten(iterable):
    """ Flatten a complex iterable """
    """ https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists """
    for _ in iterable:
        if isinstance(_, Iterable) and not isinstance(_, (str, bytes)):
            yield from complex_flatten(_)
        else:
            yield _


if __name__ == '__main__':
    x = [1, [1, 2, [1, 2, 3]], [3, 4, 5]]
    print(
        list(complex_flatten(x))
    )
