#!/usr/bin/env python3
"""
MyShop - Inventory, Sales and Restocking Management System
BIT | Programming I with Python | Group Project
"""

# ─── Standard library imports ─────────────────────────────────────────────────
import json
import os
import sys
from datetime import datetime
from typing import Optional

# ─── Constants ────────────────────────────────────────────────────────────────
DATA_FILE: str = "shop_data.json"
CATEGORIES: tuple = ("Food", "Beverages", "Hygiene", "Electronics", "Clothing", "Other")
APP_VERSION: str = "1.0.0"
APP_NAME: str = "MyShop"


# ─── Terminal colors (ANSI) ───────────────────────────────────────────────────
class Colors:
    """ANSI escape codes for terminal color output."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GRAY   = "\033[90m"


# ─── Helper print functions ───────────────────────────────────────────────────
def print_ok(msg: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.GREEN}  ✔ {msg}{Colors.RESET}")

def print_err(msg: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.RED}  ✘ {msg}{Colors.RESET}")

def print_info(msg: str) -> None:
    """Print an info message in cyan."""
    print(f"{Colors.CYAN}  ℹ {msg}{Colors.RESET}")

def print_warn(msg: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}  ⚠ {msg}{Colors.RESET}")

def separator(title: str = "", char: str = "─") -> None:
    """Print a styled separator line, optionally with a centered title."""
    width: int = 62
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{Colors.BOLD}{Colors.BLUE}{char * pad} {title} {char * (width - pad - len(title) - 2)}{Colors.RESET}")
    else:
        print(f"{Colors.GRAY}{char * width}{Colors.RESET}")

def fmt(n: float) -> str:
    """Format a number with thousands separator."""
    return f"{n:,.0f}".replace(",", " ")

def pause() -> None:
    """Wait for the user to press Enter before continuing."""
    input(f"\n  {Colors.GRAY}[Press Enter to continue]{Colors.RESET}")


# ─── Input helpers ────────────────────────────────────────────────────────────
def input_int(prompt: str, mini: int = 0, maxi: Optional[int] = None) -> int:
    """
    Prompt the user for an integer input within an optional range.

    Args:
        prompt: The message shown to the user.
        mini:   Minimum accepted value (inclusive).
        maxi:   Maximum accepted value (inclusive), or None for no limit.

    Returns:
        A valid integer entered by the user.
    """
    while True:
        try:
            val: int = int(input(prompt))
            if val < mini:
                print_err(f"Minimum value: {mini}")
                continue
            if maxi is not None and val > maxi:
                print_err(f"Maximum value: {maxi}")
                continue
            return val
        except ValueError:
            print_err("Please enter a whole number.")

def input_float(prompt: str, mini: float = 0.0) -> float:
    """
    Prompt the user for a float input with a minimum value.

    Args:
        prompt: The message shown to the user.
        mini:   Minimum accepted value (inclusive).

    Returns:
        A valid float entered by the user.
    """
    while True:
        try:
            val: float = float(input(prompt))
            if val < mini:
                print_err(f"Minimum value: {mini}")
                continue
            return val
        except ValueError:
            print_err("Please enter a valid number.")


# ─── OOP: Base class ──────────────────────────────────────────────────────────
class ShopItem:
    """
    Base class representing a generic item in the shop.

    Attributes:
        item_id (int):   Unique identifier for the item.
        name    (str):   Name of the item.
        stock   (int):   Current quantity in stock.
    """

    def __init__(self, item_id: int, name: str, stock: int) -> None:
        """
        Initialise a ShopItem.

        Args:
            item_id: Unique numeric identifier.
            name:    Display name of the item.
            stock:   Initial stock quantity.
        """
        # Encapsulation: attributes are managed through this class
        self._item_id: int = item_id
        self._name: str    = name
        self._stock: int   = stock

    # ── Properties (encapsulation: controlled access to private attributes) ──
    @property
    def item_id(self) -> int:
        """Return the item's unique ID."""
        return self._item_id

    @property
    def name(self) -> str:
        """Return the item's name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the item's name if non-empty."""
        if value.strip():
            self._name = value.strip()

    @property
    def stock(self) -> int:
        """Return the current stock level."""
        return self._stock

    @stock.setter
    def stock(self, value: int) -> None:
        """Set stock, preventing negative values."""
        self._stock = max(0, value)

    def add_stock(self, quantity: int) -> None:
        """
        Increase stock by a given quantity.

        Args:
            quantity: Number of units to add (must be positive).
        """
        if quantity > 0:
            self._stock += quantity

    def remove_stock(self, quantity: int) -> bool:
        """
        Decrease stock by a given quantity if available.

        Args:
            quantity: Number of units to remove.

        Returns:
            True if successful, False if insufficient stock.
        """
        if quantity <= self._stock:
            self._stock -= quantity
            return True
        return False

    def get_status(self) -> str:
        """
        Return a plain-text stock status label.
        Polymorphism: overridden in child classes for different behaviour.

        Returns:
            A string describing the stock status.
        """
        return "IN STOCK" if self._stock > 0 else "OUT OF STOCK"

    def display(self) -> str:
        """
        Return a formatted one-line summary of this item.
        Abstraction: caller does not need to know how formatting works.

        Returns:
            A string summary of the item.
        """
        return f"[{self._item_id}] {self._name} — stock: {self._stock}"

    def to_dict(self) -> dict:
        """
        Serialise the item to a dictionary for JSON storage.

        Returns:
            A dictionary with item data.
        """
        return {
            "id":    self._item_id,
            "name":  self._name,
            "stock": self._stock,
        }


