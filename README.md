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
- 🧱 Modular & **easily extensible architecture**
- 🎯 Ideal for **portfolios, demos, testing & learning**

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
    ├── fraud_alert_generator.py
    ├── user_login_generator.py
    ├── investment_account_generator.py
│   └── exchange_rate_generator.py
│
│── utils/
│   └── helpers.py                # Export & bad data utilities
│
│── main.py                       # Orchestration script
│── config.py                     # Central configuration
│── import_to_mssql.py            # MSSQL importer
│── requirements.txt
│── README.md
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

Edit **config.py** to control volume, relationships, output formats, and bad data ratios.

```python
CONFIG = {
    # Volume controls
    "num_customers": 1000,
    "num_branches": 50,
    "num_employees": 200,
    "num_merchants": 500,
    "num_investment_accounts": 300,           
    
    # Relationship controls
    "accounts_per_customer_min": 1,
    "accounts_per_customer_max": 3,
    "cards_per_customer_min": 0,
    "cards_per_customer_max": 2,
    "transactions_per_account_min": 5,
    "transactions_per_account_max": 50,
    "fraud_alerts_per_transaction": 0.05,     
    "user_logins_per_customer_min": 8,        
    "user_logins_per_customer_max": 30,       
    "exchange_rate_days": 365,
    "audit_logs_per_user_min": 5,
    "audit_logs_per_user_max": 50,
    "loans_per_customer_min": 0,
    "loans_per_customer_max": 2,

    # Output options: csv, sql, -- soon excel will be available
    "output_formats": ["csv", "sql"],  
    "output_directory": "output",

    # Bad data configuration
    "bad_data_percentage": {
        "customers": 0.20,
        "accounts": 0.15,
        "cards": 0.25,
        "transactions": 0.10,
        "branches": 0.05,
        "employees": 0.08,
        "merchants": 0.12,
        "loans": 0.15,
        "loan_payments": 0.20,
        "audit_logs": 0.05,
        "exchange_rates": 0.03,
        "investment_accounts": 0.12,          
        "fraud_alerts": 0.18,                 
        "user_logins": 0.08                   
    },

    # Types of bad data to generate
    "bad_data_types": {
        "missing_data": True,
        "invalid_format": True,
        "out_of_range": True,
        "inconsistent_data": True,
        "duplicate_data": False,
        "malformed_data": True
    }
}
```

---

### 3️⃣ Generate Data

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

Edit **config.py**:

```python
CONFIG["mssql_import"] = {
    "server": "localhost",                          # Your SQL Server
    "database": "YourDatabase",                     # Your database name
    "username": "YourUsername",                     # SQL Server login
    "password": "YourPassword",                     # SQL Server password
    "data_directory": "output",                     # Directory with CSV files
    "enable_quality_tracking": True,                # Quality tracking enablement
    "create_views": True,                           # Create database views
    "batch_size": 1000,                             # Rows per batch insert
    "override_batch_size_based_on_file_size": True  # Adjust batch size based on file size
}
```

### Run Import

```bash
python import_to_mssql.py
```

Imported tables include:
- `is_bad_data` flag
- `data_quality_log` table

---

## 🎯 Use Cases

- Data engineering portfolios
- ETL & pipeline validation
- SQL performance benchmarking
- Application testing
- Security & validation testing
- BI & analytics demos

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
