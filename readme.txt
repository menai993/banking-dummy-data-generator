📊 COMPREHENSIVE GUIDE: Banking Dummy Data Generator
📁 Project Structure Overview
text
dummy_banking_data/
│── constants/                    # Data constants and lists
│   ├── __init__.py
│   ├── names.py                 # Names, cities, states
│   ├── addresses.py             # Address components
│   ├── banking_terms.py         # Banking terminology
│   └── banking_products.py      # Loan types, investment types, etc.
│
│── generators/                  # Data generation modules
│   ├── __init__.py
│   ├── customer_generator.py    # Customers & details
│   ├── account_generator.py     # Bank accounts
│   ├── card_generator.py        # Credit/debit cards
│   ├── transaction_generator.py # Financial transactions
│   ├── branch_generator.py      # Bank branches
│   ├── loan_generator.py        # Loans & payments
│   ├── employee_generator.py    # Bank employees
│   ├── merchant_generator.py    # Merchants
│   ├── audit_log_generator.py   # Audit trails
│   └── exchange_rate_generator.py # Currency rates
│
│── utils/                       # Utility functions
│   ├── __init__.py
│   └── helpers.py               # Export, bad data generation
│
│── main.py                      # Main execution script
│── config.py                    # Configuration settings
│── import_to_mssql.py           # MSSQL import script
│── requirements.txt             # Python dependencies
│── README.md                    # This guide
└── output/                      # Generated files (created automatically)
🚀 QUICK START GUIDE
Step 1: Installation
bash
# 1. Clone or download the project
git clone <repository-url>
cd dummy_banking_data

# 2. Install required packages
pip install -r requirements.txt

# 3. Verify installation
python --version  # Should be Python 3.7+
Step 2: Basic Configuration
Edit config.py to set your preferences:

python
# Key configurations to adjust:
CONFIG = {
    "num_customers": 1000,           # How many customers to generate
    "accounts_per_customer_min": 1,  # Min accounts per customer
    "accounts_per_customer_max": 3,  # Max accounts per customer
    
    # Bad data percentages (20% = 0.20)
    "bad_data_percentage": {
        "customers": 0.20,      # 20% of customers will have bad data
        "accounts": 0.15,
        "cards": 0.25,
        "transactions": 0.10,
        "branches": 0.05,
        "employees": 0.08,
        "loans": 0.15,
        # ... other tables
    },
    
    "output_formats": ["csv", "sql", "excel"],  # Output formats
}
Step 3: Generate Data
bash
# Generate all data (default configuration)
python main.py

# Output will show progress like:
# ========================================
# BANKING DUMMY DATA GENERATOR WITH BAD DATA
# ========================================
# 
# [1/11] Generating customers (20.0% bad data)...
# Generated 1000 customers (200 with bad data)
# Generated 1000 customer details (200 with bad data)
# 
# [2/11] Generating accounts (15.0% bad data)...
# Generated 2500 accounts (375 with bad data)
# ... etc.
⚙️ CONFIGURATION OPTIONS
1. Volume Control
Parameter	Default	Description
num_customers	1000	Total customers to generate
num_branches	50	Number of bank branches
num_employees	200	Number of bank employees
num_merchants	500	Number of merchants
exchange_rate_days	365	Days of historical exchange rates
2. Relationship Controls
python
# In config.py
"accounts_per_customer_min": 1,    # Each customer has 1-3 accounts
"accounts_per_customer_max": 3,
"cards_per_customer_min": 0,       # Each customer has 0-2 cards
"cards_per_customer_max": 2,
"loans_per_customer_min": 0,       # Each customer has 0-2 loans
"loans_per_customer_max": 2,
"transactions_per_account_min": 5, # Each account has 5-50 transactions
"transactions_per_account_max": 50,
3. Bad Data Configuration
python
# Set different percentages for each table
"bad_data_percentage": {
    "customers": 0.20,      # 20% bad customer data
    "accounts": 0.15,       # 15% bad account data
    "cards": 0.25,          # 25% bad card data (higher for testing)
    "transactions": 0.10,   # 10% bad transaction data
    "branches": 0.05,       # 5% bad branch data
    # ... other tables
}
4. Output Formats
python
"output_formats": ["csv", "sql", "excel"]
# Options: "csv" = CSV files, "sql" = SQL INSERT statements, "excel" = Excel file
📊 GENERATED TABLES & RELATIONSHIPS
Core Banking Tables (17 Tables)
Table	Records (Default)	Description	Key Relationships
customers	1,000	Customer基本信息	Primary table
customer_details	1,000	Customer详细信息	← customers.customer_id
accounts	~2,500	Bank accounts	← customers.customer_id
cards	~1,500	Credit/debit cards	← accounts.account_id
transactions	~62,500	Financial transactions	← accounts.account_id, cards.card_id
branches	50	Bank branches	Standalone
employees	200	Bank employees	← branches.branch_id
loans	~1,000	Loans	← customers.customer_id
loan_payments	~60,000	Loan payments	← loans.loan_id
merchants	500	Merchants	Standalone
audit_logs	~25,000	System audit trails	← customers/employees
exchange_rates	4,015	Currency rates	Standalone
Data Relationships Diagram
text
customers (1) → (many) accounts (1) → (many) cards
              ↓                      ↓
        customer_details     transactions
              ↓
            loans (1) → (many) loan_payments
              ↓
    (assigned to) branches (1) → (many) employees
