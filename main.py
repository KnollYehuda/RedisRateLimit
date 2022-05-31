import math
import random
import time
from datetime import timedelta
from redis import Redis

from logger import init_logger
from request import ARequest

# application redis
r = Redis()

# application logger
logger = init_logger()


def rate_limit(request: ARequest, limit: int = -1, period: int = math.inf):
    from functools import wraps
    from threading import Semaphore

    # 'first log' conflict prevention
    logging_semaphore = Semaphore(1)

    # prevents conflict when calculating the 'extra period'
    calls_semaphore = Semaphore(1)

    def extra_period_to_add(key: str):
        calls_semaphore.acquire()
        extra_period = 0
        try:
            calls_key = f'calls${key}'
            current_time = time.time()
            calls_list = r.lrange(calls_key, 0, -1)
            if calls_list:
                avg_diffs = (float(calls_list[1]) + current_time) / float(calls_list[1])
                if avg_diffs <= 1 and float(calls_list[1]) > 10:
                    extra_period = float(calls_list[1]) * limit
                r.lset(calls_key, 0, current_time)
                r.lset(calls_key, 1, float(calls_list[1]) + 1)
            else:
                r.lpush(calls_key, current_time)
                r.lpush(calls_key, 1)
        except Exception as ex:
            logger.error(ex)
        calls_semaphore.release()
        return extra_period

    def request_is_limited(key: str, func_name: str):
        key = f'{key}${func_name}'
        if not key:
            raise ValueError('request is invalid')
        if limit < 0 or period == math.inf:
            return False
        extra_period = extra_period_to_add(key)
        if r.setnx(key, limit):
            delta_time_period = timedelta(seconds=period + extra_period)
            r.expire(key, int(delta_time_period.total_seconds()))
            logger.info(f'current {key} ttl :: {r.ttl(key)}')
        key_val = r.get(key)
        if key_val and int(key_val) > 0:
            r.decrby(key, 1)
            return False
        if can_log(key):
            logger.critical(f'request "{func_name}" is limited for key :: "{key}"')
        return True

    def can_log(key: str = None):
        can_log_rest = False
        log_verify_key = f'log_verify${key}'
        logging_semaphore.acquire()
        try:
            if not r.exists(log_verify_key):
                delta_time_period = timedelta(seconds=period)
                r.setnx(log_verify_key, 0)
                r.expire(log_verify_key, int(delta_time_period.total_seconds()))
                can_log_rest = True
        except Exception as ex:
            logger.error(ex)
        logging_semaphore.release()
        return can_log_rest

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.get_method() == ARequest.RequestMethod.USER_ID:
                request.set_value(user_id_from_token())
            else:
                request.set_value(ip_from_request())
            if not request_is_limited(str(request), f.__name__):
                args += (request.get_value(), )
                return f(*args, **kwargs)

        return wrapper

    return decorator


def user_id_from_token():
    return random.randint(1, 72)


def ip_from_request():
    return f'{random.randint(1,50)}.{random.randint(1,40)}.{random.randint(1,30)}.{random.randint(1,20)}'


@rate_limit(request=ARequest(method=ARequest.RequestMethod.USER_ID), limit=10, period=60)
def dog(*args, **kwargs):
    return f'dog - kwargs :: {kwargs}, args :: {args}'


@rate_limit(request=ARequest(method=ARequest.RequestMethod.IP), limit=15, period=60)
def cat(*args, **kwargs):
    return f'cat :: {kwargs}, args :: {args}'


if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(5000):
            message = f'a message - {random.randint(1, 100000)}'
            if i % 2 == 0:
                futures.append(executor.submit(dog, message=message))
            else:
                futures.append(executor.submit(cat, message=message))
        for future in as_completed(futures):
            results = future.result()
            if results:
                logger.info(f'ALL GOOD !! {future.result()}')
