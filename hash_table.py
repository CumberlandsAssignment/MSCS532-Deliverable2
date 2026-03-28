"""
hash_table.py
-------------
Hash table with open addressing (linear probing) for O(1) average-case
product lookup by SKU in the Inventory Management System.

Rehashes automatically when load factor exceeds 0.7.
"""

_DELETED = object()  # sentinel for lazy deletion slots


class HashTable:
    """
    Open-addressing hash table with linear probing.

    Parameters
    ----------
    initial_capacity : int
        Starting number of slots (should be prime for better distribution).

    Attributes
    ----------
    capacity : int
        Current number of slots in the internal array.
    size : int
        Number of active (non-deleted) key-value pairs stored.
    """

    _PRIMES = [17, 37, 79, 163, 331, 673, 1361, 2729, 5471, 10949, 21911]

    def __init__(self, initial_capacity: int = 17):
        self.capacity = initial_capacity
        self.size = 0
        self._slots: list = [None] * self.capacity

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _hash(self, key: str) -> int:
        """Compute slot index using Python's built-in SipHash-1-3."""
        return hash(key) % self.capacity

    def _probe(self, key: str):
        """
        Linear probing: return the index where key lives or should be inserted.

        Returns
        -------
        tuple[int, bool]
            (index, found) – found=True if key already exists.
        """
        idx = self._hash(key)
        first_deleted = None

        for _ in range(self.capacity):
            slot = self._slots[idx]

            if slot is None:
                # Empty slot – key definitely not present
                return (first_deleted if first_deleted is not None else idx, False)
            if slot is _DELETED:
                if first_deleted is None:
                    first_deleted = idx
            elif slot[0] == key:
                return (idx, True)

            idx = (idx + 1) % self.capacity

        # Table full (should not happen if load factor is controlled)
        return (first_deleted, False)

    def _rehash(self):
        """Double capacity and reinsert all live entries."""
        old_slots = self._slots
        # Pick next prime larger than 2 * current capacity
        new_cap = self.capacity * 2 + 1
        for p in self._PRIMES:
            if p > new_cap:
                new_cap = p
                break

        self.capacity = new_cap
        self.size = 0
        self._slots = [None] * self.capacity

        for slot in old_slots:
            if slot is not None and slot is not _DELETED:
                self.insert(slot[0], slot[1])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, key: str, value) -> None:
        """
        Insert or update a key-value pair.

        Parameters
        ----------
        key : str
            Product SKU or unique identifier.
        value : any
            Product record (dict or Product object).
        """
        if self.size / self.capacity >= 0.7:
            self._rehash()

        idx, found = self._probe(key)
        if not found:
            self.size += 1
        self._slots[idx] = (key, value)

    def search(self, key: str):
        """
        Retrieve the value associated with key.

        Parameters
        ----------
        key : str
            Product SKU.

        Returns
        -------
        any or None
            The stored value, or None if not found.
        """
        idx, found = self._probe(key)
        if found:
            return self._slots[idx][1]
        return None

    def delete(self, key: str) -> bool:
        """
        Remove a key-value pair using lazy deletion (tombstone).

        Parameters
        ----------
        key : str
            Product SKU to remove.

        Returns
        -------
        bool
            True if the key was found and deleted, False otherwise.
        """
        idx, found = self._probe(key)
        if found:
            self._slots[idx] = _DELETED
            self.size -= 1
            return True
        return False

    def load_factor(self) -> float:
        """Return current load factor (size / capacity)."""
        return self.size / self.capacity

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"HashTable(size={self.size}, capacity={self.capacity}, load={self.load_factor():.2f})"