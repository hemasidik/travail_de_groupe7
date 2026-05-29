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

