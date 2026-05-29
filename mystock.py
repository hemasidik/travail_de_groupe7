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