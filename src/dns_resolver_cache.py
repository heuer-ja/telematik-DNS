import datetime
from typing import Dict, Tuple
from dns_format import QryType


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
    def __init__(self): None


