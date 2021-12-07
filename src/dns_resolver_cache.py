import datetime
import threading

from typing import Dict, Tuple

timer_val: int = 10


class CacheEntry:
    """
    Represents an entry in the cache
        - contains the value of the cached entry and a timestamp that expresses until when this entry is valid
    """

    def __init__(
        self,
        value: str,
        timestamp_remove: datetime.datetime,
    ) -> None:
        self.value: str = value
        self.timestamp_remove: datetime.datetime = timestamp_remove


class Cache(Dict[Tuple[str, int], CacheEntry]):
    """
    Represents the Cache
        - is a Dictionary with domain name and query time as key and a CacheEntry as value
    """

    def __init__(self) -> None:
        threading.Timer(timer_val, self.__cache_cleanup).start()

    def __cache_cleanup(self):
        for key, cache_entry in self.copy().items():
            #print(
            #    f"key: {key} , value: {cache_entry.value} , timestamp_remove: {cache_entry.timestamp_remove}"
            #)
            if cache_entry.timestamp_remove < datetime.datetime.now():
                self.pop(key)
        threading.Timer(timer_val, self.__cache_cleanup).start()
