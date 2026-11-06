"""Reference solution for exercises/1_middle/ex02_lru_cache.py.

Hash map (key -> node) for O(1) lookup + a circular doubly linked list for
O(1) "move to front" and "drop the tail".  A single sentinel node is both
head and tail, so there are no ``if node is None`` branches anywhere.
"""


class _Node:
    __slots__ = ("key", "value", "prev", "next")  # ~3x smaller than a dict-backed object

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = self.next = self


class LRUCache:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._map = {}
        self._root = _Node()  # root.next = most recent, root.prev = least recent

    # -- linked-list primitives ---------------------------------------------
    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _push_front(self, node):
        root = self._root
        node.prev = root
        node.next = root.next
        root.next.prev = node
        root.next = node

    # -- public API -------------------------------------------------------------
    def get(self, key, default=None):
        node = self._map.get(key)  # nodes are never None, so this is unambiguous
        if node is None:
            return default
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key, value):
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return None
        node = _Node(key, value)
        self._map[key] = node
        self._push_front(node)
        if len(self._map) > self._capacity:
            lru = self._root.prev
            self._unlink(lru)
            del self._map[lru.key]
            return (lru.key, lru.value)
        return None

    def delete(self, key):
        node = self._map.pop(key, None)
        if node is None:
            return False
        self._unlink(node)
        return True

    def keys(self):
        out = []
        node = self._root.next
        while node is not self._root:
            out.append(node.key)
            node = node.next
        return out

    def __len__(self):
        return len(self._map)

    def __contains__(self, key):
        return key in self._map

    def __repr__(self):
        items = ", ".join(f"{k!r}: {self._map[k].value!r}" for k in self.keys())
        return f"LRUCache({self._capacity}, {{{items}}})"
