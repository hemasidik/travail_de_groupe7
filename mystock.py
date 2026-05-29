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
