from itertools import chain, islice
from collections.abc import Iterable


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
