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


