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

    def _init_(self, item_id: int, name: str, stock: int) -> None:
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
