"""Reference solution for sliding_median. The spec is the docstring in stub.py.

Two heaps with lazy deletion: `low` (a max-heap, stored negated) holds the smaller half
and `high` the larger half. `size` counts the live elements in each; heap tops are
always live.
"""

import heapq
from fractions import Fraction


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


class Window:
    def __init__(self):
        self.low, self.high = [], []
        self.size = {"low": 0, "high": 0}
        self.pending = {}

    def prune(self, heap, sign):
        while heap and self.pending.get(sign * heap[0], 0):
            self.pending[sign * heapq.heappop(heap)] -= 1

    def balance(self):
        if self.size["low"] > self.size["high"] + 1:
            heapq.heappush(self.high, -heapq.heappop(self.low))
            self.size["low"] -= 1
            self.size["high"] += 1
            self.prune(self.low, -1)
        elif self.size["low"] < self.size["high"]:
            heapq.heappush(self.low, -heapq.heappop(self.high))
            self.size["high"] -= 1
            self.size["low"] += 1
            self.prune(self.high, 1)

    def add(self, value):
        if not self.low or value <= -self.low[0]:
            heapq.heappush(self.low, -value)
            self.size["low"] += 1
        else:
            heapq.heappush(self.high, value)
            self.size["high"] += 1
        self.balance()

    def remove(self, value):
        self.pending[value] = self.pending.get(value, 0) + 1
        if value <= -self.low[0]:
            self.size["low"] -= 1
            self.prune(self.low, -1)
        else:
            self.size["high"] -= 1
            self.prune(self.high, 1)
        self.balance()

    def median(self, k):
        if k % 2:
            return -self.low[0]
        total = -self.low[0] + self.high[0]
        return total // 2 if total % 2 == 0 else Fraction(total, 2)


def sliding_median(nums, k):
    if not isinstance(nums, list) or not all(is_int(x) for x in nums):
        raise TypeError("nums must be a list of int")
    if not is_int(k):
        raise TypeError("k must be an int")
    if k < 1 or k > len(nums):
        raise ValueError("k must be between 1 and len(nums)")
    window, result = Window(), []
    for i, value in enumerate(nums):
        window.add(value)
        if i >= k:
            window.remove(nums[i - k])
        if i >= k - 1:
            result.append(window.median(k))
    return result
