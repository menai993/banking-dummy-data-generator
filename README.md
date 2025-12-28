# 📊 Banking Dummy Data Generator

A **comprehensive, configurable banking dummy data generator** built for **data engineering, analytics, QA testing, data quality validation, security testing, and performance benchmarking**.

This project generates **realistic, relational banking datasets** with **controlled bad data injection**, exports them in multiple formats, and optionally imports them directly into **Microsoft SQL Server with data quality tracking**.

---

## 🚀 Key Features

- 🏦 End-to-end **banking domain simulation**
- 🔗 Realistic **table relationships**
- ⚠️ Configurable **bad data injection (5 error types)**
- 📤 Export to **CSV, SQL**
- 🗄️ Direct **MSSQL import with quality logging**
- 📊 Automatic **bad data analytics report**
- 🔄 **CDC (Change Data Capture) simulation & management**
- 🎲 **Live data mutation testing** for CDC/ETL validation
- 🧱 Modular & **easily extensible architecture**
- 🎯 Ideal for **portfolios, demos, testing & learning**
- 🖥️ **Web UI interface** built with Streamlit for easy access to all features

---

## 📁 Project Structure

```
dummy_banking_data/
│── constants/                    # Domain constants
│   ├── names.py                  # Names, cities, states
│   ├── addresses.py              # Address components
│   ├── banking_terms.py          # Banking terminology
│   ├── banking_products.py       # Account & loan types
│   ├── fraud_constants.py
│   ├── investment_products.py
│   └── login_constants.py

│
│── generators/                   # Data generators
│   ├── customer_generator.py
│   ├── account_generator.py
│   ├── card_generator.py
│   ├── transaction_generator.py
│   ├── branch_generator.py
│   ├── loan_generator.py
│   ├── employee_generator.py
│   ├── merchant_generator.py
│   ├── audit_log_generator.py
│   ├── fraud_alert_generator.py
│   ├── user_login_generator.py
│   ├── investment_account_generator.py
│   └── exchange_rate_generator.py
│
│── config/
│   └── create_statements.py      # Centralized DDL definitions
│
│── utils/
│   └── helpers.py                # Export & bad data utilities
│
│── main.py                       # Orchestration script
│── app.py                        # Streamlit Web UI
│── config/settings.py            # Central configuration
│── import_to_mssql.py            # MSSQL importer
│── data_generator_mssql.py       # CDC data simulator
│── enable_cdc.py                 # CDC enable/disable utility
│── requirements.txt
│── README.md
│── STREAMLIT_UI_README.md        # Web UI user guide
└── output/                       # Generated files
```

---

## ⚡ Quick Start

### 1️⃣ Installation

```bash
git clone https://github.com/menai993/banking-dummy-data-generator.git
cd banking-dummy-data-generator
pip install -r requirements.txt
python --version   # Python 3.7+
```

---

### 2️⃣ Configuration

Edit **config/settings.py** to control volume, relationships, output formats, and bad data ratios.

```python
from config import settings

# All configuration is now in settings.CONFIG
CONFIG = settings.CONFIG

# Example: adjust values in config/settings.py
CONFIG["num_customers"] = 1000
CONFIG["output_directory"] = "output"
# ...
```
```

---

### 3️⃣ Using the Web UI (Recommended)

**Launch the Streamlit web interface for easy access to all features:**

```bash
streamlit run app.py
```

The web UI will open in your browser at `http://localhost:8501` and provides:

- 📊 **Data Generation** - Configure and generate banking data with visual controls
- 📥 **MSSQL Import** - Import data to SQL Server with progress tracking
- 🔄 **CDC Management** - Enable/disable CDC with status monitoring
- ⚡ **CDC Simulation** - Simulate data changes with configurable operations

For detailed Web UI documentation, see **[STREAMLIT_UI_README.md](STREAMLIT_UI_README.md)**

---

### 3️⃣ Generate Data (Command Line)

```bash
python main.py
```

Console output example:

```
[1/14] Generating customers (20.0% bad data)...
Generated 1000 customers (200 bad records)
```

---

## 📊 Generated Tables

| Table | Description |
|------|------------|
| customers | Customer master |
| customer_details | Extended profile |
| accounts | Bank accounts |
| cards | Debit & credit cards |
| transactions | Financial transactions |
| branches | Bank branches |
| employees | Bank employees |
| loans | Loans |
| loan_payments | Loan repayments |
| merchants | Merchants |
| audit_logs | System audit logs |
| exchange_rates | Currency exchange rates |
| fraud_alerts | Fraud detection and alert records |
| investment_accounts | Investment accounts |
| user_logins | User authentication and login activity |
---

## 🔗 Data Relationships

```
customers → accounts → cards → transactions → fraud_alerts
     ↓           ↓
customer_details loans → loan_payments
     ↓
investment_accounts

branches → employees → employees (manager hierarchy)

customers → user_logins

```

---

## ⚠️ Bad Data Types

The generator simulates **real-world data quality issues**:

1. **Missing data**
2. **Invalid formats**
3. **Out-of-range values**
4. **Logical inconsistencies**
5. **Malformed / security payloads**

Examples:

```python
customer["email"] = "invalid.email"
account["balance"] = -10000
customer["first_name"] = "<script>alert('xss')</script>"
```

---

## 📈 Data Quality Report

After generation:

```
output/bad_data_report.json
```

Includes:
- Total vs bad records
- Error type breakdown
- Sample corrupted rows

---

## 📤 Output Formats

### CSV
```
output/
├── customers.csv
├── accounts.csv
├── transactions.csv
├── loans.csv
├── audit_logs.csv
├── ...
├── import_errors_YYYYMMDD_HHmmss.txt
└── bad_data_report.json

```

