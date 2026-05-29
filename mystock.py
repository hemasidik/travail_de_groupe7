


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