# ─── OOP: Child class ─────────────────────────────────────────────────────────
class Product(ShopItem):
    """
    A sellable product in the shop. Inherits from ShopItem.

    Extends ShopItem with pricing, category, sales tracking,
    and a stock threshold for restock alerts.

    Attributes:
        category   (str):   Product category.
        sell_price (float): Price charged to the customer.
        buy_price  (float): Price paid to the supplier.
        threshold  (int):   Minimum stock before an alert is triggered.
        total_sold (int):   Cumulative units sold since creation.
        date_added (str):   Date the product was added to the system.
    """

    def __init__(
        self,
        item_id:    int,
        name:       str,
        stock:      int,
        category:   str,
        sell_price: float,
        buy_price:  float,
        threshold:  int,
        total_sold: int = 0,
        date_added: str = "",
    ) -> None:
        """
        Initialise a Product, calling the parent ShopItem constructor.

        Args:
            item_id:    Unique identifier.
            name:       Product name.
            stock:      Initial stock quantity.
            category:   Product category (from CATEGORIES tuple).
            sell_price: Price sold to customers.
            buy_price:  Price bought from supplier.
            threshold:  Minimum stock level before alert.
            total_sold: Units sold so far (default 0).
            date_added: Date added string (default today).
        """
        # Call parent constructor (inheritance)
        super().__init__(item_id, name, stock)
        self._category:   str   = category
        self._sell_price: float = sell_price
        self._buy_price:  float = buy_price
        self._threshold:  int   = threshold
        self._total_sold: int   = total_sold
        self._date_added: str   = date_added or datetime.now().strftime("%m/%d/%Y %H:%M")

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def category(self) -> str:
        """Return the product category."""
        return self._category

    @property
    def sell_price(self) -> float:
        """Return the selling price."""
        return self._sell_price

    @sell_price.setter
    def sell_price(self, value: float) -> None:
        """Set selling price if positive."""
        if value > 0:
            self._sell_price = value

    @property
    def buy_price(self) -> float:
        """Return the purchase price."""
        return self._buy_price

    @buy_price.setter
    def buy_price(self, value: float) -> None:
        """Set purchase price if non-negative."""
        if value >= 0:
            self._buy_price = value

    @property
    def threshold(self) -> int:
        """Return the restock alert threshold."""
        return self._threshold

    @threshold.setter
    def threshold(self, value: int) -> None:
        """Set the alert threshold if non-negative."""
        if value >= 0:
            self._threshold = value

    @property
    def total_sold(self) -> int:
        """Return the total units sold."""
        return self._total_sold

    @property
    def date_added(self) -> str:
        """Return the date the product was added."""
        return self._date_added

    # ── Methods ───────────────────────────────────────────────────────────────
    def sell(self, quantity: int) -> bool:
        """
        Sell a given quantity, updating stock and total_sold.

        Args:
            quantity: Number of units to sell.

        Returns:
            True if the sale was successful, False if insufficient stock.
        """
        if self.remove_stock(quantity):
            self._total_sold += quantity
            return True
        return False

    def is_low_stock(self) -> bool:
        """
        Check whether the product is at or below the alert threshold.

        Returns:
            True if stock is low (but not zero), False otherwise.
        """
        return 0 < self._stock <= self._threshold

    def is_out_of_stock(self) -> bool:
        """
        Check whether the product is completely out of stock.

        Returns:
            True if stock is zero, False otherwise.
        """
        return self._stock == 0

    def profit_margin(self) -> float:
        """
        Calculate the profit margin per unit.

        Returns:
            Difference between sell price and buy price.
        """
        return self._sell_price - self._buy_price

    def stock_value(self) -> float:
        """
        Calculate the current total value of stock at selling price.

        Returns:
            sell_price multiplied by current stock quantity.
        """
        return self._sell_price * self._stock

    def get_status(self) -> str:
        """
        Return a plain-text stock status label.
        Polymorphism: overrides the parent ShopItem.get_status().

        Returns:
            'OUT OF STOCK', 'LOW STOCK', or 'OK' depending on stock level.
        """
        if self._stock == 0:
            return "OUT OF STOCK"
        if self._stock <= self._threshold:
            return "LOW STOCK"
        return "OK"

    def colored_status(self) -> str:
        """
        Return a color-coded stock status string for terminal display.

        Returns:
            A string with ANSI color codes for the status label.
        """
        status = self.get_status()
        if status == "OUT OF STOCK":
            return f"{Colors.RED}[OUT OF STOCK]{Colors.RESET}"
        if status == "LOW STOCK":
            return f"{Colors.YELLOW}[LOW]{Colors.RESET}"
        return f"{Colors.GREEN}[OK]{Colors.RESET}"

    def stock_color(self) -> str:
        """
        Return the ANSI color code matching the current stock level.

        Returns:
            A color code string (red, yellow, or green).
        """
        if self._stock == 0:              return Colors.RED
        if self._stock <= self._threshold: return Colors.YELLOW
        return Colors.GREEN

    def display(self) -> str:
        """
        Return a detailed one-line summary of the product.
        Abstraction: overrides parent display() with richer information.

        Returns:
            A formatted string with name, price, and stock status.
        """
        return (f"[{self._item_id}] {self._name} | {self._category} | "
                f"{fmt(self._sell_price)} FCFA | stock: {self._stock} | {self.get_status()}")

    def to_dict(self) -> dict:
        """
        Serialise the product to a dictionary for JSON storage.
        Overrides parent to_dict() with additional product fields.

        Returns:
            A dictionary with all product data.
        """
        base = super().to_dict()          # inherit base fields from ShopItem
        base.update({
            "category":   self._category,
            "sell_price": self._sell_price,
            "buy_price":  self._buy_price,
            "threshold":  self._threshold,
            "total_sold": self._total_sold,
            "date_added": self._date_added,
        })
        return base

    @staticmethod
    def from_dict(data: dict) -> "Product":
        """
        Reconstruct a Product object from a saved dictionary.

        Args:
            data: Dictionary loaded from JSON file.

        Returns:
            A Product instance with all attributes restored.
        """
        return Product(
            item_id    = data["id"],
            name       = data["name"],
            stock      = data["stock"],
            category   = data["category"],
            sell_price = data["sell_price"],
            buy_price  = data["buy_price"],
            threshold  = data["threshold"],
            total_sold = data.get("total_sold", 0),
            date_added = data.get("date_added", ""),
        )