### SQL
```
output/sql/
├── customers.sql
├── accounts.sql
└── ...
```

---

## 🗄️ MSSQL Import

### Prerequisites
- SQL Server
- ODBC Driver 17

### Configure Connection

Edit **config/settings.py**:

```python
from config import settings

# In config/settings.py, update the MSSQL import section:
CONFIG = settings.CONFIG
CONFIG["mssql_import"] = {
    "server": "localhost",                          # Your SQL Server
    "database": "YourDatabase",                     # Your database name
    "username": "YourUsername",                     # SQL Server login
    "password": "YourPassword",                     # SQL Server password
    "data_directory": "output",                     # Directory with CSV files
    "enable_quality_tracking": True,                  # Quality tracking enablement
    "create_views": True,                             # Create database views
    "batch_size": 1000,                               # Rows per batch insert
    "override_batch_size_based_on_file_size": True    # Adjust batch size based on file size
}
```
```

### Run Import

```bash
python import_to_mssql.py
```

Imported tables include:
- `is_bad_data` flag
- `data_quality_log` table

---

## 🔄 CDC (Change Data Capture) Features

### Overview

The project includes **CDC simulation and management tools** for testing data pipelines, ETL processes, and real-time analytics workflows.

---

### CDC Enable/Disable Utility

**enable_cdc.py** - Interactive tool to manage CDC on SQL Server tables.

#### Features
- 🔍 Check CDC status on database and tables
- ✅ Enable CDC on database and all banking tables
- ❌ Disable CDC on tables and database
- 📋 List all CDC-enabled tables

#### Usage

```bash
python enable_cdc.py
```

Interactive menu:
```
================ CDC STATUS ================

Database CDC enabled: YES
Tables with CDC enabled (15):
  • customers
  • accounts
  • transactions
  • ...

============================================

Choose action [enable / disable / exit]:
```

---

### CDC Data Simulator

**data_generator_mssql.py** - Simulates real-world data changes for CDC testing.

#### Features
- 🎲 **Mixed operations**: INSERT, UPDATE, DELETE
- ⚖️ **Configurable weights** for operation types
- 📊 **Realistic banking mutations**: balance updates, status changes, new records
- 🔄 **Continuous data evolution** for streaming pipelines
- 📈 **Operation tracking** with success/failure logs

#### Supported Operations

| Operation Type | Description |
|------|------------|
| INSERT_CUSTOMER | Add new customer records |
| UPDATE_CUSTOMER | Modify customer contact info |
| INSERT_ACCOUNT | Create new accounts |
| UPDATE_ACCOUNT | Update account balances |
| INSERT_TRANSACTION | Generate new transactions |
| UPDATE_TRANSACTION | Change transaction status |
| INSERT_CARD | Issue new cards |
| UPDATE_CARD | Modify card status |
| INSERT_LOAN | Create new loans |
| UPDATE_LOAN | Update loan status |
| INSERT_FRAUD_ALERT | Generate fraud alerts |
| INSERT_LOGIN | Record user logins |

#### Usage

```bash
python data_generator_mssql.py
```

Example output:
```
======================================================================
SIMULATING 20 CDC OPERATIONS
======================================================================

[1/20] INSERT_CUSTOMER...
  ➕ Inserted customer: CUST-001234

[2/20] UPDATE_ACCOUNT...
  ✏️  Updated account balance: ACC-005678 (change: 1250.50)

[3/20] INSERT_TRANSACTION...
  ➕ Inserted transaction: TXN-789012

...

======================================================================
OPERATIONS COMPLETE
======================================================================
Total Executed: 20
Successful: 19
Failed: 1
======================================================================
```

#### Configuration

In **config/settings.py**, customize the simulator behavior:

```python
from config import settings

# In config/settings.py, update the simulator section:
CONFIG = settings.CONFIG
CONFIG["simulator"] = {
    "default_num_operations": 20,        # Operations per run
    "operation_weights": {                # Control operation mix
        "INSERT_CUSTOMER": 0.10,
        "UPDATE_ACCOUNT": 0.15,
        # ... customize weights
    },
    "stop_on_error": False               # Continue on failures
}
```
```

---

## 🎯 Use Cases

- Data engineering portfolios
- ETL & pipeline validation
- **CDC & streaming data testing**
- **Real-time analytics validation**
- SQL performance benchmarking
- Application testing
- Security & validation testing
- BI & analytics demos
- **Data pipeline stress testing**

---

## 🔧 Customization

### Add New Generator

1. Create a file in `generators/`
2. Follow existing patterns
3. Register in `main.py`

```python
class CustomGenerator:
    def generate(self):
        return data
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-----|---------|
| Missing dependencies | `pip install -r requirements.txt` |
| MSSQL connection error | Check credentials |
| Memory error | Reduce dataset size |
| No output files | Check permissions |

---

## 📋 Useful Commands

```bash
python main.py
python import_to_mssql.py
python enable_cdc.py
python data_generator_mssql.py
rm -rf output/*
```

---

## 📊 Sample Volumes

| Customers | Transactions | Time |
|---------|--------------|------|
| 100 | ~6k | ~30 sec |
| 1,000 | ~62k | ~3 min |
| 10,000 | ~625k | ~30 min |

---

## 🤝 Contribution

Contributions are welcome.  
Please include:
- Python version
- Error logs
- Config used
- Steps to reproduce

---

## ✅ Verification Checklist

- Data generation succeeds
- Output files created
- Bad data ratios respected
- MSSQL import works
- Quality flags present

---

**Built for real-world data engineering challenges. 🚀**
