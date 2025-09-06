from enum import Enum
from time import perf_counter
from typing import Tuple, Any


class RefreshInterval(Enum):
    SEC_5 = 5
    SEC_10 = 10
    SEC_15 = 15
    SEC_20 = 20
    SEC_25 = 25
    SEC_30 = 30
    SEC_45 = 45
    SEC_50 = 50
    MIN_1 = 60
    MIN_5 = 300
    MIN_15 = 900
    MIN_30 = 1800
    HOUR_1 = 3600
    HOUR_6 = 21600
    HOUR_12 = 43200
    DAY_1 = 86400
    DAY_3 = 259200
    DAY_7 = 604800
    DAY_30 = 2592000
    DAY_90 = 7776000
    DAY_180 = 15552000


class DiskUsage(Enum):
    LOW = 0.2
    MEDIUM = 0.4
    HIGH = 0.6
    VERY_HIGH = 0.8
    FULL = 1.0


class SizeDivisor(Enum):
    BYTES = 1
    KB = 1024
    MB = 1024 ** 2
    GB = 1024 ** 3


def timer_sync(func):
    def wrapper(*args, **kwargs) -> Tuple[Any, float]:
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()

        exec_time = end - start

        return result, exec_time

    return wrapper


def timer_async(func):
    async def wrapper(*args, **kwargs) -> Tuple[Any, float]:
        start = perf_counter()
        result = await func(*args, **kwargs)
        end = perf_counter()
        exec_time = end - start
        return result, exec_time

    return wrapper
