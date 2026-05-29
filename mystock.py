
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

    def _init_(
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
        super()._init_(item_id, name, stock)
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