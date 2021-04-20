from datetime import datetime
from threading import RLock
from typing import TypeVar, Dict

VT = TypeVar('VT')
KT = TypeVar('KT')


class CacheDict(Dict[KT, VT]):
    _locks: Dict[KT, RLock] = {}
    _updates: Dict[KT, datetime] = {}

    def __init__(self, cache_fn, validate_fn=None):
        super().__init__()
        self.cache_fn = cache_fn
        self.validate_fn = validate_fn

    def get(self, key: KT, *args, **kwargs) -> VT:
        if not self.is_valid(key, *args, **kwargs):
            self.cache(key, *args, **kwargs)
        return super(CacheDict, self).get(key)

    def invalidate(self, key: KT) -> None:
        self.pop(key)

    def cache(self, key: KT, *args, **kwargs) -> None:
        with self.lock(key):
            self[key] = self.cache_fn(*args, **kwargs)
            self._updates[key] = datetime.now()

    def lock(self, key: KT) -> RLock:
        if key not in self._locks:
            self._locks[key] = RLock()
        return self._locks[key]

    def is_valid(self, key: KT, *args, **kwargs) -> bool:
        if key not in self:
            return False
        if key not in self._updates:
            return False
        if self.validate_fn:
            kwargs.update(key=key, content=self[key], cache_version=self._updates[key])
            return self.validate_fn(*args, **kwargs)
        return True
