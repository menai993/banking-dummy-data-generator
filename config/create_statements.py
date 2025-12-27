"""Centralized DDL statements for table creation.

This module exposes `CREATE_STATEMENTS` so other scripts can import
the SQL definitions from a single source of truth.
"""

CREATE_STATEMENTS = {
    "customers": """
            CREATE TABLE customers (
                customer_id VARCHAR(20) PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                phone VARCHAR(20),
                date_of_birth DATE,
                street VARCHAR(200),
                city VARCHAR(100),
                state VARCHAR(2),
                zip_code VARCHAR(10),
                country VARCHAR(50),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "customer_details": """
            CREATE TABLE customer_details (
                detail_id INT IDENTITY(1,1) PRIMARY KEY,
                customer_id VARCHAR(20) FOREIGN KEY REFERENCES customers(customer_id),
                employment_status VARCHAR(50),
                annual_income DECIMAL(12,2),
                credit_score INT,
                marital_status VARCHAR(20),
                education_level VARCHAR(50),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "accounts": """
            CREATE TABLE accounts (
                account_id VARCHAR(20) PRIMARY KEY,
                customer_id VARCHAR(20) FOREIGN KEY REFERENCES customers(customer_id),
                account_number VARCHAR(20) UNIQUE, 
                account_type VARCHAR(50), 
                balance DECIMAL(15,2),
                currency VARCHAR(3),
                status VARCHAR(20),
                opened_date DATE,
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "cards": """
            CREATE TABLE cards (
                card_id VARCHAR(20) PRIMARY KEY,
                customer_id VARCHAR(20) FOREIGN KEY REFERENCES customers(customer_id),
                account_id VARCHAR(20) FOREIGN KEY REFERENCES accounts(account_id),
                card_number VARCHAR(20),
                card_type VARCHAR(20),
                card_network VARCHAR(20),
                expiration_date VARCHAR(10),
                cvv VARCHAR(5),
                credit_limit DECIMAL(15,2),
                status VARCHAR(20),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "transactions": """
            CREATE TABLE transactions (
                transaction_id VARCHAR(20) PRIMARY KEY,
                account_id VARCHAR(20) FOREIGN KEY REFERENCES accounts(account_id),
                card_id VARCHAR(20) NULL FOREIGN KEY REFERENCES cards(card_id),
                transaction_type VARCHAR(50),
                amount DECIMAL(15,2),
                currency VARCHAR(3),
                transaction_date DATE,
                transaction_time TIME,
                description VARCHAR(200),
                status VARCHAR(20),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "branches": """
            CREATE TABLE branches (
                branch_id VARCHAR(20) PRIMARY KEY,
                branch_name VARCHAR(100),
                branch_code VARCHAR(10),
                branch_type VARCHAR(50),
                street VARCHAR(200),
                city VARCHAR(100),
                state VARCHAR(2),
                zip_code VARCHAR(10),
                country VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100),
                manager_name VARCHAR(100),
                opening_date DATE,
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "employees": """
            CREATE TABLE employees (
                employee_id VARCHAR(20) PRIMARY KEY,
                branch_id VARCHAR(20) FOREIGN KEY REFERENCES branches(branch_id),
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100),
                phone_extension VARCHAR(10),
                role VARCHAR(50),
                department VARCHAR(50),
                salary DECIMAL(12,2),
                hire_date DATE,
                manager_id VARCHAR(20) NULL FOREIGN KEY REFERENCES employees(employee_id),
                status VARCHAR(20),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "loans": """
            CREATE TABLE loans (
                loan_id VARCHAR(20) PRIMARY KEY,
                customer_id VARCHAR(20) FOREIGN KEY REFERENCES customers(customer_id),
                account_id VARCHAR(20) FOREIGN KEY REFERENCES accounts(account_id),
                loan_type VARCHAR(50),
                loan_amount DECIMAL(15,2),
                interest_rate DECIMAL(10,6),
                term_months INT,
                start_date DATE,
                end_date DATE,
                monthly_payment DECIMAL(15,2),
                remaining_balance DECIMAL(15,2),
                status VARCHAR(50),
                interest_type VARCHAR(50),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "loan_payments": """
            CREATE TABLE loan_payments (
                payment_id VARCHAR(20) PRIMARY KEY,
                loan_id VARCHAR(20) FOREIGN KEY REFERENCES loans(loan_id),
                customer_id VARCHAR(20) FOREIGN KEY REFERENCES customers(customer_id),
                payment_number INT,
                payment_date DATE,
                due_date DATE,
                amount_due DECIMAL(15,2),
                principal_amount DECIMAL(15,2),
                interest_amount DECIMAL(15,2),
                total_paid DECIMAL(15,2),
                status VARCHAR(20),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "merchants": """
            CREATE TABLE merchants (
                merchant_id VARCHAR(20) PRIMARY KEY,
                merchant_name VARCHAR(100),
                category VARCHAR(50),
                mcc_code VARCHAR(10),
                street VARCHAR(200),
                city VARCHAR(100),
                state VARCHAR(2),
                zip_code VARCHAR(10),
                country VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100),
                website VARCHAR(100),
                status VARCHAR(20),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "audit_logs": """
            CREATE TABLE audit_logs (
                audit_id VARCHAR(20) PRIMARY KEY,
                user_id VARCHAR(20),
                action_type VARCHAR(50),
                entity_type VARCHAR(50),
                entity_id VARCHAR(20),
                action_date DATE,
                action_time TIME,
                ip_address VARCHAR(50),
                user_agent VARCHAR(500),
                status_code VARCHAR(20),
                action_details VARCHAR(500),
                error_message VARCHAR(500),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "exchange_rates": """
            CREATE TABLE exchange_rates (
                rate_id VARCHAR(50) PRIMARY KEY,
                base_currency VARCHAR(3),
                target_currency VARCHAR(3),
                buy_rate DECIMAL(15,6),
                sell_rate DECIMAL(15,6),
                mid_rate DECIMAL(15,6),
                rate_date DATE,
                valid_from DATETIME,
                valid_to DATETIME,
                source VARCHAR(50),
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50)
            );
            """,
    "investment_accounts": """
            CREATE TABLE investment_accounts (
                investment_account_id BIGINT PRIMARY KEY, 
                customer_id VARCHAR(20),
                account_id VARCHAR(20) NOT NULL,                
                investment_type VARCHAR(50),
                risk_tolerance VARCHAR(20),
                account_status VARCHAR(20),
                investment_strategy VARCHAR(30),
                primary_asset_class VARCHAR(30),
                opening_date DATE,
                current_balance DECIMAL(18,2),
                total_deposits DECIMAL(18,2),
                ytd_return_rate DECIMAL(5,4),
                annual_return_rate DECIMAL(5,4),
                management_fee_rate DECIMAL(5,4),
                total_value DECIMAL(18,2),
                is_managed_account BIT,
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            );
            """,
    "fraud_alerts": """
            CREATE TABLE fraud_alerts (
                alert_id BIGINT PRIMARY KEY,               -- Changed to BIGINT
                transaction_id VARCHAR(20) NOT NULL,            
                account_id VARCHAR(20) NOT NULL,                
                customer_id VARCHAR(20),                       
                alert_timestamp DATETIME,
                detection_method VARCHAR(30),
                fraud_reason VARCHAR(50),
                fraud_type VARCHAR(30),
                severity VARCHAR(20),
                severity_score INT,
                alert_status VARCHAR(30),
                assigned_analyst_id VARCHAR(20),
                resolution_date DATETIME,
                financial_loss DECIMAL(18,2),
                is_false_positive BIT,
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50),
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
                FOREIGN KEY (account_id) REFERENCES accounts(account_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
            """,
    "user_logins": """
            CREATE TABLE user_logins (
                login_id BIGINT PRIMARY KEY,               -- Changed to BIGINT
                customer_id VARCHAR(20) NOT NULL,             
                login_timestamp DATETIME,
                ip_address VARCHAR(50),
                device_type VARCHAR(50),
                browser VARCHAR(30),
                operating_system VARCHAR(30),
                login_method VARCHAR(20),
                login_status VARCHAR(20),
                failure_reason VARCHAR(50),
                session_duration_minutes INT,
                geolocation VARCHAR(50),
                is_vpn_used BIT,
                created_at DATETIME,
                is_bad_data BIT DEFAULT 0,
                bad_data_type VARCHAR(50),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
            """,
    "data_quality_log": """
            CREATE TABLE data_quality_log (
                log_id INT IDENTITY(1,1) PRIMARY KEY,
                table_name VARCHAR(50),
                import_date DATETIME DEFAULT GETDATE(),
                total_records INT,
                bad_records INT,
                bad_percentage DECIMAL(5,2),
                error_count INT,
                success_count INT,
                duration_seconds INT
            );
            """

}