📁 OUTPUT FILES
After running python main.py, check the output/ directory:

1. CSV Files (in output/)
text
output/
├── customers.csv              # 1,000 customers
├── customer_details.csv       # 1,000 customer details
├── accounts.csv               # ~2,500 accounts
├── cards.csv                  # ~1,500 cards
├── transactions.csv           # ~62,500 transactions
├── branches.csv               # 50 branches
├── employees.csv              # 200 employees
├── loans.csv                  # ~1,000 loans
├── loan_payments.csv          # ~60,000 payments
├── merchants.csv              # 500 merchants
├── audit_logs.csv             # ~25,000 audit logs
├── exchange_rates.csv         # 4,015 exchange rates
├── banking_data.xlsx          # All data in Excel (multi-sheet)
└── bad_data_report.json       # Bad data analysis
2. SQL Files (in output/sql/)
text
output/sql/
├── customers.sql              # INSERT statements
├── customer_details.sql
├── accounts.sql
├── cards.sql
├── transactions.sql
└── ... (all other tables)
3. Excel File
output/banking_data.xlsx contains all tables in separate sheets.

🗄️ IMPORT TO MSSQL
Prerequisites
SQL Server installed and running

ODBC Driver 17 for SQL Server installed

Database created (e.g., BankingDB)

Step 1: Configure Connection
Edit import_to_mssql.py:

python
CONFIG = {
    "server": "localhost",              # Your SQL Server
    "database": "BankingDB",            # Your database name
    "username": "your_username",        # SQL login
    "password": "your_password",        # SQL password
    "data_directory": "output"
}
Step 2: Run Import
bash
python import_to_mssql.py

# You'll see:
# ========================================
# MSSQL DATA IMPORTER WITH BAD DATA HANDLING
# ========================================
# 
# [1/2] Creating tables with data quality tracking...
# Created table: customers
# Created table: customer_details
# ... etc.
# 
# [2/2] Importing data with quality checks...
# Importing customers.csv...
# Imported 1000 rows into customers (5 errors, 200 bad records)
# ... etc.
Step 3: Verify Import
Connect to your SQL Server and run:

sql
-- Check data quality
SELECT * FROM data_quality_log ORDER BY import_date DESC;

-- View bad data
SELECT * FROM customers WHERE is_bad_data = 1;

-- Check counts
SELECT 
    'customers' as table_name, COUNT(*) as records 
FROM customers
UNION ALL
SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;
🔍 BAD DATA TYPES GENERATED
The system generates 5 types of bad data:

