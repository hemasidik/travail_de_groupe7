
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

