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

CONFIG["mssql_import"] = {
    "server": "localhost",              # Your SQL Server
    "database": "YourDatabase",         # Your database name
    "username": "YourUsername",         # SQL Server login
    "password": "YourPassword",         # SQL Server password
    "data_directory": "output",         # Directory with CSV files
    "enable_quality_tracking": True,      # Quality tracking enablement
    "create_views": True,                 # Create database views
    "batch_size": 1000                    # Rows per batch insert
}