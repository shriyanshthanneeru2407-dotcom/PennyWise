# PennyWise 💰 — Smart Personal Finance & Wealth Tracker
### *CS50x 2026 Final Project Capstone*
#### By Shriyansh Thanneeru

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-00e676.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0.3-00e676.svg?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/pytest-78%20passed%20(100%25)-00e676.svg?style=flat-square&logo=pytest)](https://docs.pytest.org/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20%7C%20SQLite-00e676.svg?style=flat-square&logo=postgresql)](https://supabase.com/)
[![Security](https://img.shields.io/badge/security-CSRF%20%2B%20scrypt%20%2B%20OAuth2-00e676.svg?style=flat-square)](https://owasp.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)

- **Live Production URL:** [https://pennywise-cs50.vercel.app](https://pennywise-cs50.vercel.app)
- **Demo Account:** `demo@pennywise.app` / `demo1234` (or click *"Auto-fill CS50 Demo Account"* on the sign-in page)

---

## 📌 Video Demo
- **Video Walkthrough (1080p HD, 2 mins):** [pennywise_walkthrough.mp4](pennywise_walkthrough.mp4)
- **YouTube / Loom Presentation:** *Upload your finalized `pennywise_walkthrough.mp4` to YouTube and insert the public link here.*

---

## 📖 Project Overview

**PennyWise** is a full-stack personal finance and expense management web application designed from the ground up to help users master their money, track cash inflows and outflows, manage strict monthly category budgets, and grow dedicated savings vaults.

Many personal finance tools are either bloated with paywalled features or fail to offer intuitive visual feedback. PennyWise was built to bridge that gap with a responsive, keyboard-friendly fintech interface, real-time Chart.js visual analytics, multi-currency support using exact decimal arithmetic, and seamless dark and light mode theming.

The application is built using **Python 3**, **Flask**, **SQLAlchemy ORM**, **Supabase PostgreSQL**, and vanilla JavaScript/CSS with zero heavy frontend dependencies.

---

## ✨ Key Features

1. **Two-Way Cash Flow & Net Margin Tracking:**
   - Records both **Inflows** (Salary, Freelance, Investments) and **Outflows** across 11 financial categories.
   - Computes real-time Available Net Balance: $\text{Available Balance} = \text{Income} - \text{Expenses} - \text{Savings}$.
   - Displays monthly savings rate percentage with visual indicators.

2. **Interactive Chart.js Visual Analytics:**
   - Real-time spending trend line chart and category distribution doughnut charts.
   - Automatically adapts colors, grid lines, and axis labels dynamically when switching between dark and light modes.

3. **Multi-Currency Precision Engine:**
   - Supports 10 global currencies: INR (₹), USD ($), EUR (€), GBP (£), CAD (CA$), AUD (A$), JPY (¥), AED (د.إ), SGD (S$), and CHF (CHF).
   - All financial operations use Python's `Decimal` type to prevent binary floating-point drift.

4. **Monthly Budget Threshold Alert System:**
   - Set overall and category-specific monthly spending caps.
   - Dynamic threshold alerts: `50%` (on track), `80%` (warning), and `100%` (over budget) with color-coded progress meters.

5. **Dedicated Savings Goals Vault:**
   - Create distinct savings funds (e.g. Emergency Fund, Vacation, Car Downpayment).
   - Track quick deposits, remaining amounts, percentage completion, and estimated target dates.

6. **Recurring Subscriptions & Bills Manager:**
   - Monitor recurring charges (Netflix, Spotify, utility bills) with automatic cadence calculation and due-date countdowns.

7. **Financial Insights & Spending Velocity:**
   - Algorithmic analysis of spending velocity, month-over-month percentage variance, and top spending drivers.

8. **Printable Reports & RFC 4180 CSV Export:**
   - 12-month annual financial matrix with full data portability and one-click CSV export.

9. **Fintech Command Palette (Cmd+K / Ctrl+K):**
   - Instant keyboard navigation to any page, quick actions, and single-key shortcuts (`n` for new expense, `d` for dashboard, `u` for theme toggle, `?` for shortcuts modal).

10. **Zero-FOUC Dark & Light Theming:**
    - Persistent dual theme system with immediate `<head>` initialization preventing any Flash of Unstyled Content (FOUC).
    - Asynchronously syncs user theme preferences to PostgreSQL.

---

## 🏗️ Architecture & File Structure

```
spendwise/
├── app/
│   ├── __init__.py               # Flask application factory, DB & login manager initialization
│   ├── models/                   # SQLAlchemy ORM Database Models
│   │   ├── __init__.py
│   │   ├── user.py               # User model with scrypt password hashing & preferences
│   │   ├── category.py           # Pre-seeded & user-custom financial categories
│   │   ├── expense.py            # Transactions (expenses & income) with receipt metadata
│   │   ├── budget.py             # Monthly spending limits & category thresholds
│   │   ├── savings_goal.py       # Savings targets, vaults, and contributions
│   │   ├── recurring.py          # Subscription rules & cadence tracking
│   │   └── notification.py       # Automated in-app alerts (budget caps, bills due)
│   ├── auth/                     # Authentication Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # Login, register, Google OAuth, and email verification
│   ├── dashboard/                # Main Overview Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # KPI computations and JSON chart data endpoints
│   ├── expenses/                 # Transactions Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # CRUD for transactions, receipt uploads, and search
│   ├── budgets/                  # Budget Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # Monthly limits and threshold notifications
│   ├── savings/                  # Savings Vault Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # Goal targets, deposits, and progress calculation
│   ├── recurring/                # Subscriptions Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # Cadence tracker and bill status
│   ├── insights/                 # Analytics Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # Spending velocity and month-over-month trends
│   ├── reports/                  # Reporting Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # 12-month matrix and CSV generation
│   ├── settings/                 # User Preferences Blueprint
│   │   ├── __init__.py
│   │   └── routes.py             # Profile, currency, password, theme AJAX persistence
│   ├── services/                 # Business Logic Services
│   │   ├── export_service.py     # RFC 4180 CSV export generation
│   │   └── notification_service.py # Automated alert generation
│   ├── static/                   # Static Assets
│   │   ├── css/style.css         # Custom responsive design system with CSS tokens
│   │   ├── js/main.js            # UI interactions, shortcuts, theme engine, Cmd+K
│   │   ├── js/charts.js          # Chart.js initialization & dynamic theme listener
│   │   └── images/               # App icons, favicons, brand logo
│   └── templates/                # Jinja2 HTML Templates
│       ├── base.html             # Master layout with sidebar, navbar, and modals
│       ├── index.html            # Public responsive landing page
│       ├── auth/                 # Sign-in, sign-up, and password recovery views
│       ├── dashboard/            # Interactive dashboard view with tour
│       ├── expenses/             # Transaction lists, filters, and forms
│       ├── budgets/              # Budget cards and progress meters
│       ├── savings/              # Savings vault cards and deposit modals
│       ├── recurring/            # Subscription cards and cadence views
│       ├── insights/             # Visual trend charts and velocity cards
│       ├── reports/              # Financial statements and export tables
│       └── settings/             # User preferences, currency, and categories
├── tests/                        # Automated Pytest Suite (78 test cases)
│   ├── conftest.py               # Test fixtures and authenticated client setup
│   ├── test_auth.py              # Auth, OAuth, email verification, and theme API tests
│   ├── test_analytics.py         # KPI calculations, savings rate, and velocity tests
│   ├── test_budgets.py           # Budget cap checks and threshold triggers
│   ├── test_expenses.py          # Transaction validation, pagination, and search
│   ├── test_recurring.py         # Subscription cadence and advancement logic
│   ├── test_savings.py           # Deposit arithmetic and completion projections
│   ├── test_reports_and_insights.py # CSV export formatting and multi-month matrix
│   └── test_security.py          # CSRF, SQL injection immunity, and permission boundaries
├── requirements.txt              # Production Python dependencies
├── vercel.json                   # Serverless WSGI deployment configuration
└── walkthrough.md                # Synchronized 2-minute video voiceover breakdown
```

---

## 🔒 Security & Data Integrity

- **Password Security:** Salted hashes generated using `werkzeug.security` with `scrypt` (memory-hard, resistant to GPU attacks).
- **CSRF Protection:** Every state-altering form and AJAX request includes cryptographic CSRF tokens validated server-side.
- **SQL Injection Immunity:** Strict usage of SQLAlchemy ORM parameterized queries with zero raw string SQL interpolation.
- **Access Control:** User isolation enforced on all queries (`WHERE user_id = current_user.id`) to prevent unauthorized cross-tenant data access.
- **Decimal Accounting:** Currencies are computed with exact precision using Python `Decimal` rather than standard IEEE-754 floats.

---

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/shriyanshthanneeru2407-dotcom/PennyWise.git
cd PennyWise
```

### 3. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Automated Test Suite
```bash
pytest tests/ -v
```
*(All 78 unit, integration, and security tests will execute in ~8 seconds).*

### 5. Launch the Development Server
```bash
flask run --port=5000
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🎓 CS50x Submission Compliance

- **Web Application:** Fully functional, responsive, and mobile-friendly web application deployed to production on Vercel.
- **Complexity & Scope:** Exceeds problem set requirements with 8 full-featured blueprints, 7 relational database models, multi-currency support, receipt attachments, subscription engines, and automated budget notifications.
- **Independent Audio & Video:** Includes an exact 2-minute (129.8s) 1080p demonstration video featuring an animated motion intro and synchronized audio walkthrough.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
