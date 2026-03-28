"""
avl_tree.py
-----------
Self-balancing AVL Binary Search Tree keyed on (price, product_id).

Supports O(log n) insert, delete, and range queries.
Used per product category to enable sorted traversal and price-range filtering.
"""

from typing import Optional, List, Tuple


class AVLNode:
    """
    A single node in the AVL tree.

    Attributes
    ----------
    key : tuple
        (price, product_id) – price is the primary sort key.
    height : int
        Height of this node's subtree (leaf = 1).
    left, right : AVLNode or None
        Child pointers.
    """

    __slots__ = ("key", "height", "left", "right")

    def __init__(self, key: Tuple):
        self.key = key          # (price, product_id)
        self.height = 1
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None


# ------------------------------------------------------------------
# Module-level helper functions (operate on nodes, not a class instance)
# ------------------------------------------------------------------

def _height(node: Optional[AVLNode]) -> int:
    return node.height if node else 0


def _balance_factor(node: Optional[AVLNode]) -> int:
    if node is None:
        return 0
    return _height(node.left) - _height(node.right)


def _update_height(node: AVLNode) -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_right(y: AVLNode) -> AVLNode:
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    _update_height(y)
    _update_height(x)
    return x


def _rotate_left(x: AVLNode) -> AVLNode:
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    _update_height(x)
    _update_height(y)
    return y


def _rebalance(node: AVLNode) -> AVLNode:
    """Apply rotations to restore AVL balance property."""
    _update_height(node)
    bf = _balance_factor(node)

    # Left-heavy
    if bf > 1:
        if _balance_factor(node.left) < 0:          # Left-Right case
            node.left = _rotate_left(node.left)
        return _rotate_right(node)

    # Right-heavy
    if bf < -1:
        if _balance_factor(node.right) > 0:         # Right-Left case
            node.right = _rotate_right(node.right)
        return _rotate_left(node)

    return node


def _insert(node: Optional[AVLNode], key: Tuple) -> AVLNode:
    if node is None:
        return AVLNode(key)
    if key < node.key:
        node.left = _insert(node.left, key)
    elif key > node.key:
        node.right = _insert(node.right, key)
    else:
        # Duplicate key – no-op (key is (price, product_id), so collisions rare)
        return node
    return _rebalance(node)


def _min_node(node: AVLNode) -> AVLNode:
    """Return the leftmost (minimum) node."""
    while node.left:
        node = node.left
    return node


def _delete(node: Optional[AVLNode], key: Tuple) -> Optional[AVLNode]:
    if node is None:
        return None
    if key < node.key:
        node.left = _delete(node.left, key)
    elif key > node.key:
        node.right = _delete(node.right, key)
    else:
        # Node to delete found
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        # Replace with in-order successor
        successor = _min_node(node.right)
        node.key = successor.key
        node.right = _delete(node.right, successor.key)
    return _rebalance(node)


def _range_query(node: Optional[AVLNode], lo: Tuple, hi: Tuple, result: List) -> None:
    """Collect all keys k where lo <= k <= hi via in-order traversal."""
    if node is None:
        return
    if lo < node.key:
        _range_query(node.left, lo, hi, result)
    if lo <= node.key <= hi:
        result.append(node.key)
    if node.key < hi:
        _range_query(node.right, lo, hi, result)


def _inorder(node: Optional[AVLNode], result: List) -> None:
    if node is None:
        return
    _inorder(node.left, result)
    result.append(node.key)
    _inorder(node.right, result)


# ------------------------------------------------------------------
# Public AVLTree class
# ------------------------------------------------------------------

class AVLTree:
    """
    AVL tree for a single product category, keyed on (price, product_id).

    All public methods maintain the AVL balance invariant automatically.
    """

    def __init__(self):
        self._root: Optional[AVLNode] = None
        self._size: int = 0

    def insert(self, price: float, product_id: str) -> None:
        """
        Insert a product into the tree.

        Parameters
        ----------
        price : float
            Product price (primary sort key).
        product_id : str
            Product SKU (tie-breaker).
        """
        key = (price, product_id)
        new_root = _insert(self._root, key)
        if new_root is not self._root or self._root is None:
            self._size += 1
        self._root = new_root

    def delete(self, price: float, product_id: str) -> None:
        """
        Remove a product from the tree.

        Parameters
        ----------
        price : float
        product_id : str
        """
        key = (price, product_id)
        self._root = _delete(self._root, key)
        self._size -= 1

    def range_query(self, lo_price: float, hi_price: float) -> List[Tuple]:
        """
        Return all (price, product_id) pairs where lo_price <= price <= hi_price,
        in ascending price order.

        Parameters
        ----------
        lo_price : float
        hi_price : float

        Returns
        -------
        list of tuple
            Sorted list of (price, product_id).
        """
        result: List[Tuple] = []
        lo = (lo_price, "")
        hi = (hi_price, "\uffff")   # unicode max char ensures all IDs at hi_price are included
        _range_query(self._root, lo, hi, result)
        return result

    def inorder(self) -> List[Tuple]:
        """Return all (price, product_id) pairs in ascending order."""
        result: List[Tuple] = []
        _inorder(self._root, result)
        return result

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"AVLTree(size={self._size}, height={_height(self._root)})" 