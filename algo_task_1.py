from collections import OrderedDict
import random
import time
from dataclasses import dataclass
from typing import List, Any

class LRUCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self._data = OrderedDict()

    def get(self, key: Any) -> Any:
        if key in self._data:
            self._data.move_to_end(key)
            return self._data[key]
        return -1

    def put(self, key: Any, value: Any) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def keys(self):
        return list(self._data.keys())

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries

def range_sum_no_cache(array: List[int], left: int, right: int) -> int:
    return sum(array[left:right+1])

def update_no_cache(array: List[int], index: int, value: int) -> None:
    array[index] = value

@dataclass
class CacheContext:
    cache: LRUCache

def range_sum_with_cache(ctx: CacheContext, array: List[int], left: int, right: int) -> int:
    key = (left, right)
    cached = ctx.cache.get(key)
    if cached != -1:
        return cached
    result = sum(array[left:right+1])
    ctx.cache.put(key, result)
    return result

def update_with_cache(ctx: CacheContext, array: List[int], index: int, value: int) -> None:
    array[index] = value
    for (l, r) in ctx.cache.keys():
        if l <= index <= r:
            try:
                ctx.cache._data.pop((l, r), None)
            except KeyError:
                pass

def run_benchmark(n: int = 100_000, q: int = 50_000, seed: int = 42, capacity: int = 1000):
    random.seed(seed)
    array1 = [random.randint(1, 100) for _ in range(n)]
    array2 = list(array1)
    queries = make_queries(n, q)

    t0 = time.perf_counter()
    checksum = 0
    for typ, a, b in queries:
        if typ == "Range":
            checksum ^= range_sum_no_cache(array1, a, b)
        else:
            update_no_cache(array1, a, b)
    no_cache_time = time.perf_counter() - t0

    ctx = CacheContext(cache=LRUCache(capacity=capacity))
    t0 = time.perf_counter()
    checksum2 = 0
    for typ, a, b in queries:
        if typ == "Range":
            checksum2 ^= range_sum_with_cache(ctx, array2, a, b)
        else:
            update_with_cache(ctx, array2, a, b)
    with_cache_time = time.perf_counter() - t0

    print(f"Без кешу : {no_cache_time:8.2f} c")
    print(f"LRU-кеш  : {with_cache_time:8.2f} c  (прискорення ×{(no_cache_time/with_cache_time) if with_cache_time>0 else float('inf'):.2f})")
    print(f"Перевірка сум: {'OK' if checksum==checksum2 else 'MISMATCH'}")
    print(f"Розмір кешу: {len(ctx.cache._data)}/{capacity}")

if __name__ == "__main__":
    run_benchmark()
