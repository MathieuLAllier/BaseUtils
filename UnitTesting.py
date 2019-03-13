
import time
import functools
from termcolor import colored


def time_func(_func=None, *, runs=3):
    """https://realpython.com/primer-on-python-decorators/"""

    if runs < 1:
        raise ValueError('runs should be higher than 0 not {}'.format(runs))

    def decorator(func):

        @functools.wraps(func)
        def inner(*args, **kwargs):

            value = None
            start = time.perf_counter()

            for _ in range(runs):
                value = func(*args, **kwargs)

            end = time.perf_counter()
            run_time = (end - start) / (_ + 1)
            print(colored('function: {} took {:.4f} secs on an average of {} runs'.format(
                func.__name__,
                run_time,
                runs
            ), 'red'))
            return value

        return inner

    if _func is None:
        return decorator
    return decorator(_func)


if __name__ == '__main__':
    @time_func(runs=10)
    def test():
        for i in range(1000):
            print(i)

    test()

