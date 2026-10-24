import functools
import logging
from typing import Callable


def debug(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        debug_logger = logging.getLogger(f"{func.__module__}")
        debug_logger.info(f">>> {func.__qualname__}({signature})", stacklevel=2)
        result = func(*args, **kwargs)
        debug_logger.info(f"<<< {func.__qualname__}: {result!r}", stacklevel=2)
        return result
    return wrapper
