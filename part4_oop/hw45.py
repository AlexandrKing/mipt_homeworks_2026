from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, overload

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key, None)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5) -> None:
        self.capacity = capacity
        self._order = []

    def register_access(self, key: K) -> None:
        # if key not in self._order:
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if not self.has_keys:
            return None
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5) -> None:
        self.capacity = capacity
        self._order = []

    def register_access(self, key: K) -> None:
        if key in self._order:
            self.remove_key(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if not self.has_keys:
            return None
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _order: list[K] = field(default_factory=list, init=False)

    def __init__(self, capacity: int = 5) -> None:
        self.capacity = capacity
        self._order = []
        self._key_counter = {}

    def register_access(self, key: K) -> None:
        counter = self._key_counter.get(key, 0)

        if counter == 0:
            self._order.append(key)

        self._key_counter[key] = counter + 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) <= self.capacity:
            return None

        return self._get_keys_with_min_freq()[0]

    def remove_key(self, key: K) -> None:
        if key in self._key_counter:
            self._key_counter.pop(key)
            self._order.remove(key)

    def clear(self) -> None:
        self._key_counter.clear()
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0

    def _get_keys_with_min_freq(self) -> list[K]:
        min_count = min(self._key_counter.values())
        return [key for key in self._order if self._key_counter[key] == min_count]


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)
        returned_key = self.policy.get_key_to_evict()
        if returned_key is not None:
            self.storage.remove(returned_key)
            self.policy.remove_key(returned_key)

    def get(self, key: K) -> V | None:
        value = self.storage.get(key)
        if value is not None:
            self.policy.register_access(key)
        return value

    def exists(self, key: K) -> bool:
        exist_key = self.storage.exists(key)
        if exist_key:
            self.policy.register_access(key)
        return exist_key

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "CachedProperty[V]": ...

    @overload
    def __get__(self, instance: HasCache[str, V], owner: type[Any]) -> V: ...

    def __get__(
        self,
        instance: HasCache[str, V] | None,
        owner: type[Any],
    ) -> "CachedProperty[V] | V":
        if instance is None:
            return self

        cache_key = self.func.__name__
        if instance.cache.exists(cache_key):
            cached_value = instance.cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        value = self.func(instance)
        instance.cache.set(cache_key, value)
        return value
