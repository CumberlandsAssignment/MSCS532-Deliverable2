"""
main.py
-------
Demonstration and test suite for the Inventory Management System.

Covers:
  1. Normal insertions and lookups
  2. Duplicate SKU (update) behavior
  3. Reorder alerts (min-heap)
  4. Price-range queries (AVL tree)
  5. Edge cases: empty inventory, SKU not found, single-item heap, deletion
"""

from inventory import InventoryManager


# -----------------------------------------------------------------------
# ANSI colour helpers for readable console output
# -----------------------------------------------------------------------
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

PASS = f"{GREEN}PASS{RESET}"
FAIL = f"{RED}FAIL{RESET}"


def header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def check(description: str, condition: bool) -> None:
    status = PASS if condition else FAIL
    print(f"  [{status}] {description}")


# -----------------------------------------------------------------------
# Sample product catalogue
# -----------------------------------------------------------------------
SAMPLE_PRODUCTS = [
    {"sku": "ELEC-001", "name": "Laptop Pro 15",       "category": "Electronics", "price": 1299.99, "quantity": 8,  "reorder_level": 10},
    {"sku": "ELEC-002", "name": "Wireless Headphones",  "category": "Electronics", "price": 89.99,  "quantity": 3,  "reorder_level": 10},
    {"sku": "ELEC-003", "name": "USB-C Hub",            "category": "Electronics", "price": 49.99,  "quantity": 25, "reorder_level": 10},
    {"sku": "ELEC-004", "name": "4K Monitor",           "category": "Electronics", "price": 399.99, "quantity": 15, "reorder_level": 10},
    {"sku": "ELEC-005", "name": "Mechanical Keyboard",  "category": "Electronics", "price": 149.99, "quantity": 2,  "reorder_level": 10},
    {"sku": "CLTH-001", "name": "Running Shoes",        "category": "Clothing",    "price": 120.00, "quantity": 50, "reorder_level": 20},
    {"sku": "CLTH-002", "name": "Winter Jacket",        "category": "Clothing",    "price": 220.00, "quantity": 1,  "reorder_level": 10},
    {"sku": "CLTH-003", "name": "Cotton T-Shirt",       "category": "Clothing",    "price": 25.00,  "quantity": 4,  "reorder_level": 10},
    {"sku": "GROC-001", "name": "Organic Coffee 1kg",   "category": "Grocery",     "price": 18.99,  "quantity": 0,  "reorder_level": 5},
    {"sku": "GROC-002", "name": "Almond Milk 1L",       "category": "Grocery",     "price": 4.99,   "quantity": 12, "reorder_level": 5},
]


# -----------------------------------------------------------------------
# Test Suites
# -----------------------------------------------------------------------

def test_insertion_and_lookup(mgr: InventoryManager) -> None:
    header("TEST 1 — Insertion and Lookup")

    for p in SAMPLE_PRODUCTS:
        mgr.add_product(p)
    print(f"  Inserted {len(SAMPLE_PRODUCTS)} products.")
    print(f"  {mgr}")

    result = mgr.get_product("ELEC-001")
    check("get_product('ELEC-001') returns correct name",
          result is not None and result["name"] == "Laptop Pro 15")

    result2 = mgr.get_product("GROC-002")
    check("get_product('GROC-002') price == 4.99",
          result2 is not None and result2["price"] == 4.99)

    result3 = mgr.get_product("CLTH-001")
    check("get_product('CLTH-001') category == 'Clothing'",
          result3 is not None and result3["category"] == "Clothing")


def test_update_duplicate_sku(mgr: InventoryManager) -> None:
    header("TEST 2 — Duplicate SKU (Update Behavior)")

    updated = {"sku": "ELEC-001", "name": "Laptop Pro 15 Updated",
               "category": "Electronics", "price": 1199.99, "quantity": 20}
    mgr.add_product(updated)

    result = mgr.get_product("ELEC-001")
    check("Name updated to 'Laptop Pro 15 Updated'",
          result["name"] == "Laptop Pro 15 Updated")
    check("Price updated to 1199.99",
          result["price"] == 1199.99)
    check("Quantity updated to 20",
          result["quantity"] == 20)
    check("Product count unchanged (no duplicate entry)",
          mgr.product_count() == len(SAMPLE_PRODUCTS))


def test_reorder_alerts(mgr: InventoryManager) -> None:
    header("TEST 3 — Reorder Alerts (Min-Heap)")

    alerts = mgr.reorder_alerts(top_k=5)
    print(f"  Top-5 low-stock products:")
    for p in alerts:
        flag = f"{RED}CRITICAL{RESET}" if p["quantity"] == 0 else f"{YELLOW}LOW{RESET}"
        print(f"    {flag}  {p['sku']:12s}  qty={p['quantity']:>3}  {p['name']}")

    skus_in_alert = [p["sku"] for p in alerts]
    check("GROC-001 (qty=0) appears in top-5 alerts",  "GROC-001" in skus_in_alert)
    check("CLTH-002 (qty=1) appears in top-5 alerts",  "CLTH-002" in skus_in_alert)
    check("ELEC-005 (qty=2) appears in top-5 alerts",  "ELEC-005" in skus_in_alert)
    check("ELEC-002 (qty=3) appears in top-5 alerts",  "ELEC-002" in skus_in_alert)
    check("Alerts ordered by ascending quantity",
          alerts == sorted(alerts, key=lambda p: p["quantity"]))


