#!/usr/bin/env python3
\"\"\"Food Ordering App - single file
Usage:
  - Run interactive CLI: python food_ordering_app.py --cli
  - Run unit tests:        python food_ordering_app.py --test
  - Show demo run:         python food_ordering_app.py --demo
This single-file app contains:
  - MenuItem, Menu, OrderItem, Order, Store classes
  - JSON persistence (store_data folder)
  - Simple CLI for listing menu, creating orders, adding items, placing and cancelling orders
  - Unit tests included
Designed for Python 3.8+
\"\"\"

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

# Helper for currency rounding
def money(val):
    return Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class MenuItem:
    id: str
    name: str
    price: Decimal
    available: bool = True

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": str(self.price), "available": self.available}

    @staticmethod
    def from_dict(d):
        return MenuItem(id=d["id"], name=d["name"], price=Decimal(d["price"]), available=d.get("available", True))

class Menu:
    def __init__(self, items: Optional[List[MenuItem]] = None):
        self.items_by_id: Dict[str, MenuItem] = {}
        if items:
            for it in items:
                self.add_item(it)

    def add_item(self, item: MenuItem):
        if not item.id:
            raise ValueError("Item must have an id")
        self.items_by_id[item.id] = item

    def get_item(self, item_id: str) -> MenuItem:
        if item_id not in self.items_by_id:
            raise KeyError(f"Menu item id not found: {item_id}")
        return self.items_by_id[item_id]

    def list_available(self) -> List[MenuItem]:
        return [it for it in self.items_by_id.values() if it.available]

    def to_list(self):
        return [it.to_dict() for it in self.items_by_id.values()]

    @staticmethod
    def from_list(lst):
        items = [MenuItem.from_dict(d) for d in lst]
        return Menu(items)

@dataclass
class OrderItem:
    item_id: str
    name: str
    unit_price: Decimal
    quantity: int

    def total(self):
        return money(self.unit_price * self.quantity)

