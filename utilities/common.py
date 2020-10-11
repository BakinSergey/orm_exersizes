import time
import random
import string

from django.conf import settings


def rnd_string(size):
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))


def rnd_number(size):
    return ''.join(random.choice(string.digits) for _ in range(size))


def clock(func):
    def clocked(*args, **kwargs):
        t0 = time.time()

        result = func(*args, **kwargs)  # вызов декорированной функции

        elapsed = time.time() - t0
        name = func.__name__
        arg_1st = []
        if args:
            arg_1st.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
            arg_1st.append(', '.join(pairs))
        arg_str = ', '.join(arg_1st)
        print('[%0.8fs] %s' % (elapsed, name))
        # print('[%0.8fs] %s(%s)' % (elapsed, name, arg_str))
        # print('[%0.8fs] %s(%s) -> %r' % (elapsed, name, arg_str, result))
        return result

    if settings.DEBUG:
        return clocked
    return
