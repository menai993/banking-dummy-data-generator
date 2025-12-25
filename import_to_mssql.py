#!/usr/bin/env python3
"""
Script to import generated data into MSSQL with bad data handling
Supports all 12 tables from the banking data generator
"""

import pyodbc
import pandas as pd
import os
import config
import re
from datetime import datetime
from utils.helpers import DataExporter 


class MSSQLImporter:
    def __init__(self, server, database, username, password):
        """
        Initialize MSSQL connection
        
        Args:
            server: SQL Server instance (e.g., 'localhost' or 'SERVERNAME\\INSTANCE')
            database: Database name
            username: SQL Server login username
            password: SQL Server login password
        """
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        
    def test_connection(self):
        """Test database connection"""
        try:
            conn = pyodbc.connect(self.connection_string)
            conn.close()
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def create_tables_with_bad_data_tracking(self):
        """Create all 12 tables in MSSQL database with bad data tracking"""
        print("\n" + "=" * 60)
        print("CREATING ALL TABLES WITH DATA QUALITY TRACKING")
        print("=" * 60)
        
        create_statements = {
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
        
        if any(value > 0 for value in config.CONFIG["bad_data_percentage"].values()):
            for table_name, sql in create_statements.items():
                create_statements[table_name] = re.sub(r'VARCHAR\s*\(\s*\d+\s*\)', 'VARCHAR(500)', sql, flags=re.IGNORECASE)
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Drop tables in reverse order (due to foreign key constraints)
            tables_to_drop = list(create_statements.keys())
            tables_to_drop.reverse()  # Drop child tables first
            
            print("Dropping existing tables if they exist...")
            for table_name in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                    print(f"  Dropped: {table_name}")
                except Exception as e:
                    print(f"  Warning dropping {table_name}: {e}")
            
            print("\nCreating new tables...")
            for table_name, create_stmt in create_statements.items():
                try:
                    cursor.execute(create_stmt)
                    print(f"  Created: {table_name}")
                except Exception as e:
                    print(f"  Error creating table {table_name}: {e}")
            
            conn.commit()
            conn.close()
            print("\n✅ All tables created successfully!")
            
        except Exception as e:
            print(f"❌ Database connection/creation error: {e}")
            return False
    

    
    def import_csv_with_quality_check(self, csv_file, table_name, batch_size=1000):
        """
        Import data from CSV file with data quality logging
        
        Args:
            csv_file: Path to CSV file
            table_name: Target table name
            batch_size: Number of rows to insert in each batch
        """
        try:
            # Read CSV file
            print(f"  Reading {csv_file}...")
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
            
            # Handle potential encoding issues
            if df.empty:
                print(f"  Warning: {csv_file} is empty or could not be read")
                return 0, 0, 0
            
            # Count bad data
            bad_records = 0
            if 'is_bad_data' in df.columns:
                bad_records = df['is_bad_data'].sum()
            
            # Connect to database
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Prepare INSERT statement
            columns = [col for col in df.columns if col != 'Unnamed: 0']
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['?' for _ in columns])
            insert_stmt = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Insert data in batches
            rows_imported = 0
            error_count = 0
            start_time = datetime.now()
            
            total_rows = len(df)
            print(f"  Importing {total_rows:,} rows in batches of {batch_size}...")
            
            for start_idx in range(0, total_rows, batch_size):
                end_idx = min(start_idx + batch_size, total_rows)
                batch = df.iloc[start_idx:end_idx]
                
                batch_errors = 0
                batch_success = 0
                
                for i, (_, row) in enumerate(batch.iterrows()):
                    try:
                        # Convert NaN to None and prepare values
                        row_values = []
                        for col in columns:
                            val = row[col]
                            if pd.isna(val):
                                row_values.append(None)
                            else:
                                row_values.append(val)
                        
                        cursor.execute(insert_stmt, tuple(row_values))
                        batch_success += 1
                    except Exception as e:
                        batch_errors += 1
                        csv_line = start_idx + i + 2
                        DataExporter.log_to_txt(f"|{csv_file}| CSV line {csv_line}: " + str(e),config.CONFIG["output_directory"])
                        if batch_errors <= 3:  # Show only first 3 errors per batch
                            print(f"    Row error at CSV line {csv_line}: {str(e)[:100]}")                           
                        continue
                
                rows_imported += batch_success
                error_count += batch_errors
                
                # Show progress
                if end_idx % (batch_size * 10) == 0 or end_idx == total_rows:
                    percent = (end_idx / total_rows) * 100
                    print(f"    Progress: {end_idx:,}/{total_rows:,} rows ({percent:.1f}%)")
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log data quality metrics
            if table_name != "data_quality_log":
                log_stmt = """
                INSERT INTO data_quality_log 
                (table_name, total_records, bad_records, bad_percentage, error_count, success_count, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                bad_percentage = (bad_records / total_rows * 100) if total_rows > 0 else 0
                cursor.execute(log_stmt, (
                    table_name,
                    total_rows,
                    int(bad_records),
                    float(bad_percentage),
                    error_count,
                    rows_imported,
                    int(duration)
                ))
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ Imported {rows_imported:,} rows into {table_name} "
                  f"({error_count:,} errors, {bad_records:,} bad records, {duration:.1f}s)")
            return rows_imported, error_count, bad_records
            
        except Exception as e:
            print(f"  ❌ Error importing {csv_file}: {e}")
            import traceback
            traceback.print_exc()
            return 0, 0, 0
    
    def import_all_data(self, data_dir="output"):
        """
        Import all CSV files from directory with quality tracking
        
        Args:
            data_dir: Directory containing CSV files
        """
        # Define all tables and their CSV files in correct import order
        # (respecting foreign key constraints)
        files_to_import = [
            # Level 1: Independent tables
            ("branches.csv", "branches"),
            ("customers.csv", "customers"),
            ("merchants.csv", "merchants"),
            ("exchange_rates.csv", "exchange_rates"),
            
            # Level 2: Depend on customers
            ("customer_details.csv", "customer_details"),
            ("accounts.csv", "accounts"),
            
            # Level 3: Depend on accounts and customers
            ("cards.csv", "cards"),
            ("loans.csv", "loans"),
            
            # Level 4: Depend on accounts, cards, loans
            ("transactions.csv", "transactions"),
            ("loan_payments.csv", "loan_payments"),

            # Level 5: Depend on transactions (for fraud alerts)
            ("fraud_alerts.csv", "fraud_alerts"),  # NEW: Depends on transactions
            
            # Level 6: Depend on branches
            ("employees.csv", "employees"),
            
            # Level 7: Depend on customers/employees
            ("audit_logs.csv", "audit_logs"),

            # Level 8: Depend on customers only
            ("user_logins.csv", "user_logins"),  # NEW: Depends on customers
        ]
        
        print("=" * 70)
        print("IMPORTING ALL 12 TABLES WITH FOREIGN KEY CONSTRAINT AWARENESS")
        print("=" * 70)
        
        total_rows = 0
        total_errors = 0
        total_bad = 0
        import_stats = {}
        
        # Check if files exist
        print("\nChecking for data files...")
        existing_files = []
        for filename, table_name in files_to_import:
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath) / (1024*1024)  # MB
                existing_files.append((filename, table_name, filepath, file_size))
                print(f"  ✓ {filename:25} ({file_size:.1f} MB)")
            else:
                print(f"  ✗ {filename:25} (File not found)")
        
        if not existing_files:
            print("\n❌ No data files found! Please run the generator first.")
            print("   Run: python main.py")
            return 0
        
        print(f"\nFound {len(existing_files)} data files. Starting import...")
        
        # Import files in order
        for filename, table_name, filepath, file_size in existing_files:
            print(f"\n{'='*70}")
            print(f"IMPORTING: {filename} ({file_size:.1f} MB)")
            print(f"TABLE: {table_name}")
            print(f"{'='*70}")
            
            # Adjust batch size based on file size
            batch_size = 500 if file_size > 10 else 1000
            batch_size = 250 if file_size > 50 else batch_size
            
            rows, errors, bad = self.import_csv_with_quality_check(
                filepath, table_name, batch_size=batch_size
            )
            
            total_rows += rows
            total_errors += errors
            total_bad += bad
            
            import_stats[table_name] = {
                'rows': rows,
                'errors': errors,
                'bad': bad,
                'file_size': file_size
            }
        
        # Generate import summary
        self._print_import_summary(total_rows, total_errors, total_bad, import_stats)
        
        # Read and display data quality report
        self._display_data_quality_report()
        
        # Generate SQL queries for analysis
        self._generate_analysis_queries()
        
        return total_rows
    
    def _print_import_summary(self, total_rows, total_errors, total_bad, import_stats):
        """Print import summary"""
        print("\n" + "=" * 70)
        print("IMPORT SUMMARY")
        print("=" * 70)
        
        print(f"{'Table Name':25} {'Rows':>10} {'Errors':>8} {'Bad':>8} {'% Bad':>8} {'Size (MB)':>10}")
        print("-" * 70)
        
        for table_name, stats in import_stats.items():
            bad_percentage = (stats['bad'] / stats['rows'] * 100) if stats['rows'] > 0 else 0
            print(f"{table_name:25} {stats['rows']:10,} {stats['errors']:8,} "
                  f"{stats['bad']:8,} {bad_percentage:8.1f} {stats['file_size']:10.1f}")
        
        print("-" * 70)
        total_bad_percentage = (total_bad / total_rows * 100) if total_rows > 0 else 0
        print(f"{'TOTAL':25} {total_rows:10,} {total_errors:8,} "
              f"{total_bad:8,} {total_bad_percentage:8.1f}")
        print("=" * 70)
    
    def _display_data_quality_report(self):
        """Display data quality report from database"""
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    table_name,
                    total_records,
                    bad_records,
                    bad_percentage,
                    error_count,
                    success_count,
                    duration_seconds,
                    import_date
                FROM data_quality_log 
                ORDER BY import_date DESC
            """)
            rows = cursor.fetchall()
            
            if rows:
                print("\n" + "=" * 70)
                print("DATA QUALITY REPORT FROM DATABASE")
                print("=" * 70)
                print(f"{'Table':20} {'Total':>8} {'Bad':>8} {'% Bad':>8} "
                      f"{'Errors':>8} {'Success':>8} {'Time(s)':>8}")
                print("-" * 70)
                
                for row in rows:
                    print(f"{row.table_name:20} {row.total_records:8,} {row.bad_records:8,} "
                          f"{row.bad_percentage:8.1f} {row.error_count:8,} "
                          f"{row.success_count:8,} {row.duration_seconds:8}")
            
            conn.close()
        except Exception as e:
            print(f"\nNote: Could not retrieve quality report: {e}")
    
    def _generate_analysis_queries(self):
        """Generate useful SQL queries for data analysis"""
        print("\n" + "=" * 70)
        print("USEFUL SQL QUERIES FOR DATA ANALYSIS")
        print("=" * 70)
        
        queries = {
            "1. Data Quality Overview": """
            -- Overall data quality
            SELECT 
                table_name,
                total_records,
                bad_records,
                ROUND(bad_percentage, 2) as bad_pct,
                error_count,
                success_count,
                duration_seconds
            FROM data_quality_log
            ORDER BY bad_percentage DESC;
            """,
            
            "2. Find All Bad Records": """
            -- Find bad records by table
            SELECT 
                'customers' as table_name,
                COUNT(*) as bad_count
            FROM customers WHERE is_bad_data = 1
            UNION ALL
            SELECT 'accounts', COUNT(*) FROM accounts WHERE is_bad_data = 1
            UNION ALL
            SELECT 'transactions', COUNT(*) FROM transactions WHERE is_bad_data = 1
            UNION ALL
            SELECT 'loans', COUNT(*) FROM loans WHERE is_bad_data = 1
            UNION ALL
            SELECT 'cards', COUNT(*) FROM cards WHERE is_bad_data = 1
            ORDER BY bad_count DESC;
            """,
            
            "3. Top 10 Customers by Number of Accounts": """
            -- Top 10 customers with most accounts
            SELECT TOP 10 
                c.customer_id,
                c.first_name + ' ' + c.last_name as customer_name,
                COUNT(a.account_id) as account_count,
                SUM(a.balance) as total_balance
            FROM customers c
            LEFT JOIN accounts a ON c.customer_id = a.customer_id
            GROUP BY c.customer_id, c.first_name, c.last_name
            ORDER BY account_count DESC, total_balance DESC;
            """,
            
            "4. Transaction Statistics": """
            -- Transaction statistics by type
            SELECT 
                transaction_type,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount
            FROM transactions
            GROUP BY transaction_type
            ORDER BY total_amount DESC;
            """,
            
            "5. Loan Portfolio Summary": """
            -- Loan portfolio summary
            SELECT 
                loan_type,
                COUNT(*) as loan_count,
                SUM(loan_amount) as total_loaned,
                AVG(interest_rate * 100) as avg_interest_rate_pct,
                SUM(remaining_balance) as total_outstanding,
                COUNT(CASE WHEN status IN ('Defaulted', 'In Arrears') THEN 1 END) as problem_loans
            FROM loans
            GROUP BY loan_type
            ORDER BY total_loaned DESC;
            """,
            
            "6. Branch Performance": """
            -- Branch performance metrics
            SELECT 
                b.branch_name,
                b.city,
                b.state,
                COUNT(DISTINCT a.customer_id) as customer_count,
                COUNT(a.account_id) as account_count,
                SUM(a.balance) as total_deposits,
                COUNT(DISTINCT e.employee_id) as employee_count
            FROM branches b
            LEFT JOIN employees e ON b.branch_id = e.branch_id
            LEFT JOIN accounts a ON 1=1  -- Simplified for demo
            GROUP BY b.branch_id, b.branch_name, b.city, b.state
            ORDER BY total_deposits DESC;
            """,
            
            "7. Merchant Categories Analysis": """
            -- Merchant categories analysis
            SELECT 
                category,
                COUNT(*) as merchant_count,
                COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_merchants,
                COUNT(CASE WHEN status = 'Inactive' THEN 1 END) as inactive_merchants
            FROM merchants
            GROUP BY category
            ORDER BY merchant_count DESC;
            """,
            
            "8. Find Data Quality Issues": """
            -- Find specific data quality issues
            -- Invalid emails
            SELECT customer_id, email 
            FROM customers 
            WHERE email NOT LIKE '%_@__%.__%' AND email IS NOT NULL
            
            UNION ALL
            
            -- Negative balances
            SELECT account_id, balance 
            FROM accounts 
            WHERE balance < 0
            
            UNION ALL
            
            -- Future birth dates
            SELECT customer_id, date_of_birth 
            FROM customers 
            WHERE date_of_birth > GETDATE()
            
            UNION ALL
            
            -- Inconsistent employment vs income
            SELECT c.customer_id, cd.annual_income, cd.employment_status
            FROM customers c
            JOIN customer_details cd ON c.customer_id = cd.customer_id
            WHERE cd.employment_status = 'Unemployed' AND cd.annual_income > 50000;
            """,
            
            "9. Exchange Rate Analysis": """
            -- Exchange rate analysis
            SELECT 
                base_currency + '/' + target_currency as currency_pair,
                COUNT(*) as rate_count,
                MIN(rate_date) as earliest_date,
                MAX(rate_date) as latest_date,
                AVG(mid_rate) as avg_rate,
                MIN(mid_rate) as min_rate,
                MAX(mid_rate) as max_rate
            FROM exchange_rates
            GROUP BY base_currency, target_currency
            ORDER BY currency_pair;
            """,
            
            "10. Audit Trail Analysis": """
            -- Audit trail analysis
            SELECT 
                action_type,
                entity_type,
                status_code,
                COUNT(*) as action_count,
                COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as error_count
            FROM audit_logs
            GROUP BY action_type, entity_type, status_code
            ORDER BY action_count DESC;
            """
        }
        
        for query_name, query in queries.items():
            print(f"\n{query_name}:")
            print("-" * 40)
            print(query.strip())
        
        print("\n" + "=" * 70)
        print("QUICK TIPS:")
        print("=" * 70)
        print("1. Run queries in SQL Server Management Studio (SSMS)")
        print("2. Export results to Excel for further analysis")
        print("3. Modify queries to fit your specific analysis needs")
        print("4. Check the 'data_quality_log' table for import statistics")
        print("5. Use WHERE is_bad_data = 1 to find problematic records")
    
    def create_database_views(self):
        """Create useful database views for analysis"""
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            views = {
                "v_customer_summary": """
                CREATE VIEW v_customer_summary AS
                SELECT 
                    c.customer_id,
                    c.first_name,
                    c.last_name,
                    c.email,
                    c.phone,
                    c.date_of_birth,
                    cd.employment_status,
                    cd.annual_income,
                    cd.credit_score,
                    COUNT(DISTINCT a.account_id) as account_count,
                    SUM(a.balance) as total_balance,
                    COUNT(DISTINCT cr.card_id) as card_count,
                    COUNT(DISTINCT l.loan_id) as loan_count,
                    SUM(l.loan_amount) as total_loans,
                    c.created_at
                FROM customers c
                LEFT JOIN customer_details cd ON c.customer_id = cd.customer_id
                LEFT JOIN accounts a ON c.customer_id = a.customer_id
                LEFT JOIN cards cr ON c.customer_id = cr.customer_id
                LEFT JOIN loans l ON c.customer_id = l.customer_id
                GROUP BY 
                    c.customer_id, c.first_name, c.last_name, c.email, c.phone, 
                    c.date_of_birth, cd.employment_status, cd.annual_income, 
                    cd.credit_score, c.created_at;
                """,
                
                "v_branch_performance": """
                CREATE VIEW v_branch_performance AS
                SELECT 
                    b.branch_id,
                    b.branch_name,
                    b.city,
                    b.state,
                    b.manager_name,
                    COUNT(DISTINCT e.employee_id) as employee_count,
                    (SELECT COUNT(*) FROM customers) as total_customers_assigned,
                    b.opening_date,
                    b.created_at
                FROM branches b
                LEFT JOIN employees e ON b.branch_id = e.branch_id
                GROUP BY 
                    b.branch_id, b.branch_name, b.city, b.state, 
                    b.manager_name, b.opening_date, b.created_at;
                """,
                
                "v_daily_transactions": """
                CREATE VIEW v_daily_transactions AS
                SELECT 
                    CAST(transaction_date AS DATE) as transaction_day,
                    transaction_type,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(CASE WHEN status = 'Failed' THEN 1 END) as failed_count
                FROM transactions
                GROUP BY CAST(transaction_date AS DATE), transaction_type;
                """
            }
            
            print("\nCreating database views...")
            for view_name, view_sql in views.items():
                try:
                    cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
                    cursor.execute(view_sql)
                    print(f"  Created view: {view_name}")
                except Exception as e:
                    print(f"  Error creating view {view_name}: {e}")
            
            conn.commit()
            conn.close()
            print("✅ Database views created successfully!")
            
        except Exception as e:
            print(f"Error creating views: {e}")


