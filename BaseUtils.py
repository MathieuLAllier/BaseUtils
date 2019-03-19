from itertools import chain, islice


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
    return [val for sublist in iterable for val in sublist]
