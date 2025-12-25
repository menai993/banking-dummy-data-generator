#!/usr/bin/env python3
"""
Main script to generate dummy banking data with bad data
"""

import time
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

def calculate_statistics(all_data):
    """Calculate and display statistics about bad data"""
    print("\n" + "=" * 60)
    print("BAD DATA STATISTICS")
    print("=" * 60)
    
    total_bad = 0
    total_records = 0
    
    for table_name, data in all_data.items():
        if data:
            bad_count = sum(1 for record in data if record.get('is_bad_data', False))
            total_records += len(data)
            total_bad += bad_count
            
            percentage = (bad_count / len(data) * 100) if len(data) > 0 else 0
            
            print(f"{table_name:20} {len(data):10,} records | {bad_count:6,} bad ({percentage:6.2f}%)")
            
            # Count by bad data type
            bad_types = {}
            for record in data:
                if record.get('is_bad_data'):
                    bad_type = record.get('bad_data_type', 'unknown')
                    bad_types[bad_type] = bad_types.get(bad_type, 0) + 1
            
            if bad_types:
                print(" " * 22 + "Types: ", end="")
                for bad_type, count in bad_types.items():
                    print(f"{bad_type}: {count}", end=", ")
                print()
    
    overall_percentage = (total_bad / total_records * 100) if total_records > 0 else 0
    print("-" * 60)
    print(f"TOTAL{' ':15} {total_records:10,} records | {total_bad:6,} bad ({overall_percentage:6.2f}%)")
    print("=" * 60)

def generate_bad_data_report(all_data, output_dir="output"):
    """Generate a detailed report about bad data"""
    import json
    
    report = {
        "generation_date": datetime.now().isoformat(),
        "configuration": config.CONFIG["bad_data_percentage"],
        "tables": {}
    }
    
    for table_name, data in all_data.items():
        if data:
            bad_records = [record for record in data if record.get('is_bad_data', False)]
            bad_by_type = {}
            
            for record in bad_records:
                bad_type = record.get('bad_data_type', 'unknown')
                bad_by_type[bad_type] = bad_by_type.get(bad_type, 0) + 1
            
            report["tables"][table_name] = {
                "total_records": len(data),
                "bad_records": len(bad_records),
                "bad_percentage": (len(bad_records) / len(data) * 100) if len(data) > 0 else 0,
                "bad_by_type": bad_by_type,
                "examples": bad_records[:5] if bad_records else []  # First 5 examples
            }
    
    report_file = f"{output_dir}/bad_data_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed bad data report saved to: {report_file}")
    return report_file

