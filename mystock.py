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

