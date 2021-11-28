from typing import Dict, List
from dns_format import QryType


class CacheEntry:
    def __init__(
            self,
            value: str,
            rr_type: QryType,
            ttl: int,
    ) -> None:
        self.value: str = value
        self.rr_type: QryType = rr_type
        self.ttl: int = ttl


class Cache(Dict[str, List[CacheEntry]]):
    """
    Class that represents the Cache
        - is a Dictionary with domain as key and a list of CacheEntries as value
    """
    def __init__(self): None

    def get_cache_entries_by_domain_and_rr_type(self, domain: str, rr_type: str) -> List[CacheEntry]:
        domain_entries: List[CacheEntry] = self.get(self, domain)
        result_list: List[CacheEntry] = {}
        for entry in domain_entries:
            if entry.rr_type == rr_type:
                result_list.append(entry)
        return result_list