def main():
    print("=" * 70)
    print("MSSQL DATA IMPORTER - COMPLETE BANKING DATABASE")
    print("=" * 70)
    print("This script will:")
    print("  1. Create 12 banking tables with data quality tracking")
    print("  2. Import all generated CSV files")
    print("  3. Create useful database views")
    print("  4. Generate analysis queries")
    print("=" * 70)
    
    # Configuration - UPDATE THESE FOR YOUR ENVIRONMENT
    CONFIG = {
        "server": "localhost",              # Your SQL Server
        "database": "YourDatabase",      # Your database name
        "username": "YourUsername",             # SQL Server login
        "password": "YourPassword",             # SQL Server password
        "data_directory": "output",         # Directory with CSV files
        "enable_quality_tracking": True,    # Quality tracking enablement
        "create_views": True,               # Create database views
        "batch_size": 1000                  # Rows per batch insert
    }
    

    # Display current configuration
    print("\nCURRENT CONFIGURATION:")
    print("-" * 40)
    for key, value in CONFIG.items():
        if key == "password":
            print(f"  {key:20} {'*' * len(str(value))}")
        else:
            print(f"  {key:20} {value}")
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will drop existing tables if they exist!")
    response = input("\nProceed with import? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Import cancelled.")
        return
    
    # Test database connection
    print("\nTesting database connection...")
    importer = MSSQLImporter(
        CONFIG["server"],
        CONFIG["database"],
        CONFIG["username"],
        CONFIG["password"]
    )
    
    if not importer.test_connection():
        print("\n❌ Cannot connect to database. Please check:")
        print("  1. SQL Server is running")
        print("  2. Database exists (create it if needed)")
        print("  3. Login credentials are correct")
        print("  4. ODBC Driver 17 is installed")
        return
    
    try:
        # Step 1: Create tables
        print("\n" + "=" * 70)
        print("STEP 1: CREATING TABLES")
        print("=" * 70)
        importer.create_tables_with_bad_data_tracking()
        
        # Step 2: Import data
        print("\n" + "=" * 70)
        print("STEP 2: IMPORTING DATA")
        print("=" * 70)
        total_rows = importer.import_all_data(CONFIG["data_directory"])
        
        # Step 3: Create views (optional)
        if CONFIG["create_views"] and total_rows > 0:
            print("\n" + "=" * 70)
            print("STEP 3: CREATING DATABASE VIEWS")
            print("=" * 70)
            importer.create_database_views()
        
        # Final success message
        print("\n" + "=" * 70)
        print("✅ IMPORT COMPLETE!")
        print("=" * 70)
        print(f"Total rows imported: {total_rows:,}")
        print("\nNext steps:")
        print("  1. Open SQL Server Management Studio")
        print("  2. Connect to your database")
        print("  3. Run the provided analysis queries")
        print("  4. Check the 'data_quality_log' table for import stats")
        print("  5. Check the 'import_errors.txt' file for import errors")
        print("\nGenerated files are in 'output/' directory")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()