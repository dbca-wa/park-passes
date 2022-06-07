import time
import traceback
from django.db import connection, reset_queries
import functools
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.request import Request
import logging

logger = logging.getLogger("parkpasses")


def basic_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except serializers.ValidationError:
            print(traceback.print_exc())
            logger.error(traceback.print_exc())
            raise
        except ValidationError as e:
            from parkpasses.components.main.utils import handle_validation_error

            handle_validation_error(e)
        except Exception as e:
            print(traceback.print_exc())
            logger.error(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    return wrapper


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
            # logger.error('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()
        start_queries = len(connection.queries)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        end_queries = len(connection.queries)
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        function_name = "Function : {}".format(func.__name__)
        number_of_queries = "Number of Queries : {}".format(end_queries - start_queries)
        time_taken = "Finished in : {0:.2f}s".format((end - start))
        logger.error(function_name)
        logger.error(number_of_queries)
        logger.error(time_taken)
        return result

    return inner_func
