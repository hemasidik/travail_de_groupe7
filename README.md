🛒 MyShop – Inventory & Sales Management System

📌 Project Description

MyShop is a Python-based inventory management system designed for small businesses.
It allows users to manage products, track stock levels, record sales, generate reports, and receive restocking alerts.

The project demonstrates Object-Oriented Programming (OOP), file handling, and real-world software design principles.

---

🚀 Features

- Add, edit, and delete products
- Manage perishable and non-perishable products
- Track stock levels automatically
- Record sales with cart system
- Calculate total revenue and profit
- Generate business reports (KPIs, best sellers, categories)
- Stock alerts (low stock, out of stock, expired products)
- Data persistence using JSON files
- User-friendly terminal interface with colors

---

🧠 Technologies Used

- Python 3.x
- JSON (data storage)
- datetime module
- os module
- sys module
- OOP (Object-Oriented Programming)

---

📂 Project Structure

MyShop/
│
├── 
│ └── 
│
├── 
│ └── 
│
├── docs/
│ └── 
│
├── 
│
├─
├──
└── .

---

🏗️ OOP Structure

ShopItem (Base Class)

- Attributes: id, name, stock
- Methods: add_stock(), remove_stock(), display()

Product (Child Class of ShopItem)

- Adds: price, category, threshold, sales tracking
- Methods: sell(), stock_value(), profit_margin()

PerishableProduct (Child of Product)

- Adds: expiry_date
- Methods: is_expired(), overridden get_status()

OOP Concepts Used:

- Encapsulation → private attributes with getters/setters
- Inheritance → Product inherits ShopItem
- Polymorphism → get_status() behaves differently
- Abstraction → display() hides complexity



1. Clone the repository:

https://github.com/hemasidik/travail_de_groupe7.git

