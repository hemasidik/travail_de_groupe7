TEAM MATE CONTRIBUTION :

Hema Dilofa A. C. Sidik : i'm the leader and for this project i helped to write the header to code line(1-117) and the deadline line(1205-1265) i also write a part of the readme.
kinda Fabiola: she write the product part line (230-475) she also write a part of readme
kinda Roukieta : she write the part of sales management alerts line(902-1129)
Kindo Andrea : she write the part of shopitems and persistance line(119-229) and Line(577-655)
kiendrebeogo Mashoud : he write the perishable product and ajout part, line(476-576) and line(656-745)
kima Meliane : sh write catalogue and rapport part of this project Line(746-901) and line(1130-1204)
Table of Contents

Overview
Features
Project Structure
OOP Architecture
Modules
Data Persistence
Setup & Installation
Usage
Technical Highlights


Overview
MyShop is a command-line shop management application written in pure Python 3. It is designed for small businesses that need to track inventory, record sales, monitor restocking needs, and generate performance reports — all from a terminal, with no database or external library required.

**Features**
ModuleCapabilitiesProductsAdd (standard or perishable), edit, delete, search, list allSalesMulti-item cart, auto stock deduction, profit tracking, historyAlertsOut-of-stock, low-stock, and expired product detectionReportsRevenue KPIs, best sellers, category breakdown, stock value

Full OOP design — 3-level inheritance chain
ANSI color-coded terminal output
Auto-save — data persisted to JSON after every write operation
Perishable products with expiry date tracking
Type annotations throughout (int, float, str, Optional, list, dict)
Full docstrings on every class, method, and function


Project Structure
myshop/
├── main.py          # Entry point — all classes and logic
└── shop_data.json   # Auto-generated persistent storage

The application is intentionally single-file for simplicity and portability.

Internal organisation of main.py:
main.py
 ├── Constants & Colors          CATEGORIES, APP_VERSION, ANSI codes
 ├── Input helpers               input_int(), input_float()
 ├── Class: ShopItem             Base class
 ├── Class: Product              Child class (sellable product)
 ├── Class: PerishableProduct    Grandchild class (with expiry)
 ├── Data persistence            load_data(), save_data()
 ├── Shared UI helper            pick_product()
 ├── Products module             products_menu(), add/list/search/edit/delete
 ├── Sales module                sales_menu(), record_sale(), sales_history()
 ├── Alerts module               alerts_menu(), restock()
 ├── Reports module              reports()
 └── Entry point                 main_menu(), main()

OOP Architecture
The application uses a 3-level inheritance chain, demonstrating the four pillars of OOP:
ShopItem  (base)
│   item_id, name, stock
│   add_stock(), remove_stock(), get_status(), display(), to_dict()
│
└── Product  (child)
│       category, sell_price, buy_price, threshold, total_sold, date_added
│       sell(), is_low_stock(), is_out_of_stock(), profit_margin(), stock_value()
│       get_status() <- overrides ShopItem
│
└── PerishableProduct  (grandchild)
        expiry_date
        is_expired()
        get_status() <- overrides Product  ->  adds "EXPIRED" status
OOP Pillars in practice
PillarImplementationEncapsulationAll attributes are private (_name, _stock, ...). Controlled access via @property decorators with validation — e.g. stock can never go negative.InheritanceEach child calls super().__init__() and extends the parent without duplicating code. Product.to_dict() calls super().to_dict() and merges additional fields.Polymorphismget_status() and display() are overridden at each level: ShopItem -> "IN STOCK", Product -> adds "LOW STOCK", PerishableProduct -> adds "EXPIRED".AbstractionCallers use sell(), add_stock(), stock_value() without knowing the implementation. to_dict() / from_dict() hide JSON serialisation complexity.

Modules
Products Module

Add a standard product or a perishable product (with expiry date)
Category selection from a predefined CATEGORIES tuple: Food, Beverages, Hygiene, Electronics, Clothing, Other
Duplicate name detection (case-insensitive)
Edit name, selling price, purchase price, and alert threshold
Delete with confirmation prompt
Search by name, category, or status keyword (low, out, expired)

