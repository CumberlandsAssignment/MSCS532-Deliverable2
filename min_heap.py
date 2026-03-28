"""
min_heap.py
-----------
Binary min-heap priority queue for reorder alerting.

Each entry is (current_quantity, product_id). The product with the lowest
stock level is always accessible at the top of the heap in O(1) time.
Lazy deletion is used: when a product's quantity changes, a new entry is
pushed; stale entries are skipped at extraction time.
"""

import heapq
from typing import List, Tuple, Optional


class MinHeap:
    """
    Binary min-heap wrapping Python's heapq module.

    Uses lazy deletion to handle quantity updates without costly
    heap restructuring.

    Attributes
    ----------
    _heap : list
        Internal heap array of (quantity, product_id) tuples.
    _valid : dict
        Maps product_id -> current valid quantity.
        Entries not matching _heap entries are stale and skipped.
    """

    def __init__(self):
        self._heap: List[Tuple] = []
        # Maps product_id -> most recent quantity added
        self._valid: dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def push(self, quantity: int, product_id: str) -> None:
        """
        Add or update a product's stock level.

        When a product already exists, its old heap entry becomes stale
        and will be skipped during extraction.

        Parameters
        ----------
        quantity : int
            Current stock quantity.
        product_id : str
            Product SKU.
        """
        self._valid[product_id] = quantity
        heapq.heappush(self._heap, (quantity, product_id))

    def peek(self) -> Optional[Tuple]:
        """
        Return (quantity, product_id) of the lowest-stock product without removing it.

        Returns
        -------
        tuple or None
        """
        self._skip_stale()
        if self._heap:
            return self._heap[0]
        return None

    def extract_min(self) -> Optional[Tuple]:
        """
        Remove and return the product with the lowest stock level.

        Returns
        -------
        tuple or None
            (quantity, product_id) or None if heap is empty.
        """
        while self._heap:
            qty, pid = heapq.heappop(self._heap)
            # Check whether this entry is still valid
            if pid in self._valid and self._valid[pid] == qty:
                del self._valid[pid]
                return (qty, pid)
            # Stale entry – skip it
        return None

    def top_k(self, k: int) -> List[Tuple]:
        """
        Return the k products with the lowest stock levels, in ascending order.

        Does NOT remove items from the heap.

        Parameters
        ----------
        k : int
            Number of lowest-stock items to return.

        Returns
        -------
        list of (quantity, product_id)
        """
        results = []
        temp = []          # entries popped during this call
        seen_ids = set()

        while self._heap and len(results) < k:
            qty, pid = heapq.heappop(self._heap)
            temp.append((qty, pid))
            if pid in self._valid and self._valid[pid] == qty and pid not in seen_ids:
                results.append((qty, pid))
                seen_ids.add(pid)

        # Restore all popped entries back into the heap
        for entry in temp:
            heapq.heappush(self._heap, entry)

        return results

    def remove(self, product_id: str) -> None:
        """
        Logically remove a product from the heap via lazy deletion.

        Parameters
        ----------
        product_id : str
        """
        if product_id in self._valid:
            del self._valid[product_id]

    def __len__(self) -> int:
        return len(self._valid)   # count of active (non-stale) entries

    def __repr__(self) -> str:
        return f"MinHeap(active={len(self)}, raw_heap_size={len(self._heap)})"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _skip_stale(self) -> None:
        """Pop and discard stale entries from the top of the heap."""
        while self._heap:
            qty, pid = self._heap[0]
            if pid in self._valid and self._valid[pid] == qty:
                break
            heapq.heappop(self._heap)