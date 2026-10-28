"""A fixed-capacity first-in, first-out ring buffer.

RingBuffer(capacity)
    capacity must be an int, and bool is rejected; otherwise TypeError. It must
    be at least 1; otherwise ValueError (so capacity 0 raises ValueError).
    A new buffer is empty. The capacity attribute holds the capacity.

push(item) -> evicted item or None
    Add item as the newest element. If the buffer is already full, the oldest
    element is removed first and returned; otherwise push returns None.
    Push never raises and the buffer never holds more than capacity elements.

pop() -> item
    Remove and return the oldest element. Raises IndexError if the buffer is empty.

peek() -> item
    Return the oldest element without removing it. Raises IndexError if the
    buffer is empty.

clear() -> None
    Remove all elements. The capacity is unchanged.

is_full() -> bool
    True when the buffer holds exactly capacity elements.

len(buffer) is the number of elements currently held, from 0 to capacity.

Iterating over the buffer (for x in buffer, list(buffer)) yields its elements
from oldest to newest and does not remove them. Any value, including None, may
be stored.
"""

class RingBuffer:

    def __init__(self, capacity):
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError('capacity must be an int')
        if capacity < 1:
            raise ValueError('capacity must be at least 1')
        self.capacity = capacity
        self._slots = [None] * capacity
        self._head = 0
        self._size = 0

    def push(self, item):
        evicted = None
        if self.is_full():
            evicted = self._take_oldest()
        self._slots[self._slot(self._size)] = item
        self._size += 1
        return evicted

    def pop(self):
        self._require_items()
        return self._take_oldest()

    def peek(self):
        self._require_items()
        return self._slots[self._slot(0)]

    def clear(self):
        self._slots = [None] * self.capacity
        self._head = 0
        self._size = 0

    def is_full(self):
        return self._size == self.capacity

    def __len__(self):
        return self._size

    def __iter__(self):
        return iter([self._slots[self._slot(offset)] for offset in range(self._size)])

    def _slot(self, offset):
        """Index in _slots of the element offset places after the oldest."""
        return (self._head + offset) % self.capacity

    def _take_oldest(self):
        item = self._slots[self._head]
        self._slots[self._head] = None
        self._head = (self._head + 1) % self.capacity
        self._size -= 1
        return item

    def _require_items(self):
        if self._size == 0:
            raise IndexError('buffer is empty')
