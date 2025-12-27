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

# MSSQL Import Configuration
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

# Simulator specific configuration
CONFIG["simulator"] = {
    # How to render booleans for SQL inserts: if True use 1/0, else use 'TRUE'/'FALSE'
    "sql_boolean_as_int": True,

    # Default number of operations when running simulator
    "default_num_operations": 20,

    # Operation weights can be overridden here (keys must match simulator operation names)
    "operation_weights": {
        "INSERT_CUSTOMER": 0.10,
        "UPDATE_CUSTOMER": 0.08,
        "INSERT_ACCOUNT": 0.10,
        "UPDATE_ACCOUNT": 0.08,
        "INSERT_TRANSACTION": 0.15,
        "UPDATE_TRANSACTION": 0.08,
        "INSERT_CARD": 0.08,
        "UPDATE_CARD": 0.05,
        "INSERT_LOAN": 0.08,
        "UPDATE_LOAN": 0.05,
        "INSERT_FRAUD_ALERT": 0.08,
        "INSERT_LOGIN": 0.07
    },

    # Whether to stop on first SQL error (True) or continue (False)
    "stop_on_error": False
}