# ─── OOP: Second child class ──────────────────────────────────────────────────
class PerishableProduct(Product):
    """
    A product with an expiry date. Inherits from Product.

    Extends Product with expiry date tracking and expiry checking.
    Demonstrates a second level of inheritance.

    Attributes:
        expiry_date (str): The expiry date in MM/DD/YYYY format.
    """

    def __init__(self, expiry_date: str, **kwargs) -> None:
        """
        Initialise a PerishableProduct with an expiry date.

        Args:
            expiry_date: Expiry date string in MM/DD/YYYY format.
            **kwargs:    All other arguments passed to Product.__init__.
        """
        super().__init__(**kwargs)
        self._expiry_date: str = expiry_date

    @property
    def expiry_date(self) -> str:
        """Return the expiry date."""
        return self._expiry_date

    def is_expired(self) -> bool:
        """
        Check whether the product has passed its expiry date.

        Returns:
            True if the product is expired, False otherwise.
        """
        try:
            expiry = datetime.strptime(self._expiry_date, "%m/%d/%Y")
            return datetime.now() > expiry
        except ValueError:
            return False

    def get_status(self) -> str:
        """
        Return stock status, also flagging expired products.
        Polymorphism: overrides Product.get_status() with expiry logic.

        Returns:
            'EXPIRED', 'OUT OF STOCK', 'LOW STOCK', or 'OK'.
        """
        if self.is_expired():
            return "EXPIRED"
        return super().get_status()     # delegates to Product.get_status()

    def display(self) -> str:
        """
        Return a one-line product summary including expiry date.
        Overrides Product.display() with additional expiry info.

        Returns:
            A formatted string including the expiry date and status.
        """
        base = super().display()
        return f"{base} | expires: {self._expiry_date}"

    def to_dict(self) -> dict:
        """
        Serialise to dictionary including expiry date and type tag.

        Returns:
            A dictionary with all fields including 'expiry_date' and 'type'.
        """
        d = super().to_dict()
        d["expiry_date"] = self._expiry_date
        d["type"]        = "perishable"
        return d

    @staticmethod
    def from_dict(data: dict) -> "PerishableProduct":
        """
        Reconstruct a PerishableProduct from a saved dictionary.

        Args:
            data: Dictionary loaded from JSON file.

        Returns:
            A PerishableProduct instance.
        """
        return PerishableProduct(
            expiry_date = data.get("expiry_date", ""),
            item_id     = data["id"],
            name        = data["name"],
            stock       = data["stock"],
            category    = data["category"],
            sell_price  = data["sell_price"],
            buy_price   = data["buy_price"],
            threshold   = data["threshold"],
            total_sold  = data.get("total_sold", 0),
            date_added  = data.get("date_added", ""),
        )


# ─── Data persistence ─────────────────────────────────────────────────────────
def load_data() -> tuple[list, list]:
    """
    Load products and sales from the JSON data file.

    Returns:
        A tuple of (products list, sales list).
        Products are reconstructed as Product or PerishableProduct objects.
    """
    if not os.path.exists(DATA_FILE):
        return [], []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw: dict = json.load(f)

    products: list = []
    for d in raw.get("products", []):
        # Reconstruct correct object type based on saved 'type' field
        if d.get("type") == "perishable":
            products.append(PerishableProduct.from_dict(d))
        else:
            products.append(Product.from_dict(d))

    sales: list = raw.get("sales", [])
    return products, sales