def main():
    print("=" * 80)
    print("BANKING DUMMY DATA GENERATOR WITH BAD DATA")
    print("=" * 80)
    
    start_time = time.time()
    
    # Get configuration
    bad_data_config = config.CONFIG["bad_data_percentage"]
    
    # Step 1: Generate Customers
    print(f"\n[1/14] Generating customers ({bad_data_config['customers']*100}% bad data)...")
    customer_gen = CustomerGenerator(
        config.CONFIG["num_customers"],
        bad_data_config["customers"]
    )
    customers, customer_details = customer_gen.generate()
    
    # Step 2: Generate Accounts
    print(f"\n[2/14] Generating accounts ({bad_data_config['accounts']*100}% bad data)...")
    account_gen = AccountGenerator(
        customers,
        bad_data_config["accounts"]
    )
    accounts = account_gen.generate(
        config.CONFIG["accounts_per_customer_min"],
        config.CONFIG["accounts_per_customer_max"]
    )
    
    # Step 3: Generate Cards
    print(f"\n[3/14] Generating cards ({bad_data_config['cards']*100}% bad data)...")
    card_gen = CardGenerator(
        customers,
        accounts,
        bad_data_config["cards"]
    )
    cards = card_gen.generate(
        config.CONFIG["cards_per_customer_min"],
        config.CONFIG["cards_per_customer_max"]
    )
    
    # Step 4: Generate Transactions
    print(f"\n[4/14] Generating transactions ({bad_data_config['transactions']*100}% bad data)...")
    transaction_gen = TransactionGenerator(
        accounts,
        cards,
        bad_data_config["transactions"]
    )
    transactions = transaction_gen.generate(
        config.CONFIG["transactions_per_account_min"],
        config.CONFIG["transactions_per_account_max"]
    )
    
    # Step 5: Prepare and Export Data
    print("\n[5/14] Exporting data...")
    
    # Prepare all data
    all_data = {
        "customers": customers,
        "customer_details": customer_details,
        "accounts": accounts,
        "cards": cards,
        "transactions": transactions
    }
    
    # Step 6: Generate Branches
    print(f"\n[6/14] Generating branches ({config.CONFIG['bad_data_percentage']['branches']*100}% bad data)...")
    branch_gen = BranchGenerator(
        config.CONFIG["num_branches"],
        config.CONFIG["bad_data_percentage"]["branches"]
    )
    branches = branch_gen.generate()
    
    # Step 7: Generate Employees
    print(f"\n[7/14] Generating employees ({config.CONFIG['bad_data_percentage']['employees']*100}% bad data)...")
    employee_gen = EmployeeGenerator(
        branches,
        config.CONFIG["num_employees"],
        config.CONFIG["bad_data_percentage"]["employees"]
    )
    employees = employee_gen.generate()
    
    # Step 8: Generate Loans
    print(f"\n[8/14] Generating loans ({config.CONFIG['bad_data_percentage']['loans']*100}% bad data)...")
    loan_gen = LoanGenerator(
        customers,
        accounts,
        config.CONFIG["bad_data_percentage"]["loans"]
    )
    loans, loan_payments = loan_gen.generate(
        config.CONFIG["loans_per_customer_min"],
        config.CONFIG["loans_per_customer_max"]
    )
    
    # Step 9: Generate Merchants
    print(f"\n[9/14] Generating merchants ({config.CONFIG['bad_data_percentage']['merchants']*100}% bad data)...")
    merchant_gen = MerchantGenerator(
        config.CONFIG["num_merchants"],
        config.CONFIG["bad_data_percentage"]["merchants"]
    )
    merchants = merchant_gen.generate()
    
    # Step 10: Generate Audit Logs
    print(f"\n[10/14] Generating audit logs ({config.CONFIG['bad_data_percentage']['audit_logs']*100}% bad data)...")
    # Combine customers and employees for audit logs
    all_users = customers + employees
    audit_gen = AuditLogGenerator(
        all_users,
        config.CONFIG["bad_data_percentage"]["audit_logs"]
    )
    audit_logs = audit_gen.generate(
        config.CONFIG["audit_logs_per_user_min"],
        config.CONFIG["audit_logs_per_user_max"]
    )
    
    # Step 11: Generate Exchange Rates
    print(f"\n[11/14] Generating exchange rates ({config.CONFIG['bad_data_percentage']['exchange_rates']*100}% bad data)...")
    exchange_gen = ExchangeRateGenerator(
        config.CONFIG["exchange_rate_days"],
        config.CONFIG["bad_data_percentage"]["exchange_rates"]
    )
    exchange_rates = exchange_gen.generate()
    

    # Generate investment accounts
    print(f"[12/14] Generating investment accounts ({config.CONFIG['bad_data_percentage']['investment_accounts']*100}% bad data)...")
    investment_gen = InvestmentAccountGenerator(
        config.CONFIG.get("num_investment_accounts"),
        config.CONFIG["bad_data_percentage"]["investment_accounts"],
        customers,
        accounts
    )
    investment_accounts = investment_gen.generate()

    # Generate fraud alerts
    print(f"[13/14] Generating fraud alerts ({config.CONFIG['bad_data_percentage']['fraud_alerts']*100}% bad data)...")
    fraud_gen = FraudAlertGenerator(
        config.CONFIG.get("fraud_alerts_per_transaction", 0.05),
        config.CONFIG["bad_data_percentage"]["fraud_alerts"],
        transactions
    )
    fraud_alerts = fraud_gen.generate()

    # Generate user logins
    print(f"[14/14] Generating user logins ({config.CONFIG['bad_data_percentage']['user_logins']*100}% bad data)...")
    login_gen = UserLoginGenerator(
        config.CONFIG.get("user_logins_per_customer_min", 8),
        config.CONFIG.get("user_logins_per_customer_max", 30),
        config.CONFIG["bad_data_percentage"]["user_logins"],
        customers
    )
    user_logins = login_gen.generate()
    
    # Update all_data dictionary
    all_data.update({
        "branches": branches,
        "employees": employees,
        "loans": loans,
        "loan_payments": loan_payments,
        "merchants": merchants,
        "audit_logs": audit_logs,
        "exchange_rates": exchange_rates,
        "investment_accounts": investment_accounts,  # [NEW]
        "fraud_alerts": fraud_alerts,                # [NEW]
        "user_logins": user_logins                   # [NEW]
    })

    
    exporter = DataExporter()
    
    # Export based on configured formats
    if "csv" in config.CONFIG["output_formats"]:
        print("\nExporting to CSV files...")
        for table_name, data in all_data.items():
            if data:
                exporter.export_to_csv(data, f"{table_name}.csv")
    
    if "sql" in config.CONFIG["output_formats"]:
        print("\nGenerating SQL files...")
        exporter.export_to_sql_files(all_data)

    if "excel" in config.CONFIG["output_formats"]:
        print("\nExporting to Excel...")
        
        # Remove bad data indicators for Excel export (cleaner view)
        clean_data = {}
        for table_name, data in all_data.items():
            clean_records = []
            for record in data:
                clean_record = {k: v for k, v in record.items() if k not in ['is_bad_data', 'bad_data_type']}
                clean_records.append(clean_record)
            clean_data[table_name] = clean_records
        
        exporter.export_to_excel(clean_data)
    
    # Generate statistics and reports
    calculate_statistics(all_data)
    generate_bad_data_report(all_data)
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("DATA GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total execution time: {elapsed_time:.2f} seconds")
    
    # Configuration summary
    print(f"\nBad Data Configuration:")
    for table, percentage in bad_data_config.items():
        print(f"  {table:20} {percentage*100:5.1f}%")
    
    print(f"\nOutput saved in '{config.CONFIG['output_directory']}' directory")
    print("=" * 80)

if __name__ == "__main__":
    main()