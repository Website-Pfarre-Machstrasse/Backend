from datetime import datetime
from threading import RLock


class CacheDict(dict):
    _locks = {}
    _updates = {}

    def __init__(self, cache_fn, validate_fn=None):
        super().__init__()
        self.cache_fn = cache_fn
        self.validate_fn = validate_fn

    def invalidate(self, key):
        self.pop(key)

    def cache(self, key, *args, **kwargs):
        with self.lock(key):
            self[key] = self.cache_fn(*args, **kwargs)
            self._updates[key] = datetime.now()

    def lock(self, key):
        if key not in self._locks:
            self._locks[key] = RLock()
        return self._locks[key]

    def should_cache(self, key, *args, **kwargs):
        if key not in self:
            return True
        if key not in self._updates:
            return True
        if self.validate_fn:
            kwargs.update(key=key, content=self[key], cache_version=self._updates[key])
            return not self.validate_fn(*args, **kwargs)
        return False
