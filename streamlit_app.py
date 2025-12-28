#!/usr/bin/env python3
"""
Streamlit Web Interface for Banking Dummy Data Generator
"""

import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime
from generators.customer_generator import CustomerGenerator
from generators.account_generator import AccountGenerator
from generators.card_generator import CardGenerator
from generators.transaction_generator import TransactionGenerator
from generators.branch_generator import BranchGenerator
from generators.employee_generator import EmployeeGenerator
from generators.loan_generator import LoanGenerator
from generators.merchant_generator import MerchantGenerator
from generators.audit_log_generator import AuditLogGenerator
from generators.exchange_rate_generator import ExchangeRateGenerator
from generators.investment_account_generator import InvestmentAccountGenerator
from generators.fraud_alert_generator import FraudAlertGenerator
from generators.user_login_generator import UserLoginGenerator
from utils.helpers import DataExporter
import config

# Page configuration
st.set_page_config(
    page_title="Banking Data Generator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def calculate_statistics(all_data):
    """Calculate statistics about generated data"""
    stats = {}
    total_bad = 0
    total_records = 0
    
    for table_name, data in all_data.items():
        if data:
            bad_count = sum(1 for record in data if record.get('is_bad_data', False))
            total_records += len(data)
            total_bad += bad_count
            
            percentage = (bad_count / len(data) * 100) if len(data) > 0 else 0
            
            # Count by bad data type
            bad_types = {}
            for record in data:
                if record.get('is_bad_data'):
                    bad_type = record.get('bad_data_type', 'unknown')
                    bad_types[bad_type] = bad_types.get(bad_type, 0) + 1
            
            stats[table_name] = {
                'total': len(data),
                'bad_count': bad_count,
                'bad_percentage': percentage,
                'bad_types': bad_types
            }
    
    overall_percentage = (total_bad / total_records * 100) if total_records > 0 else 0
    
    return stats, total_records, total_bad, overall_percentage

def generate_data(generation_config):
    """Generate banking data based on configuration"""
    all_data = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    start_time = time.time()
    
    try:
        # Step 1: Generate Customers
        status_text.text("Step 1/14: Generating customers...")
        progress_bar.progress(1/14)
        customer_gen = CustomerGenerator(
            generation_config["num_customers"],
            generation_config["bad_data_percentage"]["customers"]
        )
        customers, customer_details = customer_gen.generate()
        all_data["customers"] = customers
        all_data["customer_details"] = customer_details
        
        # Step 2: Generate Accounts
        status_text.text("Step 2/14: Generating accounts...")
        progress_bar.progress(2/14)
        account_gen = AccountGenerator(
            customers,
            generation_config["bad_data_percentage"]["accounts"]
        )
        accounts = account_gen.generate(
            generation_config["accounts_per_customer_min"],
            generation_config["accounts_per_customer_max"]
        )
        all_data["accounts"] = accounts
        
        # Step 3: Generate Cards
        status_text.text("Step 3/14: Generating cards...")
        progress_bar.progress(3/14)
        card_gen = CardGenerator(
            customers,
            accounts,
            generation_config["bad_data_percentage"]["cards"]
        )
        cards = card_gen.generate(
            generation_config["cards_per_customer_min"],
            generation_config["cards_per_customer_max"]
        )
        all_data["cards"] = cards
        
        # Step 4: Generate Transactions
        status_text.text("Step 4/14: Generating transactions...")
        progress_bar.progress(4/14)
        transaction_gen = TransactionGenerator(
            accounts,
            cards,
            generation_config["bad_data_percentage"]["transactions"]
        )
        transactions = transaction_gen.generate(
            generation_config["transactions_per_account_min"],
            generation_config["transactions_per_account_max"]
        )
        all_data["transactions"] = transactions
        
        # Step 5: Generate Branches
        status_text.text("Step 5/14: Generating branches...")
        progress_bar.progress(5/14)
        branch_gen = BranchGenerator(
            generation_config["num_branches"],
            generation_config["bad_data_percentage"]["branches"]
        )
        branches = branch_gen.generate()
        all_data["branches"] = branches
        
        # Step 6: Generate Employees
        status_text.text("Step 6/14: Generating employees...")
        progress_bar.progress(6/14)
        employee_gen = EmployeeGenerator(
            branches,
            generation_config["num_employees"],
            generation_config["bad_data_percentage"]["employees"]
        )
        employees = employee_gen.generate()
        all_data["employees"] = employees
        
        # Step 7: Generate Loans
        status_text.text("Step 7/14: Generating loans...")
        progress_bar.progress(7/14)
        loan_gen = LoanGenerator(
            customers,
            accounts,
            generation_config["bad_data_percentage"]["loans"]
        )
        loans, loan_payments = loan_gen.generate(
            generation_config["loans_per_customer_min"],
            generation_config["loans_per_customer_max"]
        )
        all_data["loans"] = loans
        all_data["loan_payments"] = loan_payments
        
        # Step 8: Generate Merchants
        status_text.text("Step 8/14: Generating merchants...")
        progress_bar.progress(8/14)
        merchant_gen = MerchantGenerator(
            generation_config["num_merchants"],
            generation_config["bad_data_percentage"]["merchants"]
        )
        merchants = merchant_gen.generate()
        all_data["merchants"] = merchants
        
        # Step 9: Generate Audit Logs
        status_text.text("Step 9/14: Generating audit logs...")
        progress_bar.progress(9/14)
        all_users = customers + employees
        audit_gen = AuditLogGenerator(
            all_users,
            generation_config["bad_data_percentage"]["audit_logs"]
        )
        audit_logs = audit_gen.generate(
            generation_config["audit_logs_per_user_min"],
            generation_config["audit_logs_per_user_max"]
        )
        all_data["audit_logs"] = audit_logs
        
        # Step 10: Generate Exchange Rates
        status_text.text("Step 10/14: Generating exchange rates...")
        progress_bar.progress(10/14)
        exchange_gen = ExchangeRateGenerator(
            generation_config["exchange_rate_days"],
            generation_config["bad_data_percentage"]["exchange_rates"]
        )
        exchange_rates = exchange_gen.generate()
        all_data["exchange_rates"] = exchange_rates
        
        # Step 11: Generate Investment Accounts
        status_text.text("Step 11/14: Generating investment accounts...")
        progress_bar.progress(11/14)
        investment_gen = InvestmentAccountGenerator(
            generation_config["num_investment_accounts"],
            generation_config["bad_data_percentage"]["investment_accounts"],
            customers,
            accounts
        )
        investment_accounts = investment_gen.generate()
        all_data["investment_accounts"] = investment_accounts
        
        # Step 12: Generate Fraud Alerts
        status_text.text("Step 12/14: Generating fraud alerts...")
        progress_bar.progress(12/14)
        fraud_gen = FraudAlertGenerator(
            generation_config["fraud_alerts_per_transaction"],
            generation_config["bad_data_percentage"]["fraud_alerts"],
            transactions
        )
        fraud_alerts = fraud_gen.generate()
        all_data["fraud_alerts"] = fraud_alerts
        
        # Step 13: Generate User Logins
        status_text.text("Step 13/14: Generating user logins...")
        progress_bar.progress(13/14)
        login_gen = UserLoginGenerator(
            generation_config["user_logins_per_customer_min"],
            generation_config["user_logins_per_customer_max"],
            generation_config["bad_data_percentage"]["user_logins"],
            customers
        )
        user_logins = login_gen.generate()
        all_data["user_logins"] = user_logins
        
        # Step 14: Complete
        status_text.text("Step 14/14: Finalizing...")
        progress_bar.progress(1.0)
        
        elapsed_time = time.time() - start_time
        
        return all_data, elapsed_time, None
        
    except Exception as e:
        return None, 0, str(e)

def export_data(all_data, output_formats, output_dir):
    """Export generated data to specified formats"""
    exporter = DataExporter()
    export_status = {}
    
    try:
        if "csv" in output_formats:
            st.info("Exporting to CSV files...")
            for table_name, data in all_data.items():
                if data:
                    exporter.export_to_csv(data, f"{table_name}.csv", output_dir)
            export_status["csv"] = "✅ Success"
        
        if "sql" in output_formats:
            st.info("Generating SQL files...")
            exporter.export_to_sql_files(all_data, f"{output_dir}/sql")
            export_status["sql"] = "✅ Success"
        
        if "excel" in output_formats:
            st.info("Exporting to Excel...")
            clean_data = {}
            for table_name, data in all_data.items():
                clean_records = []
                for record in data:
                    clean_record = {k: v for k, v in record.items() if k not in ['is_bad_data', 'bad_data_type']}
                    clean_records.append(clean_record)
                clean_data[table_name] = clean_records
            exporter.export_to_excel(clean_data, "banking_data.xlsx", output_dir)
            export_status["excel"] = "✅ Success"
        
        return export_status, None
    except Exception as e:
        return export_status, str(e)

def main():
    # Header
    st.markdown('<div class="main-header">🏦 Banking Dummy Data Generator</div>', unsafe_allow_html=True)
    st.markdown("### Generate realistic banking data with configurable bad data injection")
    
    # Sidebar - Configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Volume Controls
    st.sidebar.subheader("📊 Volume Controls")
    num_customers = st.sidebar.number_input("Number of Customers", min_value=10, max_value=100000, value=1000, step=100)
    num_branches = st.sidebar.number_input("Number of Branches", min_value=1, max_value=1000, value=50, step=10)
    num_employees = st.sidebar.number_input("Number of Employees", min_value=10, max_value=10000, value=200, step=50)
    num_merchants = st.sidebar.number_input("Number of Merchants", min_value=10, max_value=10000, value=500, step=50)
    num_investment_accounts = st.sidebar.number_input("Number of Investment Accounts", min_value=0, max_value=10000, value=300, step=50)
    
    # Relationship Controls
    st.sidebar.subheader("🔗 Relationship Controls")
    accounts_per_customer = st.sidebar.slider("Accounts per Customer", 1, 5, (1, 3))
    cards_per_customer = st.sidebar.slider("Cards per Customer", 0, 5, (0, 2))
    transactions_per_account = st.sidebar.slider("Transactions per Account", 1, 100, (5, 50))
    loans_per_customer = st.sidebar.slider("Loans per Customer", 0, 5, (0, 2))
    
    # Bad Data Configuration
    with st.sidebar.expander("⚠️ Bad Data Configuration", expanded=False):
        st.write("Configure the percentage of bad data for each table:")
        
        bad_data_config = {}
        tables = ["customers", "accounts", "cards", "transactions", "branches", "employees", 
                 "merchants", "loans", "loan_payments", "audit_logs", "exchange_rates",
                 "investment_accounts", "fraud_alerts", "user_logins"]
        
        default_values = config.CONFIG["bad_data_percentage"]
        
        for table in tables:
            default_val = int(default_values.get(table, 0.1) * 100)
            bad_data_config[table] = st.slider(
                f"{table.replace('_', ' ').title()}",
                0, 100, default_val, 1,
                help=f"Percentage of bad data in {table} table"
            ) / 100
    
    # Output Configuration
    st.sidebar.subheader("💾 Output Options")
    output_formats = st.sidebar.multiselect(
        "Export Formats",
        ["csv", "sql", "excel"],
        default=["csv", "sql"]
    )
    output_directory = st.sidebar.text_input("Output Directory", "output")
    
    # Main area
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Customers", f"{num_customers:,}")
    with col2:
        st.metric("Branches", f"{num_branches:,}")
    with col3:
        st.metric("Employees", f"{num_employees:,}")
    
    # Generate button
    st.markdown("---")
    if st.button("🚀 Generate Banking Data", type="primary", use_container_width=True):
        # Prepare configuration
        generation_config = {
            "num_customers": num_customers,
            "num_branches": num_branches,
            "num_employees": num_employees,
            "num_merchants": num_merchants,
            "num_investment_accounts": num_investment_accounts,
            "accounts_per_customer_min": accounts_per_customer[0],
            "accounts_per_customer_max": accounts_per_customer[1],
            "cards_per_customer_min": cards_per_customer[0],
            "cards_per_customer_max": cards_per_customer[1],
            "transactions_per_account_min": transactions_per_account[0],
            "transactions_per_account_max": transactions_per_account[1],
            "loans_per_customer_min": loans_per_customer[0],
            "loans_per_customer_max": loans_per_customer[1],
            "fraud_alerts_per_transaction": 0.05,
            "user_logins_per_customer_min": 8,
            "user_logins_per_customer_max": 30,
            "exchange_rate_days": 365,
            "audit_logs_per_user_min": 5,
            "audit_logs_per_user_max": 50,
            "bad_data_percentage": bad_data_config,
            "output_formats": output_formats,
            "output_directory": output_directory
        }
        
        # Generate data
        with st.spinner("Generating banking data..."):
            all_data, elapsed_time, error = generate_data(generation_config)
        
        if error:
            st.error(f"❌ Error generating data: {error}")
        else:
            st.success(f"✅ Data generation completed in {elapsed_time:.2f} seconds!")
            
            # Calculate and display statistics
            stats, total_records, total_bad, overall_percentage = calculate_statistics(all_data)
            
            # Statistics Dashboard
            st.markdown("---")
            st.subheader("📊 Generation Statistics")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", f"{total_records:,}")
            with col2:
                st.metric("Bad Records", f"{total_bad:,}")
            with col3:
                st.metric("Bad Data %", f"{overall_percentage:.2f}%")
            with col4:
                st.metric("Tables Generated", len(all_data))
            
            # Detailed statistics table
            st.markdown("#### Table-wise Statistics")
            stats_data = []
            for table_name, table_stats in stats.items():
                stats_data.append({
                    "Table": table_name.replace('_', ' ').title(),
                    "Total Records": f"{table_stats['total']:,}",
                    "Bad Records": f"{table_stats['bad_count']:,}",
                    "Bad Data %": f"{table_stats['bad_percentage']:.2f}%"
                })
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Export data
            st.markdown("---")
            st.subheader("💾 Export Data")
            
            with st.spinner("Exporting data..."):
                export_status, export_error = export_data(all_data, output_formats, output_directory)
            
            if export_error:
                st.error(f"❌ Error during export: {export_error}")
            else:
                st.success("✅ Data exported successfully!")
                
                # Display export status
                for format_type, status in export_status.items():
                    st.write(f"{format_type.upper()}: {status}")
                
                st.info(f"📁 Files saved in '{output_directory}' directory")
            
            # Data Preview
            st.markdown("---")
            st.subheader("👀 Data Preview")
            
            selected_table = st.selectbox(
                "Select a table to preview:",
                options=list(all_data.keys()),
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            if selected_table and all_data[selected_table]:
                preview_data = all_data[selected_table][:100]  # Show first 100 records
                df_preview = pd.DataFrame(preview_data)
                
                # Remove internal columns for cleaner display
                display_cols = [col for col in df_preview.columns if col not in ['is_bad_data', 'bad_data_type']]
                
                st.dataframe(df_preview[display_cols], use_container_width=True)
                st.caption(f"Showing first 100 of {len(all_data[selected_table]):,} records")
                
                # Download button for selected table
                csv_data = df_preview[display_cols].to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {selected_table}.csv",
                    data=csv_data,
                    file_name=f"{selected_table}.csv",
                    mime="text/csv"
                )
            
            # Bad Data Analysis
            if total_bad > 0:
                st.markdown("---")
                st.subheader("⚠️ Bad Data Analysis")
                
                bad_types_summary = {}
                for table_name, table_stats in stats.items():
                    for bad_type, count in table_stats['bad_types'].items():
                        bad_types_summary[bad_type] = bad_types_summary.get(bad_type, 0) + count
                
                if bad_types_summary:
                    bad_types_df = pd.DataFrame([
                        {"Bad Data Type": k.replace('_', ' ').title(), "Count": v}
                        for k, v in bad_types_summary.items()
                    ])
                    st.dataframe(bad_types_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Banking Dummy Data Generator | Built with Streamlit</p>
        <p>Generate realistic banking datasets with configurable bad data for testing and analytics</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
