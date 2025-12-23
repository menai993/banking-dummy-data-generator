#!/usr/bin/env python3
"""
Script to import generated data into MSSQL with bad data handling
"""

import pyodbc
import pandas as pd
import os
import json
from datetime import datetime

class MSSQLImporter:
    def __init__(self, server, database, username, password):
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        
    def create_tables_with_bad_data_tracking(self):
        """Create tables in MSSQL database with bad data tracking"""
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
                card_id VARCHAR(20) FOREIGN KEY REFERENCES cards(card_id),
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
            
            "data_quality_log": """
            CREATE TABLE data_quality_log (
                log_id INT IDENTITY(1,1) PRIMARY KEY,
                table_name VARCHAR(50),
                import_date DATETIME DEFAULT GETDATE(),
                total_records INT,
                bad_records INT,
                bad_percentage DECIMAL(5,2),
                error_count INT,
                success_count INT
            );
            """
        }
        
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            for table_name, create_stmt in create_statements.items():
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                    cursor.execute(create_stmt)
                    print(f"Created table: {table_name}")
                except Exception as e:
                    print(f"Error creating table {table_name}: {e}")
            
            conn.commit()
            conn.close()
            print("\nAll tables created successfully!")
            
        except Exception as e:
            print(f"Database connection error: {e}")
    
    def import_csv_with_quality_check(self, csv_file, table_name):
        """Import data from CSV file with data quality logging"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Count bad data
            bad_records = 0
            if 'is_bad_data' in df.columns:
                bad_records = df['is_bad_data'].sum()
            
            # Connect to database
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Prepare INSERT statement
            columns = ', '.join([col for col in df.columns if col not in ['Unnamed: 0']])
            placeholders = ', '.join(['?' for _ in df.columns if _ not in ['Unnamed: 0']])
            insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # Insert data row by row
            rows_imported = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    # Convert NaN to None
                    row_values = [None if pd.isna(val) else val for val in row.values 
                                 if row.name not in ['Unnamed: 0']]
                    
                    cursor.execute(insert_stmt, tuple(row_values))
                    rows_imported += 1
                except Exception as e:
                    error_count += 1
                    # Log error but continue
                    if error_count <= 5:  # Only show first 5 errors
                        print(f"  Error importing row {_}: {str(e)[:100]}")
                    continue
            
            # Log data quality metrics
            if table_name != "data_quality_log":
                log_stmt = """
                INSERT INTO data_quality_log 
                (table_name, total_records, bad_records, bad_percentage, error_count, success_count)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                
                bad_percentage = (bad_records / len(df) * 100) if len(df) > 0 else 0
                cursor.execute(log_stmt, (
                    table_name,
                    len(df),
                    int(bad_records),
                    float(bad_percentage),
                    error_count,
                    rows_imported
                ))
            
            conn.commit()
            conn.close()
            
            print(f"Imported {rows_imported} rows into {table_name} ({error_count} errors, {bad_records} bad records)")
            return rows_imported, error_count, bad_records
            
        except Exception as e:
            print(f"Error importing {csv_file}: {e}")
            return 0, 0, 0
    
    def import_all_data(self, data_dir="output"):
        """Import all CSV files from directory with quality tracking"""
        files_to_import = [
            ("customers.csv", "customers"),
            ("customer_details.csv", "customer_details"),
            ("accounts.csv", "accounts"),
            ("cards.csv", "cards"),
            ("transactions.csv", "transactions")
        ]
        
        total_rows = 0
        total_errors = 0
        total_bad = 0
        
        print("=" * 60)
        print("IMPORTING DATA WITH QUALITY TRACKING")
        print("=" * 60)
        
        for filename, table_name in files_to_import:
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                print(f"\nImporting {filename}...")
                rows, errors, bad = self.import_csv_with_quality_check(filepath, table_name)
                total_rows += rows
                total_errors += errors
                total_bad += bad
            else:
                print(f"File not found: {filepath}")
        
        # Read and display data quality report
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM data_quality_log ORDER BY import_date DESC")
            rows = cursor.fetchall()
            
            if rows:
                print("\n" + "=" * 60)
                print("DATA QUALITY REPORT")
                print("=" * 60)
                print(f"{'Table':20} {'Total':>8} {'Bad':>8} {'% Bad':>8} {'Errors':>8} {'Success':>8}")
                print("-" * 60)
                
                for row in rows:
                    print(f"{row.table_name:20} {row.total_records:8} {row.bad_records:8} {row.bad_percentage:8.1f} {row.error_count:8} {row.success_count:8}")
            
            conn.close()
        except Exception as e:
            print(f"Could not retrieve quality report: {e}")
        
        print(f"\nImport Summary:")
        print(f"  Total rows imported: {total_rows}")
        print(f"  Total errors: {total_errors}")
        print(f"  Total bad records: {total_bad}")
        
        return total_rows

def main():
    print("=" * 60)
    print("MSSQL DATA IMPORTER WITH BAD DATA HANDLING")
    print("=" * 60)
    
    # Configuration - Update these values for your MSSQL server
    CONFIG = {
        "server": "localhost",
        "database": "BankingDB",
        "username": "sa",
        "password": "YourPassword123",
        "data_directory": "output",
        "enable_quality_tracking": True
    }
    
    # Update with your actual credentials
    print("\nPlease update the connection settings in import_to_mssql.py")
    print("Current settings:")
    for key, value in CONFIG.items():
        print(f"  {key}: {value}")
    
    response = input("\nProceed with import? (yes/no): ")
    if response.lower() != 'yes':
        print("Import cancelled.")
        return
    
    # Create importer instance
    importer = MSSQLImporter(
        CONFIG["server"],
        CONFIG["database"],
        CONFIG["username"],
        CONFIG["password"]
    )
    
    try:
        # Step 1: Create tables
        print("\n[1/2] Creating tables with data quality tracking...")
        importer.create_tables_with_bad_data_tracking()
        
        # Step 2: Import data
        print("\n[2/2] Importing data with quality checks...")
        importer.import_all_data(CONFIG["data_directory"])
        
        print("\n" + "=" * 60)
        print("DATA IMPORT COMPLETE")
        print("=" * 60)
        
        # Provide SQL queries for data quality analysis
        print("\nUseful SQL Queries for Data Quality Analysis:")
        print("1. Count bad data by table:")
        print("   SELECT table_name, SUM(bad_records) as total_bad FROM data_quality_log GROUP BY table_name")
        print("\n2. Find all bad customer records:")
        print("   SELECT * FROM customers WHERE is_bad_data = 1")
        print("\n3. Find invalid emails:")
        print("   SELECT customer_id, email FROM customers WHERE email NOT LIKE '%@%.%'")
        print("\n4. Find negative balances:")
        print("   SELECT account_id, balance FROM accounts WHERE balance < 0")
        print("\n5. Find expired cards:")
        print("   SELECT card_id, expiration_date FROM cards WHERE expiration_date < FORMAT(GETDATE(), 'MM/yy')")
        
    except Exception as e:
        print(f"\nError during import: {e}")

if __name__ == "__main__":
    main()