Sales Module

Interactive shopping cart — add multiple products before confirming
Prevents sale of out-of-stock or expired items
On confirmation: stock is automatically deducted via Product.sell()
Each line item records: date, product ID, quantity, unit price, subtotal, and profit
View the last 50 sales in a formatted table with revenue and profit totals

Alerts Module

Products grouped by severity: Expired -> Out of stock -> Low stock
Alert threshold is configurable per product
Startup check: alerts are shown automatically when the app loads
Direct access to the Restock function from the alert view

Reports Module

Total stock value at both selling and purchase price
Cumulative revenue and profit since launch
Top 8 best sellers with a proportional ASCII bar chart
Sales breakdown by category (sorted by revenue)
List of expired perishable products


Data Persistence
All data is stored in a single shop_data.json file, created automatically on first run.
json{
  "products": [
    {
      "id": 1748000000000,
      "name": "Rice 5kg",
      "stock": 42,
      "category": "Food",
      "sell_price": 3500,
      "buy_price": 2800,
      "threshold": 10,
      "total_sold": 158,
      "date_added": "05/23/2025 14:22",
      "type": "perishable",
      "expiry_date": "12/31/2025"
    }
  ],
  "sales": [
    {
      "date": "05/30/2025 09:15:00",
      "prod_id": 1748000000000,
      "prod_name": "Rice 5kg",
      "qty": 3,
      "price": 3500,
      "total": 10500,
      "profit": 2100
    }
  ]
}
Key design decisions:

save_data() is called after every mutating operation — no data loss on unexpected exit
load_data() reconstructs objects via Product.from_dict() or PerishableProduct.from_dict() based on the "type" field
Product IDs are generated as int(datetime.now().timestamp() * 1000) — millisecond timestamps, unique across sessions
Standard products omit the "type" field; only perishable products include "type": "perishable"


Setup & Installation
Requirements

Python 3.10+ (type union syntax used throughout)
Standard library only — no pip install required
A terminal with ANSI color support:

Windows: Windows Terminal or cmd.exe (ANSI enabled automatically)
macOS / Linux: any default terminal



Installation
bash# Clone the repository
git clone https://github.com/your-username/myshop.git
cd myshop

# Run directly — no setup needed
python main.py

Usage
bashpython main.py
On startup, the app loads existing data and displays any active stock alerts, then presents the main menu:
 

  1.  Manage products
  2.  Record a sale
  3.  Alerts & restocking
  4.  Reports
  0.  Quit
Navigation flow:
Main Menu
 ├── 1. Manage Products
 │       ├── Add standard / perishable product
 │       ├── View all products
 │       ├── Search (name, category, status)
 │       ├── Edit a product
 │       └── Delete a product
 ├── 2. Record a Sale
 │       ├── Build cart (add items)
 │       └── Confirm -> stock deducted, sale recorded
 ├── 3. Alerts & Restocking
 │       └── View alerts -> Restock a product
 └── 4. Reports
         └── KPIs · Top sellers · Category breakdown

Technical Highlights
Input validation — input_int() and input_float() loop until valid data is entered, enforcing min/max bounds and rejecting non-numeric input gracefully. No try/except is exposed to the caller.
Timestamp-based IDs — int(datetime.now().timestamp() * 1000) generates unique IDs without a counter or database sequence.
Type-safe object reconstruction — from_dict() is a @staticmethod on each class, keeping deserialisation logic co-located with the class it builds.
Polymorphic status chain — get_status() is overridden at each level of the hierarchy. A single isinstance(p, PerishableProduct) check is only needed where expiry-specific data (like expiry_date) must be displayed; status logic itself is fully polymorphic.
Color semantics — the Colors class is a pure namespace (no instantiation needed). Helper functions print_ok, print_err, print_info, print_warn enforce consistent iconography across the entire app.
Cart de-duplication — if the same product is added twice to the cart, quantities are merged and validated against available stock in a single check.