1. Missing Data
python
# NULL values in required fields
customer["email"] = None
account["balance"] = None
2. Invalid Format
python
# Wrong format data
customer["email"] = "invalid.email"
card["expiration_date"] = "13/25"  # Invalid month
phone = "abc-def-ghij"  # Letters in phone
3. Out of Range
python
# Values outside valid ranges
account["balance"] = -10000.00  # Negative balance
customer["date_of_birth"] = "2050-01-01"  # Future date
card["credit_limit"] = 99999999.99  # Too high
4. Inconsistent Data
python
# Logical inconsistencies
customer["state"] = "XX"  # Invalid state code
employee["role"] = "Teller"
employee["salary"] = 150000  # Teller with manager salary
5. Malformed Data
python
# Security threats or malformed strings
customer["first_name"] = "John<script>alert('xss')</script>"
account["account_type"] = "Savings' OR '1'='1"
transaction["description"] = "../../../etc/passwd"
📈 DATA QUALITY ANALYSIS
Bad Data Report
After generation, check output/bad_data_report.json:

json
{
  "generation_date": "2024-01-15T10:30:00",
  "configuration": {
    "customers": 0.20,
    "accounts": 0.15,
    ...
  },
  "tables": {
    "customers": {
      "total_records": 1000,
      "bad_records": 200,
      "bad_percentage": 20.0,
      "bad_by_type": {
        "missing_data": 80,
        "invalid_format": 60,
        "out_of_range": 40,
        "inconsistent_data": 20
      },
      "examples": [...]  # Sample bad records
    }
  }
}
SQL Queries for Data Quality Checks
sql
-- 1. Find all bad records
SELECT table_name, SUM(bad_records) as total_bad 
FROM data_quality_log 
GROUP BY table_name;

-- 2. Find invalid emails
SELECT customer_id, email 
FROM customers 
WHERE email NOT LIKE '%@%.%' OR email IS NULL;

-- 3. Find negative balances
SELECT account_id, customer_id, balance 
FROM accounts 
WHERE balance < 0;

-- 4. Find expired cards
SELECT card_id, expiration_date 
FROM cards 
WHERE CONVERT(date, '20' + RIGHT(expiration_date, 2) + LEFT(expiration_date, 2) + '01') < GETDATE();

-- 5. Find data inconsistencies
SELECT c.customer_id, c.first_name, cd.annual_income, cd.employment_status
FROM customers c
JOIN customer_details cd ON c.customer_id = cd.customer_id
WHERE cd.employment_status = 'Unemployed' AND cd.annual_income > 100000;

-- 6. Find missing required fields
SELECT customer_id, first_name, last_name, email, phone
FROM customers
WHERE email IS NULL OR phone IS NULL;
🎯 USE CASES & TESTING SCENARIOS
1. Application Testing
bash
# Test with 100 customers (quick test)
# Edit config.py:
"num_customers": 100,
"bad_data_percentage": {"customers": 0.30}  # 30% bad data for rigorous testing
2. Data Validation Testing
bash
# Test edge cases with high bad data
"bad_data_percentage": {
    "customers": 0.50,      # 50% bad customer data
    "transactions": 0.30,   # 30% bad transactions
}
3. Performance Testing
bash
# Generate large dataset for performance testing
"num_customers": 10000,
"transactions_per_account_max": 200,  # More transactions
4. Specific Test Scenarios
python
# In config.py, you can customize for specific tests:
"bad_data_types": {
    "missing_data": True,      # Test NULL handling
    "invalid_format": False,   # Skip format testing
    "out_of_range": True,      # Test boundary conditions
    "inconsistent_data": True, # Test business logic
    "malformed_data": True     # Test security
}
🔧 CUSTOMIZATION GUIDE
1. Add Custom Names
Edit constants/names.py:

python
FIRST_NAMES = [
    "Your", "Custom", "Names", "Here",
    # Add more names...
]

LAST_NAMES = [
    "Custom", "Surnames", "Here",
    # Add more surnames...
]
2. Add New Account Types
Edit constants/banking_products.py:

python
ACCOUNT_TYPES = [
    "Savings", "Checking", "Money Market", 
    "Certificate of Deposit", "Business Account",  # Added
    "Student Account"  # Added
]
3. Create Custom Generator
Create generators/custom_generator.py:

python
from utils.helpers import BadDataGenerator

class CustomGenerator:
    def __init__(self, bad_data_percentage=0.0):
        self.bad_data_percentage = bad_data_percentage
    
    def generate(self):
        data = []
        # Your generation logic here
        return data