def save_data(products: list, sales: list) -> None:
    """
    Save all products and sales to the JSON data file.

    Args:
        products: List of Product (or PerishableProduct) objects.
        sales:    List of sale dictionaries.
    """
    data: dict = {
        "products": [p.to_dict() for p in products],
        "sales":    sales,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Product picker (shared by multiple menus) ────────────────────────────────
def pick_product(products: list, label: str = "Choose a product") -> Optional[Product]:
    """
    Display a searchable product list and let the user pick one by number.

    Args:
        products: List of Product objects to choose from.
        label:    Prompt label shown above the number input.

    Returns:
        The selected Product object, or None if cancelled / not found.
    """
    if not products:
        print_err("No products registered yet.")
        return None

    term: str = input(f"  Search (name/category, Enter to show all): ").strip().lower()
    if term:
        lst: list = [p for p in products
                     if term in p.name.lower() or term in p.category.lower()]
        if not lst:
            print_warn(f"No product found for '{term}'.")
            return None
        print_info(f"{len(lst)} result(s) for '{term}'")
    else:
        lst = products

    print()
    for i, p in enumerate(lst, 1):
        print(f"  {Colors.GRAY}{i:2}.{Colors.RESET} {Colors.BOLD}{p.name:<25}{Colors.RESET} "
              f"stock: {p.stock_color()}{p.stock:>5}{Colors.RESET}  "
              f"{fmt(p.sell_price):>10} FCFA  {p.colored_status()}")
    print()
    choice: int = input_int(f"  {label} (number, 0 to cancel): ", 0, len(lst))
    return None if choice == 0 else lst[choice - 1]


# ─── PRODUCTS MODULE ──────────────────────────────────────────────────────────
def products_menu(products: list, sales: list) -> None:
    """Display the products sub-menu and dispatch to the chosen action."""
    while True:
        separator("PRODUCTS")
        print(f"""
  {Colors.BOLD}1.{Colors.RESET} Add a standard product
  {Colors.BOLD}2.{Colors.RESET} Add a perishable product (with expiry date)
  {Colors.BOLD}3.{Colors.RESET} View all products
  {Colors.BOLD}4.{Colors.RESET} Search a product
  {Colors.BOLD}5.{Colors.RESET} Edit a product
  {Colors.BOLD}6.{Colors.RESET} Delete a product
  {Colors.BOLD}0.{Colors.RESET} Back
""")
        choice: int = input_int("  Your choice: ", 0, 6)
        if choice == 0:   break
        elif choice == 1: add_product(products, sales, perishable=False)
        elif choice == 2: add_product(products, sales, perishable=True)
        elif choice == 3: list_products(products)
        elif choice == 4: search_product(products, sales)
        elif choice == 5: edit_product(products, sales)
        elif choice == 6: delete_product(products, sales)

def add_product(products: list, sales: list, perishable: bool = False) -> None:
    """
    Prompt the user for product details and add a new product to the list.

    Args:
        products:   The current list of Product objects (modified in place).
        sales:      The current sales list (needed for auto-save).
        perishable: If True, creates a PerishableProduct with an expiry date.
    """
    title: str = "ADD A PERISHABLE PRODUCT" if perishable else "ADD A PRODUCT"
    separator(title)

    name: str = input("\n  Product name: ").strip()
    if not name:
        print_err("Name cannot be empty.")
        return
    # Check for duplicate names (case-insensitive)
    if any(p.name.lower() == name.lower() for p in products):
        print_err(f"A product named '{name}' already exists.")
        return

    # Display CATEGORIES tuple for the user to choose from
    print("\n  Categories:")
    for i, c in enumerate(CATEGORIES, 1):
        print(f"    {i}. {c}")
    idx: int = input_int("  Choose a category: ", 1, len(CATEGORIES))
    cat: str = CATEGORIES[idx - 1]

    sell_price: float = input_float("  Selling price (FCFA): ", 0.01)
    buy_price:  float = input_float("  Purchase price (FCFA): ", 0)
    stock_qty:  int   = input_int("  Initial stock quantity: ", 0)
    threshold:  int   = input_int("  Alert threshold (min quantity before alert): ", 0)

    new_id: int = int(datetime.now().timestamp() * 1000)

    if perishable:
        expiry: str = input("  Expiry date (MM/DD/YYYY): ").strip()
        product = PerishableProduct(
            expiry_date = expiry,
            item_id     = new_id,
            name        = name,
            stock       = stock_qty,
            category    = cat,
            sell_price  = sell_price,
            buy_price   = buy_price,
            threshold   = threshold,
        )
    else:
        product = Product(
            item_id    = new_id,
            name       = name,
            stock      = stock_qty,
            category   = cat,
            sell_price = sell_price,
            buy_price  = buy_price,
            threshold  = threshold,
        )

    products.append(product)
    save_data(products, sales)
    print_ok(f"Product '{name}' added successfully!")

    # Warn immediately if the initial stock is already below threshold
    if product.is_out_of_stock():
        print_warn(f"Note: '{name}' was added with zero stock.")
    elif product.is_low_stock():
        print_warn(f"Note: '{name}' stock is already below the alert threshold.")

def list_products(products: list) -> None:
    """
    Display all products in a formatted table with stock status.

    Args:
        products: List of Product objects to display.
    """
    separator("PRODUCT LIST")
    if not products:
        print_info("No products registered.")
        pause()
        return

    header: str = (f"\n  {'#':>3}  {'Name':<22} {'Category':<13} "
                   f"{'Sell':>10} {'Buy':>10} {'Stock':>7} {'Min':>5}  Status")
    print(Colors.GRAY + header + Colors.RESET)
    separator(char="─")

    for i, p in enumerate(products, 1):
        # Flag expired perishable products visually
        expired_tag: str = f" {Colors.RED}[EXPIRED]{Colors.RESET}" if isinstance(p, PerishableProduct) and p.is_expired() else ""
        print(f"  {Colors.GRAY}{i:>3}.{Colors.RESET}  "
              f"{Colors.BOLD}{p.name:<22}{Colors.RESET} "
              f"{p.category:<13} "
              f"{fmt(p.sell_price):>10} "
              f"{fmt(p.buy_price):>10} "
              f"{p.stock_color()}{p.stock:>7}{Colors.RESET} "
              f"{p.threshold:>5}  "
              f"{p.colored_status()}{expired_tag}")

    separator(char="─")
    total_value: float = sum(p.stock_value() for p in products)
    print(f"\n  {Colors.BOLD}Total stock value: {Colors.GREEN}{fmt(total_value)} FCFA{Colors.RESET}")
    pause()

def search_product(products: list, sales: list) -> None:
    """
    Search products by name, category, or status keyword and display results.

    Args:
        products: List of Product objects to search through.
        sales:    Sales list used to show per-product sales statistics.
    """
    separator("SEARCH A PRODUCT")
    if not products:
        print_info("No products registered.")
        pause()
        return

    term: str = input("\n  Keyword (name, category, 'low', 'out', 'expired'): ").strip().lower()
    results: list = []

    if not term:
        print_info("Empty search — showing all products.")
        results = products
    else:
        for p in products:
            name_match:     bool = term in p.name.lower()
            cat_match:      bool = term in p.category.lower()
            low_match:      bool = term == "low"     and p.is_low_stock()
            out_match:      bool = term == "out"     and p.is_out_of_stock()
            expired_match:  bool = (term == "expired"
                                    and isinstance(p, PerishableProduct)
                                    and p.is_expired())
            if name_match or cat_match or low_match or out_match or expired_match:
                results.append(p)

    if not results:
        print_warn(f"No product found for '{term}'.")
        pause()
        return

    print_info(f"{len(results)} product(s) found:")
    separator(char="─")
    for i, p in enumerate(results, 1):
        print(f"  {Colors.GRAY}{i:>3}.{Colors.RESET}  {p.display()}")

    # Show sales stats for each result
    separator(char="─")
    for p in results:
        prod_sales: list = [v for v in sales if v["prod_id"] == p.item_id]
        if prod_sales:
            revenue: float = sum(v["total"]  for v in prod_sales)
            qty:     int   = sum(v["qty"]    for v in prod_sales)
            profit:  float = sum(v["profit"] for v in prod_sales)
            print(f"  {Colors.GRAY}  → {p.name}: {qty} units sold | "
                  f"revenue: {fmt(revenue)} FCFA | profit: {fmt(profit)} FCFA{Colors.RESET}")
    pause()

def edit_product(products: list, sales: list) -> None:
    """
    Let the user select a product and update its editable fields.

    Args:
        products: List of Product objects (modified in place).
        sales:    Sales list needed for auto-save.
    """
    separator("EDIT A PRODUCT")
    p = pick_product(products, "Product to edit")
    if p is None:
        return

    print(f"\n  Editing: {Colors.BOLD}{p.name}{Colors.RESET}")
    print(f"  {Colors.GRAY}(Leave blank to keep current value){Colors.RESET}\n")

    new_name: str = input(f"  Name [{p.name}]: ").strip()
    if new_name:
        p.name = new_name

    val: str = input(f"  Selling price [{p.sell_price}]: ").strip()
    if val:
        try:
            p.sell_price = float(val)
        except ValueError:
            print_warn("Invalid value — selling price unchanged.")

    val = input(f"  Purchase price [{p.buy_price}]: ").strip()
    if val:
        try:
            p.buy_price = float(val)
        except ValueError:
            print_warn("Invalid value — purchase price unchanged.")

    val = input(f"  Alert threshold [{p.threshold}]: ").strip()
    if val:
        try:
            p.threshold = int(val)
        except ValueError:
            print_warn("Invalid value — threshold unchanged.")

    save_data(products, sales)
    print_ok("Product updated successfully.")

def delete_product(products: list, sales: list) -> None:
    """
    Let the user select and permanently delete a product.

    Args:
        products: List of Product objects (modified in place).
        sales:    Sales list needed for auto-save.
    """
    separator("DELETE A PRODUCT")
    p = pick_product(products, "Product to delete")
    if p is None:
        return

    confirm: str = input(f"\n  {Colors.RED}Permanently delete '{p.name}'? (yes/no): {Colors.RESET}").strip().lower()
    if confirm == "yes":
        products.remove(p)
        save_data(products, sales)
        print_ok(f"Product '{p.name}' deleted.")
    else:
        print_info("Deletion cancelled.")


# ─── SALES MODULE ─────────────────────────────────────────────────────────────
def sales_menu(products: list, sales: list) -> None:
    """Display the sales sub-menu and dispatch to the chosen action."""
    while True:
        separator("SALES")
        print(f"""
  {Colors.BOLD}1.{Colors.RESET} Record a sale
  {Colors.BOLD}2.{Colors.RESET} View sales history
  {Colors.BOLD}0.{Colors.RESET} Back
""")
        choice: int = input_int("  Your choice: ", 0, 2)
        if choice == 0:   break
        elif choice == 1: record_sale(products, sales)
        elif choice == 2: sales_history(sales)

def record_sale(products: list, sales: list) -> None:
    """
    Guide the user through building a cart and recording a multi-item sale.
    Stock is deducted and totals are calculated automatically.

    Args:
        products: List of Product objects (stock modified in place).
        sales:    Sales list (new entries appended in place).
    """
    separator("RECORD A SALE")
    if not products:
        print_err("No products available.")
        return

    cart: list = []     # list of dicts: {id, name, qty, price, buy}

    while True:
        # Display current cart
        print(f"\n  {Colors.BOLD}Current cart:{Colors.RESET}", end="")
        if not cart:
            print(f" {Colors.GRAY}(empty){Colors.RESET}")
        else:
            print()
            cart_total: float = 0.0
            for item in cart:
                subtotal: float = item["price"] * item["qty"]
                cart_total += subtotal
                print(f"    • {item['name']:<22} x{item['qty']}  {fmt(subtotal)} FCFA")
            print(f"    {Colors.BOLD}Total: {Colors.GREEN}{fmt(cart_total)} FCFA{Colors.RESET}")

        print(f"""
  {Colors.BOLD}1.{Colors.RESET} Add a product to cart
  {Colors.BOLD}2.{Colors.RESET} Confirm sale
  {Colors.BOLD}0.{Colors.RESET} Cancel
""")
        choice: int = input_int("  Your choice: ", 0, 2)

        if choice == 0:
            print_info("Sale cancelled.")
            return

        if choice == 1:
            p = pick_product(products, "Product to sell")
            if p is None:
                continue
            if p.is_out_of_stock():
                print_err(f"'{p.name}' is out of stock!")
                continue
            if isinstance(p, PerishableProduct) and p.is_expired():
                print_err(f"'{p.name}' is expired and cannot be sold!")
                continue

            qty: int = input_int(f"  Quantity (available: {p.stock}): ", 1, p.stock)

            # Check if already in cart and add if so
            existing = next((i for i in cart if i["id"] == p.item_id), None)
            if existing:
                if existing["qty"] + qty > p.stock:
                    print_err("Total quantity exceeds available stock.")
                    continue
                existing["qty"] += qty
            else:
                cart.append({
                    "id":    p.item_id,
                    "name":  p.name,
                    "qty":   qty,
                    "price": p.sell_price,
                    "buy":   p.buy_price,
                })

        if choice == 2:
            if not cart:
                print_err("Cart is empty.")
                continue

            now: str         = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            total_sale: float  = 0.0
            total_profit: float = 0.0

            for item in cart:
                # Find the matching Product object
                prod = next(p for p in products if p.item_id == item["id"])
                prod.sell(item["qty"])      # deducts stock via method

                subtotal: float = item["price"] * item["qty"]
                profit:   float = (item["price"] - item["buy"]) * item["qty"]
                total_sale   += subtotal
                total_profit += profit

                # Append a sale record dictionary
                sales.append({
                    "date":      now,
                    "prod_id":   item["id"],
                    "prod_name": item["name"],
                    "qty":       item["qty"],
                    "price":     item["price"],
                    "total":     subtotal,
                    "profit":    profit,
                })

            save_data(products, sales)
            separator()
            print_ok(f"Sale recorded!  Total: {fmt(total_sale)} FCFA  |  Profit: {fmt(total_profit)} FCFA")

            # Post-sale stock alerts
            for item in cart:
                prod = next(p for p in products if p.item_id == item["id"])
                if prod.is_out_of_stock():
                    print_warn(f"OUT OF STOCK: '{prod.name}' — no units left!")
                elif prod.is_low_stock():
                    print_warn(f"Low stock: '{prod.name}' — {prod.stock} unit(s) left (threshold: {prod.threshold})")

            pause()
            return

def sales_history(sales: list) -> None:
    """
    Display the last 50 sales in a formatted table.

    Args:
        sales: List of sale record dictionaries.
    """
    separator("SALES HISTORY")
    if not sales:
        print_info("No sales recorded yet.")
        pause()
        return

    recent: list = sales[-50:][::-1]    # show most recent first
    header: str  = f"\n  {'Date':<22} {'Product':<22} {'Qty':>5} {'Total':>12} {'Profit':>12}"
    print(Colors.GRAY + header + Colors.RESET)
    separator(char="─")

    for v in recent:
        print(f"  {Colors.GRAY}{v['date']:<22}{Colors.RESET} "
              f"{v['prod_name']:<22} "
              f"{v['qty']:>5} "
              f"{fmt(v['total']):>12} FCFA "
              f"{Colors.GREEN}{fmt(v['profit']):>10} FCFA{Colors.RESET}")

    separator(char="─")
    total_rev:    float = sum(v["total"]  for v in sales)
    total_profit: float = sum(v["profit"] for v in sales)
    print(f"\n  {Colors.BOLD}Total revenue: {Colors.GREEN}{fmt(total_rev)} FCFA{Colors.RESET}")
    print(f"  {Colors.BOLD}Total profit:  {Colors.GREEN}{fmt(total_profit)} FCFA{Colors.RESET}")
    pause()


# ─── ALERTS MODULE ────────────────────────────────────────────────────────────
def alerts_menu(products: list, sales: list) -> None:
    """
    Display all stock alerts and offer to restock a product.

    Args:
        products: List of Product objects to check for alerts.
        sales:    Sales list needed by the restock function for auto-save.
    """
    separator("ALERTS & RESTOCKING")

    # Build alert lists using Product methods
    out_list:     list = [p for p in products if p.is_out_of_stock()]
    low_list:     list = [p for p in products if p.is_low_stock()]
    expired_list: list = [p for p in products
                          if isinstance(p, PerishableProduct) and p.is_expired()]

    if not out_list and not low_list and not expired_list:
        print_ok("All good — no stock alerts!")
    else:
        if expired_list:
            print(f"\n  {Colors.RED}{Colors.BOLD}{len(expired_list)} expired product(s):{Colors.RESET}")
            for p in expired_list:
                print(f"  {Colors.RED}● EXPIRED     {Colors.RESET}  "
                      f"{Colors.BOLD}{p.name:<25}{Colors.RESET}  "
                      f"expires: {p.expiry_date}")

        if out_list:
            print(f"\n  {Colors.RED}{Colors.BOLD}{len(out_list)} out-of-stock product(s):{Colors.RESET}")
            for p in out_list:
                print(f"  {Colors.RED}● OUT OF STOCK{Colors.RESET}  "
                      f"{Colors.BOLD}{p.name:<25}{Colors.RESET}  "
                      f"threshold: {p.threshold}")

        if low_list:
            print(f"\n  {Colors.YELLOW}{Colors.BOLD}{len(low_list)} low-stock product(s):{Colors.RESET}")
            for p in low_list:
                print(f"  {Colors.YELLOW}● LOW STOCK   {Colors.RESET}  "
                      f"{Colors.BOLD}{p.name:<25}{Colors.RESET}  "
                      f"stock: {p.stock}  threshold: {p.threshold}")

    print(f"\n  {Colors.BOLD}1.{Colors.RESET} Restock a product")
    print(f"  {Colors.BOLD}0.{Colors.RESET} Back\n")
    choice: int = input_int("  Your choice: ", 0, 1)
    if choice == 1:
        restock(products, sales)

def restock(products: list, sales: list) -> None:
    """
    Let the user select a product and add stock to it.

    Args:
        products: List of Product objects (stock modified in place).
        sales:    Sales list needed for auto-save.
    """
    separator("RESTOCK")
    p = pick_product(products, "Product to restock")
    if p is None:
        return
    qty: int = input_int(f"  Quantity to add (current stock: {p.stock}): ", 1)
    p.add_stock(qty)        # uses inherited ShopItem method
    save_data(products, sales)
    print_ok(f"'{p.name}': stock updated → {p.stock} unit(s).")


# ─── REPORTS MODULE ───────────────────────────────────────────────────────────
def reports(products: list, sales: list) -> None:
    """
    Display a full shop report: KPIs, best sellers, category breakdown,
    and critical stock situations.

    Args:
        products: List of Product objects.
        sales:    List of sale record dictionaries.
    """
    separator("REPORTS")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    nb_products:   int   = len(products)
    stock_value:   float = sum(p.stock_value() for p in products)
    stock_cost:    float = sum(p.buy_price * p.stock for p in products)
    total_rev:     float = sum(v["total"]  for v in sales)
    total_profit:  float = sum(v["profit"] for v in sales)
    out_of_stock:  list  = [p for p in products if p.is_out_of_stock()]
    low_stock:     list  = [p for p in products if p.is_low_stock()]

    print(f"""
  {Colors.BOLD}── General summary ──────────────────────────────────{Colors.RESET}
  Number of products       : {Colors.BOLD}{nb_products}{Colors.RESET}
  Stock value (sell price) : {Colors.BOLD}{Colors.GREEN}{fmt(stock_value)} FCFA{Colors.RESET}
  Stock value (buy price)  : {Colors.BOLD}{fmt(stock_cost)} FCFA{Colors.RESET}
  Total revenue            : {Colors.BOLD}{Colors.GREEN}{fmt(total_rev)} FCFA{Colors.RESET}
  Total profit             : {Colors.BOLD}{Colors.GREEN}{fmt(total_profit)} FCFA{Colors.RESET}
  Out of stock             : {Colors.BOLD}{Colors.RED}{len(out_of_stock)}{Colors.RESET}
  Low stock                : {Colors.BOLD}{Colors.YELLOW}{len(low_stock)}{Colors.RESET}
""")

    # ── Best sellers (uses total_sold attribute) ───────────────────────────────
    top: list = sorted(products, key=lambda p: p.total_sold, reverse=True)[:8]
    print(f"  {Colors.BOLD}── Best selling products ────────────────────────────{Colors.RESET}")
    if any(p.total_sold > 0 for p in top):
        max_sold: int = top[0].total_sold
        for i, p in enumerate(top, 1):
            if p.total_sold == 0:
                break
            bar_len: int = min(int(p.total_sold / max(max_sold, 1) * 20), 20)
            bar: str     = "█" * bar_len
            print(f"  {i:>2}. {p.name:<22} {Colors.GREEN}{bar:<20}{Colors.RESET} {p.total_sold} units")
    else:
        print_info("No sales recorded yet.")

    # ── Out of stock ───────────────────────────────────────────────────────────
    if out_of_stock:
        print(f"\n  {Colors.BOLD}── Out of stock products ────────────────────────────{Colors.RESET}")
        for p in out_of_stock:
            print(f"  {Colors.RED}●{Colors.RESET} {p.name}")

    # ── Sales by category (uses a dictionary) ─────────────────────────────────
    cats: dict = {}
    for v in sales:
        prod = next((p for p in products if p.item_id == v["prod_id"]), None)
        cat: str = prod.category if prod else "Unknown"
        cats[cat] = cats.get(cat, 0) + v["total"]

    if cats:
        print(f"\n  {Colors.BOLD}── Sales by category ────────────────────────────────{Colors.RESET}")
        for cat, total in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"  {Colors.CYAN}{cat:<16}{Colors.RESET} {fmt(total):>14} FCFA")

    # ── Expired perishables ────────────────────────────────────────────────────
    expired: list = [p for p in products
                     if isinstance(p, PerishableProduct) and p.is_expired()]
    if expired:
        print(f"\n  {Colors.BOLD}── Expired products ─────────────────────────────────{Colors.RESET}")
        for p in expired:
            print(f"  {Colors.RED}●{Colors.RESET} {p.name}  (expired: {p.expiry_date})")

    pause()


