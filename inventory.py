"""
inventory.py
------------
InventoryManager: integrates HashTable, AVLTree, and MinHeap into a
unified Inventory Management System backend.

Public Methods
--------------
add_product(product)           – insert or update a product record
get_product(sku)               – retrieve product by SKU
delete_product(sku)            – remove product from all structures
reorder_alerts(top_k)          – list top-k lowest-stock products
list_by_price(category, lo, hi)– sorted products in a price range
"""

from hash_table import HashTable
from avl_tree import AVLTree
from min_heap import MinHeap
from typing import Dict, List, Optional, Any


class InventoryManager:
    """
    Coordinates the three data structures for inventory operations.

    Internal layout
    ---------------
    _products  : HashTable  – SKU -> product dict
    _categories: HashTable  – category_name -> AVLTree(price, SKU)
    _heap      : MinHeap    – (quantity, SKU) for reorder alerts
    """

    def __init__(self):
        self._products = HashTable(initial_capacity=17)
        self._categories = HashTable(initial_capacity=17)
        self._heap = MinHeap()

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add_product(self, product: Dict[str, Any]) -> None:
        """
        Insert a new product or update an existing one.

        Parameters
        ----------
        product : dict
            Must contain keys: 'sku' (str), 'name' (str), 'category' (str),
            'price' (float), 'quantity' (int).
            Optional: 'reorder_level' (int, default 10).

        Raises
        ------
        ValueError
            If required keys are missing.
        """
        required = {"sku", "name", "category", "price", "quantity"}
        missing = required - product.keys()
        if missing:
            raise ValueError(f"Product missing required fields: {missing}")

        sku = product["sku"]
        category = product["category"]
        price = float(product["price"])
        quantity = int(product["quantity"])
        product.setdefault("reorder_level", 10)

        # --- Handle update: remove old AVL entry if price/category changed ---
        existing = self._products.search(sku)
        if existing:
            old_cat = existing["category"]
            old_price = existing["price"]
            old_tree = self._categories.search(old_cat)
            if old_tree:
                try:
                    old_tree.delete(old_price, sku)
                except Exception:
                    pass

        # --- Hash table update ---
        self._products.insert(sku, product)

        # --- AVL tree update ---
        tree = self._categories.search(category)
        if tree is None:
            tree = AVLTree()
            self._categories.insert(category, tree)
        tree.insert(price, sku)

        # --- Min-heap update (lazy) ---
        self._heap.push(quantity, sku)

    def get_product(self, sku: str) -> Optional[Dict]:
        """
        Retrieve a product record by SKU.

        Parameters
        ----------
        sku : str

        Returns
        -------
        dict or None
        """
        return self._products.search(sku)

    def delete_product(self, sku: str) -> bool:
        """
        Remove a product from all three data structures.

        Parameters
        ----------
        sku : str

        Returns
        -------
        bool
            True if product was found and deleted.
        """
        product = self._products.search(sku)
        if product is None:
            return False

        # Remove from AVL tree
        tree = self._categories.search(product["category"])
        if tree:
            try:
                tree.delete(product["price"], sku)
            except Exception:
                pass

        # Lazy-remove from heap
        self._heap.remove(sku)

        # Remove from hash table
        self._products.delete(sku)
        return True

    def reorder_alerts(self, top_k: int = 5) -> List[Dict]:
        """
        Return the top_k products with the lowest stock quantities.

        Parameters
        ----------
        top_k : int

        Returns
        -------
        list of dict
            Product records sorted by ascending quantity.
        """
        entries = self._heap.top_k(top_k)
        results = []
        for qty, sku in entries:
            p = self._products.search(sku)
            if p:
                results.append(p)
        return results

    def list_by_price(self, category: str, lo: float = 0.0,
                      hi: float = float("inf")) -> List[Dict]:
        """
        Return all products in a category with price in [lo, hi], sorted ascending.

        Parameters
        ----------
        category : str
        lo : float
        hi : float

        Returns
        -------
        list of dict
        """
        tree = self._categories.search(category)
        if tree is None:
            return []
        keys = tree.range_query(lo, hi)
        results = []
        for _, sku in keys:
            p = self._products.search(sku)
            if p:
                results.append(p)
        return results

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def product_count(self) -> int:
        return len(self._products)

    def __repr__(self) -> str:
        return f"InventoryManager(products={self.product_count()})"