4. Modify Main Script
Add to main.py:

python
# Import your custom generator
from generators.custom_generator import CustomGenerator

# In main() function:
print("\n[12/12] Generating custom data...")
custom_gen = CustomGenerator(bad_data_percentage=0.10)
custom_data = custom_gen.generate()

# Add to all_data dictionary
all_data["custom_table"] = custom_data
🐛 TROUBLESHOOTING
Common Issues & Solutions
Issue	Solution
ImportError: No module named 'pandas'	Run pip install -r requirements.txt
SQL Server connection failed	Check server name, credentials in import_to_mssql.py
ODBC Driver 17 not found	Install from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
Memory error with large datasets	Reduce num_customers or transaction counts
CSV files not generated	Check write permissions in output/ directory
Bad data percentage not working	Ensure values are between 0.0 and 1.0
Debug Mode
Add debug prints in generators:

python
def generate(self):
    print(f"DEBUG: Generating with bad_data_percentage={self.bad_data_percentage}")
    # ... rest of code
📋 COMMAND CHEAT SHEET
bash
# Generate data with default settings
python main.py

# Generate minimal dataset for testing
# Edit config.py: set num_customers=100
python main.py

# Generate maximum dataset for performance testing
# Edit config.py: set num_customers=10000, transactions_per_account_max=200
python main.py

# Import to MSSQL (after configuring connection)
python import_to_mssql.py

# Generate only CSV files
# Edit config.py: set output_formats=["csv"]
python main.py

# Generate with specific bad data percentage
# Edit config.py: set bad_data_percentage["customers"]=0.50
python main.py

# Clean output directory (Linux/Mac)
rm -rf output/*

# Clean output directory (Windows)
rmdir /s /q output
mkdir output
📊 SAMPLE DATA VOLUMES
Configuration	Customers	Accounts	Transactions	File Size	Generation Time
Small (100 customers)	100	~250	~6,250	~10 MB	~30 seconds
Medium (1,000 customers)	1,000	~2,500	~62,500	~100 MB	~3 minutes
Large (10,000 customers)	10,000	~25,000	~625,000	~1 GB	~30 minutes
🔄 WORKFLOW EXAMPLES
Workflow 1: Complete System Test
bash
# 1. Generate medium dataset with 20% bad data
# Edit config.py: num_customers=1000, bad_data_percentage=0.20
python main.py

# 2. Import to MSSQL
python import_to_mssql.py

# 3. Run data quality checks in SQL Server
# Use queries from "Data Quality Analysis" section
Workflow 2: Focused Validation Test
bash
# 1. Generate data with only format errors
# Edit config.py: 
# bad_data_types: set all False except "invalid_format": True
# bad_data_percentage["customers"]=0.40
python main.py

# 2. Test your application's format validation
Workflow 3: Performance Benchmark
bash
# 1. Generate large dataset
# Edit config.py: num_customers=5000
python main.py

# 2. Import and measure import time
# 3. Run performance queries on the database
🎓 LEARNING RESOURCES
For Understanding the Code
Python Basics: Functions, classes, dictionaries

SQL Fundamentals: Tables, relationships, INSERT statements

Data Quality: Types of data errors, validation rules

For Extending the System
Study utils/helpers.py: BadDataGenerator class

Examine generators/customer_generator.py: Pattern for new generators

Review main.py: How generators are orchestrated

📞 SUPPORT & CONTRIBUTION
Getting Help
Check output/bad_data_report.json for generation details

Review console output for error messages

Verify SQL Server connection settings

Reporting Issues
When reporting issues, include:

Python version (python --version)

Error message from console

Relevant configuration from config.py

Steps to reproduce

Extending the System
To add new features:

Follow existing patterns in generators

Use BadDataGenerator for consistent bad data

Update config.py for new configurations

Add to main.py orchestration

✅ VERIFICATION CHECKLIST
After setup, verify:

python main.py runs without errors

CSV files are created in output/ directory

bad_data_report.json shows correct percentages

SQL Server connection works (if using MSSQL)

Data imports correctly to database

Bad data flags are present in imported data