def test_range_query(mgr: InventoryManager) -> None:
    header("TEST 4 — Price Range Query (AVL Tree)")

    results = mgr.list_by_price("Electronics", lo=50.0, hi=400.0)
    prices = [p["price"] for p in results]
    print(f"  Electronics $50–$400:")
    for p in results:
        print(f"    {p['sku']:12s}  ${p['price']:>8.2f}  {p['name']}")

    check("All returned prices are within [50, 400]",
          all(50.0 <= pr <= 400.0 for pr in prices))
    check("Results are in ascending price order",
          prices == sorted(prices))
    check("ELEC-003 ($49.99) is NOT included (below lo)",
          all(p["sku"] != "ELEC-003" for p in results))
    check("ELEC-001 ($1199.99 after update) is NOT included (above hi)",
          all(p["sku"] != "ELEC-001" for p in results))

    clothing = mgr.list_by_price("Clothing", lo=0, hi=300)
    check("All 3 clothing items returned in price range $0–$300",
          len(clothing) == 3)


def test_deletion(mgr: InventoryManager) -> None:
    header("TEST 5 — Deletion")

    removed = mgr.delete_product("GROC-001")
    check("delete_product('GROC-001') returns True", removed)
    check("get_product('GROC-001') returns None after deletion",
          mgr.get_product("GROC-001") is None)
    check("Product count decremented",
          mgr.product_count() == len(SAMPLE_PRODUCTS) - 1)

    # Deleted product should not appear in reorder alerts
    alerts = mgr.reorder_alerts(top_k=10)
    skus = [p["sku"] for p in alerts]
    check("GROC-001 absent from reorder alerts after deletion",
          "GROC-001" not in skus)


def test_edge_cases(mgr: InventoryManager) -> None:
    header("TEST 6 — Edge Cases")

    # Lookup non-existent SKU
    result = mgr.get_product("FAKE-999")
    check("get_product on unknown SKU returns None", result is None)

    # Delete non-existent SKU
    removed = mgr.delete_product("FAKE-999")
    check("delete_product on unknown SKU returns False", not removed)

    # Range query on non-existent category
    results = mgr.list_by_price("NonexistentCategory", 0, 1000)
    check("list_by_price on unknown category returns []", results == [])

    # Empty reorder alerts when heap is exhausted
    empty_mgr = InventoryManager()
    alerts = empty_mgr.reorder_alerts(top_k=5)
    check("reorder_alerts on empty inventory returns []", alerts == [])

    # Single-item inventory
    single_mgr = InventoryManager()
    single_mgr.add_product({"sku": "X1", "name": "Solo Item",
                             "category": "Test", "price": 9.99, "quantity": 0})
    alert = single_mgr.reorder_alerts(top_k=1)
    check("Single-item heap: alert correctly identifies sole product",
          len(alert) == 1 and alert[0]["sku"] == "X1")

    # Missing required field raises ValueError
    try:
        mgr.add_product({"sku": "BAD-001", "name": "No Price"})
        check("ValueError raised for missing fields", False)
    except ValueError:
        check("ValueError raised for missing required fields", True)


def test_hash_table_rehash() -> None:
    header("TEST 7 — Hash Table Rehashing")
    from hash_table import HashTable
    ht = HashTable(initial_capacity=17)
    # Insert enough items to trigger rehash (>= 0.7 * 17 = ~12 items)
    initial_capacity = ht.capacity
    for i in range(20):
        ht.insert(f"key_{i}", i)

    check("Capacity increased after rehash", ht.capacity > initial_capacity)
    check("All 20 items still accessible after rehash",
          all(ht.search(f"key_{i}") == i for i in range(20)))
    check("Load factor stays below 0.7 after rehash", ht.load_factor() < 0.7)


def test_avl_tree_balance() -> None:
    header("TEST 8 — AVL Tree Balance")
    from avl_tree import AVLTree, _height
    tree = AVLTree()
    # Insert in sorted order – a plain BST would degenerate to O(n)
    prices = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    for p in prices:
        tree.insert(p, f"sku_{int(p)}")

    import math
    max_height = math.floor(1.44 * math.log2(len(prices) + 2))
    actual_height = _height(tree._root)
    check(f"AVL height ({actual_height}) within O(log n) bound ({max_height})",
          actual_height <= max_height)

    result = tree.inorder()
    check("Inorder traversal returns sorted prices",
          [k[0] for k in result] == sorted(prices))

    result_range = tree.range_query(20.0, 50.0)
    check("Range query [20, 50] returns exactly 4 items", len(result_range) == 4)


# -----------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------

if __name__ == "__main__":
    print(f"\n{BOLD}Inventory Management System — Phase 2 Proof of Concept{RESET}")
    print(f"{'─'*60}")

    mgr = InventoryManager()

    test_insertion_and_lookup(mgr)
    test_update_duplicate_sku(mgr)
    test_reorder_alerts(mgr)
    test_range_query(mgr)
    test_deletion(mgr)
    test_edge_cases(mgr)
    test_hash_table_rehash()
    test_avl_tree_balance()

    print(f"\n{BOLD}{'─'*60}")
    print(f"All tests complete.{RESET}\n")