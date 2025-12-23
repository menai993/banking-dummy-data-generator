# Configuration settings
CONFIG = {
    "num_customers": 1000,
    "num_branches": 50,
    "num_employees": 200,
    "num_merchants": 500,
    
    "accounts_per_customer_min": 1,
    "accounts_per_customer_max": 3,
    "cards_per_customer_min": 0,
    "cards_per_customer_max": 2,
    "transactions_per_account_min": 5,
    "transactions_per_account_max": 50,
    
    "exchange_rate_days": 365,
    "audit_logs_per_user_min": 5,
    "audit_logs_per_user_max": 50,
    "loans_per_customer_min": 0,
    "loans_per_customer_max": 2,
    
    "output_formats": ["csv", "sql"],  # Options: csv, sql, -- soon excel will be available
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
        "exchange_rates": 0.03
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