# ─── MAIN MENU ────────────────────────────────────────────────────────────────
def main_menu() -> int:
    """
    Display the main menu and return the user's choice.

    Returns:
        An integer representing the selected menu option.
    """
    print(f"""
{Colors.BOLD}{Colors.BLUE}  ╔══════════════════════════════════════════╗
  ║   {APP_NAME} v{APP_VERSION} — Stock Management      ║
  ╚══════════════════════════════════════════╝{Colors.RESET}

  {Colors.BOLD}1.{Colors.RESET} 📦  Manage products
  {Colors.BOLD}2.{Colors.RESET} 🛒  Record a sale
  {Colors.BOLD}3.{Colors.RESET} 🔔  Alerts & restocking
  {Colors.BOLD}4.{Colors.RESET} 📊  Reports
  {Colors.BOLD}0.{Colors.RESET} 🚪  Quit
""")
    return input_int("  Your choice: ", 0, 4)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
def main() -> None:
    """
    Entry point: load data, show startup alerts, run the main menu loop,
    and save on exit.
    """
    # Enable ANSI color support on Windows
    if sys.platform == "win32":
        os.system("color")

    products, sales = load_data()
    print_info(f"Data loaded from '{DATA_FILE}'  "
               f"({len(products)} products, {len(sales)} sales)")

    # Startup alerts: check for low/out-of-stock using a for loop
    alert_count: int = 0
    for p in products:
        if p.is_out_of_stock() or p.is_low_stock():
            alert_count += 1
    if alert_count > 0:
        print_warn(f"{alert_count} product(s) need restocking — check Alerts menu.")

    # Main loop
    while True:
        choice: int = main_menu()
        if choice == 0:
            save_data(products, sales)
            print_ok("Data saved. Goodbye!")
            break
        elif choice == 1: products_menu(products, sales)
        elif choice == 2: sales_menu(products, sales)
        elif choice == 3: alerts_menu(products, sales)
        elif choice == 4: reports(products, sales)


if __name__ == "__main__":
    main()
