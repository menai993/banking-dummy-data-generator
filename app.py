#!/usr/bin/env python3
"""
Streamlit Web UI for Banking Dummy Data Generator
Provides a user-friendly interface for all features:
- Data Generation (main.py)
- MSSQL Import (import_to_mssql.py)
- CDC Management (enable_cdc.py)
- CDC Simulation (data_generator_mssql.py)
"""

import streamlit as st
import os
import json
import time
from datetime import datetime
import pandas as pd
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
import config
from main import (
    CustomerGenerator, AccountGenerator, CardGenerator, TransactionGenerator,
    BranchGenerator, EmployeeGenerator, LoanGenerator, MerchantGenerator,
    AuditLogGenerator, ExchangeRateGenerator, InvestmentAccountGenerator,
    FraudAlertGenerator, UserLoginGenerator
)
from utils.helpers import DataExporter
from import_to_mssql import MSSQLImporter
import enable_cdc
from data_generator_mssql import CDCDataSimulator

# Page configuration
st.set_page_config(
    page_title="Banking Data Generator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'import_stats' not in st.session_state:
    st.session_state.import_stats = None

def main():
    # Sidebar navigation
    st.sidebar.markdown("# 🏦 Banking Data Generator")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📊 Data Generation", "📥 MSSQL Import", "🔄 CDC Management", "⚡ CDC Simulation"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This tool generates realistic banking data with configurable bad data "
        "percentages and provides utilities for importing to MSSQL and managing CDC."
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 Data Generation":
        show_data_generation_page()
    elif page == "📥 MSSQL Import":
        show_mssql_import_page()
    elif page == "🔄 CDC Management":
        show_cdc_management_page()
    elif page == "⚡ CDC Simulation":
        show_cdc_simulation_page()

def show_home_page():
    st.markdown('<div class="main-header">🏦 Banking Dummy Data Generator</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Welcome to the Banking Data Generator Web Interface
    
    This application provides a comprehensive suite of tools for generating, importing, and managing banking data:
    
    ### 🎯 Features
    
    #### 📊 Data Generation
    - Generate realistic banking data including customers, accounts, transactions, loans, cards, and more
    - Configure bad data percentages for data quality testing
    - Export to CSV, SQL, and Excel formats
    - Generate detailed quality reports
    
    #### 📥 MSSQL Import
    - Import generated data into Microsoft SQL Server
    - Create database tables with quality tracking
    - Batch import with progress monitoring
    - Generate useful analysis queries and views
    
    #### 🔄 CDC Management
    - Enable/Disable Change Data Capture (CDC) on database
    - Manage CDC for individual tables
    - View CDC status and enabled tables
    
    #### ⚡ CDC Simulation
    - Simulate real-time data changes (INSERT, UPDATE, DELETE)
    - Configure operation weights and counts
    - Track operation success/failure
    
    ### 🚀 Getting Started
    
    1. **Generate Data**: Start by generating banking data using the Data Generation page
    2. **Import to MSSQL**: Import the generated data to your SQL Server database
    3. **Enable CDC**: Enable Change Data Capture to track data changes
    4. **Simulate Changes**: Use CDC Simulation to generate realistic data changes
    
    ### 📝 Current Configuration
    """)
    
    # Display current configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Customers", f"{config.CONFIG['num_customers']:,}")
        st.metric("Branches", f"{config.CONFIG['num_branches']:,}")
    
    with col2:
        st.metric("Employees", f"{config.CONFIG['num_employees']:,}")
        st.metric("Merchants", f"{config.CONFIG['num_merchants']:,}")
    
    with col3:
        st.metric("Output Directory", config.CONFIG['output_directory'])
        st.metric("Output Formats", ", ".join(config.CONFIG['output_formats']))
    
    st.markdown("---")
    st.info("👈 Use the navigation menu on the left to access different features")

def show_data_generation_page():
    st.markdown('<div class="main-header">📊 Data Generation</div>', unsafe_allow_html=True)
    
    st.markdown("### Configuration")
    
    # Create tabs for different configuration sections
    tab1, tab2, tab3 = st.tabs(["📈 Volume Settings", "⚠️ Bad Data Settings", "💾 Output Settings"])
    
    with tab1:
        st.markdown("#### Volume Controls")
        col1, col2 = st.columns(2)
        
        with col1:
            num_customers = st.number_input("Number of Customers", min_value=10, max_value=100000, 
                                          value=config.CONFIG['num_customers'], step=100)
            num_branches = st.number_input("Number of Branches", min_value=1, max_value=1000, 
                                         value=config.CONFIG['num_branches'], step=10)
            num_employees = st.number_input("Number of Employees", min_value=1, max_value=10000, 
                                          value=config.CONFIG['num_employees'], step=50)
            num_merchants = st.number_input("Number of Merchants", min_value=1, max_value=10000, 
                                          value=config.CONFIG['num_merchants'], step=50)
        
        with col2:
            accounts_min = st.number_input("Accounts per Customer (Min)", min_value=0, max_value=10, 
                                         value=config.CONFIG['accounts_per_customer_min'])
            accounts_max = st.number_input("Accounts per Customer (Max)", min_value=1, max_value=20, 
                                         value=config.CONFIG['accounts_per_customer_max'])
            transactions_min = st.number_input("Transactions per Account (Min)", min_value=0, max_value=100, 
                                             value=config.CONFIG['transactions_per_account_min'])
            transactions_max = st.number_input("Transactions per Account (Max)", min_value=1, max_value=500, 
                                             value=config.CONFIG['transactions_per_account_max'])
    
    with tab2:
        st.markdown("#### Bad Data Percentages")
        st.info("Configure the percentage of bad data for each entity type")
        
        col1, col2, col3 = st.columns(3)
        
        bad_data_config = {}
        entities = list(config.CONFIG['bad_data_percentage'].keys())
        
        for i, entity in enumerate(entities):
            col = [col1, col2, col3][i % 3]
            with col:
                bad_data_config[entity] = st.slider(
                    f"{entity.replace('_', ' ').title()}", 
                    0.0, 1.0, 
                    config.CONFIG['bad_data_percentage'][entity],
                    0.01,
                    format="%.2f"
                )
    
    with tab3:
        st.markdown("#### Output Settings")
        
        output_formats = st.multiselect(
            "Output Formats",
            ["csv", "sql", "excel"],
            default=config.CONFIG['output_formats']
        )
        
        output_directory = st.text_input("Output Directory", value=config.CONFIG['output_directory'])
    
    st.markdown("---")
    
    # Generate button
    if st.button("🚀 Generate Data", type="primary", use_container_width=True):
        generate_data(num_customers, num_branches, num_employees, num_merchants,
                     accounts_min, accounts_max, transactions_min, transactions_max,
                     bad_data_config, output_formats, output_directory)

def generate_data(num_customers, num_branches, num_employees, num_merchants,
                 accounts_min, accounts_max, transactions_min, transactions_max,
                 bad_data_config, output_formats, output_directory):
    """Generate banking data with progress tracking"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        start_time = time.time()
        all_data = {}
        
        # Step 1: Generate Customers
        status_text.text("Generating customers...")
        progress_bar.progress(1/14)
        customer_gen = CustomerGenerator(num_customers, bad_data_config['customers'])
        customers, customer_details = customer_gen.generate()
        all_data['customers'] = customers
        all_data['customer_details'] = customer_details
        
        # Step 2: Generate Accounts
        status_text.text("Generating accounts...")
        progress_bar.progress(2/14)
        account_gen = AccountGenerator(customers, bad_data_config['accounts'])
        accounts = account_gen.generate(accounts_min, accounts_max)
        all_data['accounts'] = accounts
        
        # Step 3: Generate Cards
        status_text.text("Generating cards...")
        progress_bar.progress(3/14)
        card_gen = CardGenerator(customers, accounts, bad_data_config['cards'])
        cards = card_gen.generate(config.CONFIG['cards_per_customer_min'], 
                                 config.CONFIG['cards_per_customer_max'])
        all_data['cards'] = cards
        
        # Step 4: Generate Transactions
        status_text.text("Generating transactions...")
        progress_bar.progress(4/14)
        transaction_gen = TransactionGenerator(accounts, cards, bad_data_config['transactions'])
        transactions = transaction_gen.generate(transactions_min, transactions_max)
        all_data['transactions'] = transactions
        
        # Step 5: Generate Branches
        status_text.text("Generating branches...")
        progress_bar.progress(5/14)
        branch_gen = BranchGenerator(num_branches, bad_data_config['branches'])
        branches = branch_gen.generate()
        all_data['branches'] = branches
        
        # Step 6: Generate Employees
        status_text.text("Generating employees...")
        progress_bar.progress(6/14)
        employee_gen = EmployeeGenerator(branches, num_employees, bad_data_config['employees'])
        employees = employee_gen.generate()
        all_data['employees'] = employees
        
        # Step 7: Generate Loans
        status_text.text("Generating loans...")
        progress_bar.progress(7/14)
        loan_gen = LoanGenerator(customers, accounts, bad_data_config['loans'])
        loans, loan_payments = loan_gen.generate(
            config.CONFIG['loans_per_customer_min'],
            config.CONFIG['loans_per_customer_max']
        )
        all_data['loans'] = loans
        all_data['loan_payments'] = loan_payments
        
        # Step 8: Generate Merchants
        status_text.text("Generating merchants...")
        progress_bar.progress(8/14)
        merchant_gen = MerchantGenerator(num_merchants, bad_data_config['merchants'])
        merchants = merchant_gen.generate()
        all_data['merchants'] = merchants
        
        # Step 9: Generate Audit Logs
        status_text.text("Generating audit logs...")
        progress_bar.progress(9/14)
        all_users = customers + employees
        audit_gen = AuditLogGenerator(all_users, bad_data_config['audit_logs'])
        audit_logs = audit_gen.generate(
            config.CONFIG['audit_logs_per_user_min'],
            config.CONFIG['audit_logs_per_user_max']
        )
        all_data['audit_logs'] = audit_logs
        
        # Step 10: Generate Exchange Rates
        status_text.text("Generating exchange rates...")
        progress_bar.progress(10/14)
        exchange_gen = ExchangeRateGenerator(
            config.CONFIG['exchange_rate_days'],
            bad_data_config['exchange_rates']
        )
        exchange_rates = exchange_gen.generate()
        all_data['exchange_rates'] = exchange_rates
        
        # Step 11: Generate Investment Accounts
        status_text.text("Generating investment accounts...")
        progress_bar.progress(11/14)
        investment_gen = InvestmentAccountGenerator(
            config.CONFIG.get("num_investment_accounts"),
            bad_data_config['investment_accounts'],
            customers,
            accounts
        )
        investment_accounts = investment_gen.generate()
        all_data['investment_accounts'] = investment_accounts
        
        # Step 12: Generate Fraud Alerts
        status_text.text("Generating fraud alerts...")
        progress_bar.progress(12/14)
        fraud_gen = FraudAlertGenerator(
            config.CONFIG.get("fraud_alerts_per_transaction", 0.05),
            bad_data_config['fraud_alerts'],
            transactions
        )
        fraud_alerts = fraud_gen.generate()
        all_data['fraud_alerts'] = fraud_alerts
        
        # Step 13: Generate User Logins
        status_text.text("Generating user logins...")
        progress_bar.progress(13/14)
        login_gen = UserLoginGenerator(
            config.CONFIG.get("user_logins_per_customer_min", 8),
            config.CONFIG.get("user_logins_per_customer_max", 30),
            bad_data_config['user_logins'],
            customers
        )
        user_logins = login_gen.generate()
        all_data['user_logins'] = user_logins
        
        # Step 14: Export Data
        status_text.text("Exporting data...")
        progress_bar.progress(14/14)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        exporter = DataExporter()
        
        if "csv" in output_formats:
            for table_name, data in all_data.items():
                if data:
                    exporter.export_to_csv(data, f"{table_name}.csv")
        
        if "sql" in output_formats:
            exporter.export_to_sql_files(all_data)
        
        if "excel" in output_formats:
            clean_data = {}
            for table_name, data in all_data.items():
                clean_records = []
                for record in data:
                    clean_record = {k: v for k, v in record.items() if k not in ['is_bad_data', 'bad_data_type']}
                    clean_records.append(clean_record)
                clean_data[table_name] = clean_records
            exporter.export_to_excel(clean_data)
        
        # Calculate statistics
        total_records = sum(len(data) for data in all_data.values() if data)
        total_bad = sum(sum(1 for record in data if record.get('is_bad_data', False)) 
                       for data in all_data.values() if data)
        
        elapsed_time = time.time() - start_time
        
        # Store in session state
        st.session_state.generated_data = all_data
        
        # Success message
        progress_bar.progress(1.0)
        status_text.empty()
        
        st.success(f"✅ Data generation complete! Generated {total_records:,} records in {elapsed_time:.2f} seconds")
        
        # Display statistics
        st.markdown("### 📊 Generation Statistics")
        
        stats_data = []
        for table_name, data in all_data.items():
            if data:
                bad_count = sum(1 for record in data if record.get('is_bad_data', False))
                percentage = (bad_count / len(data) * 100) if len(data) > 0 else 0
                stats_data.append({
                    'Table': table_name,
                    'Total Records': len(data),
                    'Bad Records': bad_count,
                    'Bad %': f"{percentage:.2f}%"
                })
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
        
        # Display output files
        st.markdown("### 📁 Generated Files")
        files = [f for f in os.listdir(output_directory) if not f.startswith('.')]
        st.write(f"Generated {len(files)} files in `{output_directory}/` directory")
        
        with st.expander("View Files"):
            for file in sorted(files):
                st.text(f"• {file}")
        
    except Exception as e:
        st.error(f"❌ Error during data generation: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_mssql_import_page():
    st.markdown('<div class="main-header">📥 MSSQL Import</div>', unsafe_allow_html=True)
    
    st.markdown("### Database Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        server = st.text_input("Server", value=config.CONFIG['mssql_import']['server'])
        database = st.text_input("Database", value=config.CONFIG['mssql_import']['database'])
        username = st.text_input("Username", value=config.CONFIG['mssql_import']['username'])
    
    with col2:
        password = st.text_input("Password", type="password", value=config.CONFIG['mssql_import']['password'])
        data_directory = st.text_input("Data Directory", value=config.CONFIG['mssql_import']['data_directory'])
        batch_size = st.number_input("Batch Size", min_value=100, max_value=10000, 
                                     value=config.CONFIG['mssql_import']['batch_size'], step=100)
    
    create_views = st.checkbox("Create Database Views", value=config.CONFIG['mssql_import']['create_views'])
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔌 Test Connection", use_container_width=True):
            test_database_connection(server, database, username, password)
    
    with col2:
        if st.button("🏗️ Create Tables", use_container_width=True):
            create_database_tables(server, database, username, password)
    
    with col3:
        if st.button("📥 Import Data", type="primary", use_container_width=True):
            import_data_to_mssql(server, database, username, password, data_directory, 
                                batch_size, create_views)

def test_database_connection(server, database, username, password):
    """Test database connection"""
    with st.spinner("Testing connection..."):
        try:
            importer = MSSQLImporter(server, database, username, password)
            if importer.test_connection():
                st.success("✅ Database connection successful!")
            else:
                st.error("❌ Database connection failed!")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")

def create_database_tables(server, database, username, password):
    """Create database tables"""
    with st.spinner("Creating tables..."):
        try:
            importer = MSSQLImporter(server, database, username, password)
            importer.create_tables_with_bad_data_tracking()
            st.success("✅ Tables created successfully!")
        except Exception as e:
            st.error(f"❌ Error creating tables: {str(e)}")
            st.code(str(e))

def import_data_to_mssql(server, database, username, password, data_directory, 
                         batch_size, create_views):
    """Import data to MSSQL with progress tracking"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        importer = MSSQLImporter(server, database, username, password)
        
        # Define files to import
        files_to_import = [
            ("branches.csv", "branches"),
            ("customers.csv", "customers"),
            ("merchants.csv", "merchants"),
            ("exchange_rates.csv", "exchange_rates"),
            ("customer_details.csv", "customer_details"),
            ("accounts.csv", "accounts"),
            ("cards.csv", "cards"),
            ("loans.csv", "loans"),
            ("transactions.csv", "transactions"),
            ("loan_payments.csv", "loan_payments"),
            ("fraud_alerts.csv", "fraud_alerts"),
            ("employees.csv", "employees"),
            ("audit_logs.csv", "audit_logs"),
            ("user_logins.csv", "user_logins"),
        ]
        
        # Check existing files
        existing_files = []
        for filename, table_name in files_to_import:
            filepath = os.path.join(data_directory, filename)
            if os.path.exists(filepath):
                existing_files.append((filename, table_name, filepath))
        
        if not existing_files:
            st.error("❌ No data files found! Please generate data first.")
            return
        
        total_files = len(existing_files)
        import_stats = {}
        
        # Import each file
        for i, (filename, table_name, filepath) in enumerate(existing_files):
            status_text.text(f"Importing {filename} ({i+1}/{total_files})...")
            progress_bar.progress((i + 1) / total_files)
            
            rows, errors, bad = importer.import_csv_with_quality_check(
                filepath, table_name, batch_size=batch_size
            )
            
            import_stats[table_name] = {
                'rows': rows,
                'errors': errors,
                'bad': bad
            }
        
        # Create views if requested
        if create_views:
            status_text.text("Creating database views...")
            importer.create_database_views()
        
        # Store stats in session state
        st.session_state.import_stats = import_stats
        
        # Success message
        progress_bar.progress(1.0)
        status_text.empty()
        
        total_rows = sum(stats['rows'] for stats in import_stats.values())
        total_errors = sum(stats['errors'] for stats in import_stats.values())
        total_bad = sum(stats['bad'] for stats in import_stats.values())
        
        st.success(f"✅ Import complete! Imported {total_rows:,} rows with {total_errors:,} errors")
        
        # Display import statistics
        st.markdown("### 📊 Import Statistics")
        
        stats_data = []
        for table_name, stats in import_stats.items():
            bad_pct = (stats['bad'] / stats['rows'] * 100) if stats['rows'] > 0 else 0
            stats_data.append({
                'Table': table_name,
                'Rows': stats['rows'],
                'Errors': stats['errors'],
                'Bad Records': stats['bad'],
                'Bad %': f"{bad_pct:.2f}%"
            })
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error during import: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_cdc_management_page():
    st.markdown('<div class="main-header">🔄 CDC Management</div>', unsafe_allow_html=True)
    
    st.markdown("### Database Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        server = st.text_input("Server", value=config.CONFIG['mssql_import']['server'], key="cdc_server")
        database = st.text_input("Database", value=config.CONFIG['mssql_import']['database'], key="cdc_database")
    
    with col2:
        username = st.text_input("Username", value=config.CONFIG['mssql_import']['username'], key="cdc_username")
        password = st.text_input("Password", type="password", value=config.CONFIG['mssql_import']['password'], key="cdc_password")
    
    st.markdown("---")
    
    # Check CDC Status button
    if st.button("🔍 Check CDC Status", use_container_width=True):
        check_cdc_status(server, database, username, password)
    
    st.markdown("---")
    
    # Enable/Disable CDC buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Enable CDC", type="primary", use_container_width=True):
            enable_cdc(server, database, username, password)
    
    with col2:
        if st.button("❌ Disable CDC", use_container_width=True):
            disable_cdc(server, database, username, password)

def check_cdc_status(server, database, username, password):
    """Check CDC status"""
    try:
        conn = enable_cdc.get_connection()
        cursor = conn.cursor()
        
        db_enabled = enable_cdc.is_cdc_enabled_db(cursor)
        
        st.markdown("### 📊 CDC Status")
        
        if db_enabled:
            st.success(f"✅ CDC is **ENABLED** on database: {database}")
            
            enabled_tables = enable_cdc.get_enabled_tables(cursor)
            
            if enabled_tables:
                st.markdown(f"#### Enabled Tables ({len(enabled_tables)})")
                
                # Display as a nice table
                table_data = [{"Table Name": table} for table in enabled_tables]
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)
            else:
                st.info("ℹ️ CDC is enabled on database but no tables have CDC enabled")
        else:
            st.warning(f"⚠️ CDC is **DISABLED** on database: {database}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Error checking CDC status: {str(e)}")

def enable_cdc(server, database, username, password):
    """Enable CDC on database and all tables"""
    with st.spinner("Enabling CDC..."):
        try:
            # Update config temporarily
            original_config = config.CONFIG['mssql_import'].copy()
            config.CONFIG['mssql_import']['server'] = server
            config.CONFIG['mssql_import']['database'] = database
            config.CONFIG['mssql_import']['username'] = username
            config.CONFIG['mssql_import']['password'] = password
            
            conn = enable_cdc.get_connection()
            cursor = conn.cursor()
            
            # Load CREATE_STATEMENTS
            from config.create_statements import CREATE_STATEMENTS
            tables = list(CREATE_STATEMENTS.keys())
            
            # Enable CDC on database
            enable_cdc.enable_cdc_db(cursor)
            
            # Enable CDC on all tables
            for table in tables:
                enable_cdc.enable_cdc_table(cursor, "dbo", table)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Restore original config
            config.CONFIG['mssql_import'] = original_config
            
            st.success(f"✅ CDC enabled successfully on database and {len(tables)} tables!")
            
        except Exception as e:
            st.error(f"❌ Error enabling CDC: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

def disable_cdc(server, database, username, password):
    """Disable CDC on all tables and database"""
    with st.spinner("Disabling CDC..."):
        try:
            # Update config temporarily
            original_config = config.CONFIG['mssql_import'].copy()
            config.CONFIG['mssql_import']['server'] = server
            config.CONFIG['mssql_import']['database'] = database
            config.CONFIG['mssql_import']['username'] = username
            config.CONFIG['mssql_import']['password'] = password
            
            conn = enable_cdc.get_connection()
            cursor = conn.cursor()
            
            # Load CREATE_STATEMENTS
            from config.create_statements import CREATE_STATEMENTS
            tables = list(CREATE_STATEMENTS.keys())
            
            # Disable CDC on all tables
            for table in tables:
                enable_cdc.disable_cdc_table(cursor, "dbo", table)
            
            # Disable CDC on database
            enable_cdc.disable_cdc_db(cursor)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Restore original config
            config.CONFIG['mssql_import'] = original_config
            
            st.success(f"✅ CDC disabled successfully on {len(tables)} tables and database!")
            
        except Exception as e:
            st.error(f"❌ Error disabling CDC: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

def show_cdc_simulation_page():
    st.markdown('<div class="main-header">⚡ CDC Simulation</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Simulate Data Changes
    
    This tool simulates real-time data changes (INSERT, UPDATE, DELETE operations) 
    to test Change Data Capture functionality.
    """)
    
    st.markdown("### Database Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        server = st.text_input("Server", value=config.CONFIG['mssql_import']['server'], key="sim_server")
        database = st.text_input("Database", value=config.CONFIG['mssql_import']['database'], key="sim_database")
    
    with col2:
        username = st.text_input("Username", value=config.CONFIG['mssql_import']['username'], key="sim_username")
        password = st.text_input("Password", type="password", value=config.CONFIG['mssql_import']['password'], key="sim_password")
    
    st.markdown("---")
    
    st.markdown("### Simulation Settings")
    
    num_operations = st.number_input(
        "Number of Operations", 
        min_value=1, 
        max_value=1000, 
        value=config.CONFIG['simulator']['default_num_operations'],
        step=5
    )
    
    st.markdown("#### Operation Weights")
    st.info("Configure the probability of each operation type (values between 0.0 and 1.0)")
    
    col1, col2, col3 = st.columns(3)
    
    operation_weights = {}
    operations = [
        'INSERT_CUSTOMER', 'UPDATE_CUSTOMER', 'INSERT_ACCOUNT', 'UPDATE_ACCOUNT',
        'INSERT_TRANSACTION', 'UPDATE_TRANSACTION', 'INSERT_CARD', 'UPDATE_CARD',
        'INSERT_LOAN', 'UPDATE_LOAN', 'INSERT_FRAUD_ALERT', 'INSERT_LOGIN'
    ]
    
    for i, op in enumerate(operations):
        col = [col1, col2, col3][i % 3]
        with col:
            default_weight = config.CONFIG['simulator']['operation_weights'].get(op, 0.08)
            operation_weights[op] = st.slider(
                op.replace('_', ' ').title(),
                0.0, 1.0,
                default_weight,
                0.01,
                format="%.2f"
            )
    
    st.markdown("---")
    
    # Simulate button
    if st.button("⚡ Run Simulation", type="primary", use_container_width=True):
        run_cdc_simulation(server, database, username, password, num_operations, operation_weights)

def run_cdc_simulation(server, database, username, password, num_operations, operation_weights):
    """Run CDC simulation with progress tracking"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Update simulator config
        config.CONFIG['simulator']['default_num_operations'] = num_operations
        config.CONFIG['simulator']['operation_weights'] = operation_weights
        
        simulator = CDCDataSimulator(server, database, username, password)
        
        if not simulator.connect():
            st.error("❌ Failed to connect to database!")
            return
        
        # Create a placeholder for operation logs
        log_placeholder = st.empty()
        operation_logs = []
        
        # Run operations
        success_count = 0
        
        # Prepare weighted operations
        from data_generator_mssql import (
            customer_generator, account_generator, transaction_generator,
            card_generator, loan_generator, fraud_alert_generator, user_login_generator
        )
        
        operations = [
            ('INSERT_CUSTOMER', operation_weights['INSERT_CUSTOMER'], simulator.insert_new_customer),
            ('UPDATE_CUSTOMER', operation_weights['UPDATE_CUSTOMER'], simulator.update_customer_contact),
            ('INSERT_ACCOUNT', operation_weights['INSERT_ACCOUNT'], simulator.insert_new_account),
            ('UPDATE_ACCOUNT', operation_weights['UPDATE_ACCOUNT'], simulator.update_account_balance),
            ('INSERT_TRANSACTION', operation_weights['INSERT_TRANSACTION'], simulator.insert_transaction),
            ('UPDATE_TRANSACTION', operation_weights['UPDATE_TRANSACTION'], simulator.update_transaction_status),
            ('INSERT_CARD', operation_weights['INSERT_CARD'], simulator.insert_card),
            ('UPDATE_CARD', operation_weights['UPDATE_CARD'], simulator.update_card_status),
            ('INSERT_LOAN', operation_weights['INSERT_LOAN'], simulator.insert_loan),
            ('UPDATE_LOAN', operation_weights['UPDATE_LOAN'], simulator.update_loan_status),
            ('INSERT_FRAUD_ALERT', operation_weights['INSERT_FRAUD_ALERT'], simulator.insert_fraud_alert),
            ('INSERT_LOGIN', operation_weights['INSERT_LOGIN'], simulator.insert_user_login),
        ]
        
        import random
        
        for i in range(num_operations):
            status_text.text(f"Running operation {i+1}/{num_operations}...")
            progress_bar.progress((i + 1) / num_operations)
            
            # Weighted random selection
            operation_name, weight, operation_func = random.choices(
                operations, weights=[op[1] for op in operations], k=1
            )[0]
            
            result = operation_func()
            if result:
                success_count += 1
                operation_logs.append(f"✅ [{i+1}] {operation_name}")
            else:
                operation_logs.append(f"❌ [{i+1}] {operation_name}")
            
            # Update log display
            if len(operation_logs) > 20:
                display_logs = operation_logs[-20:]
            else:
                display_logs = operation_logs
            
            log_placeholder.text_area("Operation Log", "\n".join(display_logs), height=200)
        
        simulator.close()
        
        # Success message
        progress_bar.progress(1.0)
        status_text.empty()
        
        st.success(f"✅ Simulation complete! Executed {num_operations} operations ({success_count} successful, {num_operations - success_count} failed)")
        
        # Display operation summary
        st.markdown("### 📊 Operation Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Operations", num_operations)
        
        with col2:
            st.metric("Successful", success_count)
        
        with col3:
            st.metric("Failed", num_operations - success_count)
        
    except Exception as e:
        st.error(f"❌ Error during simulation: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