@dataclass
class Order:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    items: List[OrderItem] = field(default_factory=list)
    placed: bool = False

    def add(self, menu_item: MenuItem, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if not menu_item.available:
            raise ValueError("Item is not available")
        for oi in self.items:
            if oi.item_id == menu_item.id:
                oi.quantity += quantity
                return
        self.items.append(OrderItem(item_id=menu_item.id, name=menu_item.name, unit_price=menu_item.price, quantity=quantity))

    def subtotal(self) -> Decimal:
        return money(sum(oi.total() for oi in self.items))

    def total(self, tax_rate=Decimal("0.05"), delivery_fee=Decimal("0.00"), discount=Decimal("0.00")) -> Decimal:
        st = self.subtotal()
        tx = money(st * money(tax_rate))
        total = st + tx + money(delivery_fee) - money(discount)
        if total < 0:
            total = Decimal("0.00")
        return money(total)

    def place(self):
        if self.placed:
            raise RuntimeError("Order already placed")
        if not self.items:
            raise ValueError("Cannot place empty order")
        self.placed = True

    def to_dict(self):
        return {
            "id": self.id,
            "items": [{"item_id": it.item_id, "name": it.name, "unit_price": str(it.unit_price), "quantity": it.quantity} for it in self.items],
            "placed": self.placed
        }

    @staticmethod
    def from_dict(d):
        ord = Order(id=d["id"])
        ord.items = [OrderItem(item_id=i["item_id"], name=i["name"], unit_price=Decimal(i["unit_price"]), quantity=int(i["quantity"])) for i in d["items"]]
        ord.placed = bool(d.get("placed", False))
        return ord

class Store:
    def __init__(self, menu: Optional[Menu] = None, data_folder: str = "store_data"):
        self.menu = menu or Menu()
        self.orders: Dict[str, Order] = {}
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)
        self._orders_file = os.path.join(self.data_folder, "orders.json")
        self._menu_file = os.path.join(self.data_folder, "menu.json")
        self._load()

    def _load(self):
        try:
            if os.path.exists(self._menu_file):
                with open(self._menu_file, "r", encoding="utf-8") as f:
                    lst = json.load(f)
                    self.menu = Menu.from_list(lst)
        except Exception:
            pass
        try:
            if os.path.exists(self._orders_file):
                with open(self._orders_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for od in data:
                        o = Order.from_dict(od)
                        self.orders[o.id] = o
        except Exception:
            pass

    def _persist(self):
        tmp_menu = self._menu_file + ".tmp"
        tmp_orders = self._orders_file + ".tmp"
        try:
            with open(tmp_menu, "w", encoding="utf-8") as f:
                json.dump(self.menu.to_list(), f, indent=2)
            os.replace(tmp_menu, self._menu_file)
        except Exception:
            if os.path.exists(tmp_menu):
                try:
                    os.remove(tmp_menu)
                except Exception:
                    pass
        try:
            with open(tmp_orders, "w", encoding="utf-8") as f:
                json.dump([o.to_dict() for o in self.orders.values()], f, indent=2)
            os.replace(tmp_orders, self._orders_file)
        except Exception:
            if os.path.exists(tmp_orders):
                try:
                    os.remove(tmp_orders)
                except Exception:
                    pass

    def list_menu(self) -> List[Dict]:
        return [it.to_dict() for it in self.menu.list_available()]

    def create_order(self) -> Order:
        o = Order()
        self.orders[o.id] = o
        self._persist()
        return o

    def get_order(self, order_id: str) -> Order:
        if order_id not in self.orders:
            raise KeyError("Order id not found")
        return self.orders[order_id]

    def add_item_to_order(self, order_id: str, item_id: str, quantity: int):
        order = self.get_order(order_id)
        menu_item = self.menu.get_item(item_id)
        order.add(menu_item, quantity)
        self._persist()

    def place_order(self, order_id: str):
        order = self.get_order(order_id)
        order.place()
        self._persist()

    def cancel_order(self, order_id: str):
        order = self.get_order(order_id)
        if order.placed:
            raise RuntimeError("Cannot cancel an already placed order")
        del self.orders[order_id]
        self._persist()

# Sample menu
def sample_store(data_folder="store_data"):
    mitems = [
        MenuItem(id="m1", name="Margherita Pizza", price=money("5.99")),
        MenuItem(id="m2", name="Veg Burger", price=money("3.49")),
        MenuItem(id="m3", name="French Fries", price=money("1.99")),
        MenuItem(id="m4", name="Soft Drink", price=money("0.99")),
        MenuItem(id="m5", name="Ice Cream", price=money("1.50")),
    ]
    menu = Menu(mitems)
    return Store(menu=menu, data_folder=data_folder)

# Simple CLI - defensive input handling
def run_cli():
    store = sample_store()
    print("Welcome to the demo Food Ordering CLI")
    print("Type 'help' for commands. Data saved in folder:", store.data_folder)
    current_order_id = None
    try:
        while True:
            cmd = input(">> ").strip()
            if not cmd:
                continue
            parts = cmd.split()
            c = parts[0].lower()
            if c in ("quit", "exit"):
                print("Goodbye")
                break
            if c == "help":
                print(\"\"\"Commands:
  menu                         - list available menu items
  create                       - create a new order
  add <order_id> <item_id> <qty> - add item to order
  show <order_id>              - show order details
  place <order_id>             - place an order
  cancel <order_id>            - cancel an order (only if not placed)
  orders                       - list existing order ids
  demo                         - run a small demo order
  exit / quit                  - exit the CLI
\"\"\")
                continue
            if c == "menu":
                for it in store.list_menu():
                    print(f\"{it['id']}: {it['name']} - ₹{it['price']}\")
                continue
            if c == "create":
                o = store.create_order()
                current_order_id = o.id
                print(\"Created order id:\", o.id)
                continue
            if c == "add":
                if len(parts) != 4:
                    print(\"Usage: add <order_id> <item_id> <qty>\") 
                    continue
                oid, iid, qtys = parts[1], parts[2], parts[3]
                try:
                    qty = int(qtys)
                except Exception:
                    print(\"Quantity must be an integer\")
                    continue
                try:
                    store.add_item_to_order(oid, iid, qty)
                    print(\"Added\") 
                except Exception as e:
                    print(\"Error:\", e)
                continue
            if c == "show":
                if len(parts) != 2:
                    print(\"Usage: show <order_id>\")
                    continue
                oid = parts[1]
                try:
                    o = store.get_order(oid)
                    print(json.dumps(o.to_dict(), indent=2))
                    print(\"Subtotal:\", str(o.subtotal()))
                    print(\"Total (est):\", str(o.total()))
                except Exception as e:
                    print(\"Error:\", e)
                continue
            if c == "place":
                if len(parts) != 2:
                    print(\"Usage: place <order_id>\")
                    continue
                oid = parts[1]
                try:
                    store.place_order(oid)
                    print(\"Order placed\") 
                except Exception as e:
                    print(\"Error:\", e)
                continue
            if c == "cancel":
                if len(parts) != 2:
                    print(\"Usage: cancel <order_id>\")
                    continue
                oid = parts[1]
                try:
                    store.cancel_order(oid)
                    print(\"Order cancelled\") 
                except Exception as e:
                    print(\"Error:\", e)
                continue
            if c == "orders":
                print(list(store.orders.keys()))
                continue
            if c == "demo":
                demo(store)
                continue
            print(\"Unknown command. Type 'help'\")
    except (KeyboardInterrupt, EOFError):
        print(\"\\nExiting CLI\")


def demo(store=None):
    s = store or sample_store(data_folder="demo_store_data")
    o = s.create_order()
    s.add_item_to_order(o.id, "m1", 1)
    s.add_item_to_order(o.id, "m4", 2)
    print(\"Demo order created with id:\", o.id)
    print(json.dumps(o.to_dict(), indent=2))
    print(\"Subtotal:\", str(o.subtotal()))
    print(\"Total (est):\", str(o.total(tax_rate=Decimal('0.05'), delivery_fee=Decimal('1.20'))))
    s.place_order(o.id)
    print(\"Order placed\")


# Basic tests (run when invoked with --test)
def run_tests():
    import unittest

    class TestOrderingSystem(unittest.TestCase):
        def setUp(self):
            # use temporary folder for testing
            self.store = sample_store(data_folder=\"test_store_data_cli\")
            try:
                if os.path.exists(os.path.join(\"test_store_data_cli\", \"orders.json\")):
                    os.remove(os.path.join(\"test_store_data_cli\", \"orders.json\"))
            except Exception:
                pass

        def test_create_and_add_and_place_order(self):
            o = self.store.create_order()
            self.assertFalse(o.placed)
            self.store.add_item_to_order(o.id, \"m1\", 2)
            self.store.add_item_to_order(o.id, \"m3\", 1)
            o2 = self.store.get_order(o.id)
            self.assertEqual(len(o2.items), 2)
            subtotal = o2.subtotal()
            expected_sub = money(\"5.99\") * 2 + money(\"1.99\") * 1
            self.assertEqual(subtotal, expected_sub)
            self.store.place_order(o.id)
            self.assertTrue(self.store.get_order(o.id).placed)

        def test_invalid_add(self):
            o = self.store.create_order()
            with self.assertRaises(ValueError):
                self.store.add_item_to_order(o.id, \"m1\", 0)
            with self.assertRaises(KeyError):
                self.store.add_item_to_order(o.id, \"NO_SUCH\", 1)

        def tearDown(self):
            try:
                files = os.listdir(\"test_store_data_cli\")
                for f in files:
                    try:
                        os.remove(os.path.join(\"test_store_data_cli\", f))
                    except Exception:
                        pass
                try:
                    os.rmdir(\"test_store_data_cli\")
                except Exception:
                    pass
            except Exception:
                pass

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestOrderingSystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

def main(argv):
    if "--test" in argv:
        run_tests()
        return
    if "--demo" in argv:
        demo()
        return
    if "--cli" in argv:
        run_cli()
        return
    print(\"Food Ordering App - single file\")
    print(\"Run with --cli for interactive demo, --demo for a quick demo, --test to run unit tests.\")

if __name__ == \"__main__\":
    main(sys.argv[1:])
