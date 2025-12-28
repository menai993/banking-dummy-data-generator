import pyodbc
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import sys
from config import settings

#!/usr/bin/env python3
"""
Script to generate and execute INSERT, UPDATE, DELETE operations on MSSQL
to simulate real data changes for Change Data Capture (CDC) testing
"""

sys.path.append('.')

from constants import (
    names, addresses, banking_products, login_constants, 
    fraud_constants, investment_products, banking_terms
)
from generators import (
    customer_generator, account_generator, card_generator,
    transaction_generator, loan_generator, fraud_alert_generator,
    user_login_generator
)


class CDCDataSimulator:
    def __init__(self, server: str, database: str, username: str, password: str):
        """Initialize MSSQL connection for CDC simulation"""
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        self.conn = None
        self.cursor = None
        self.operations_log = []
        # Simulator configuration
        sim_cfg = settings.CONFIG.get("simulator", {})
        self.sql_boolean_as_int = sim_cfg.get("sql_boolean_as_int", True)
        self.default_num_operations = sim_cfg.get("default_num_operations", 20)
        self.operation_weights_cfg = sim_cfg.get("operation_weights", {})
        self.stop_on_error = sim_cfg.get("stop_on_error", False)
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            print("✅ Connected to MSSQL database")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_existing_ids(self, table: str, id_column: str) -> List[str]:
        """Fetch existing IDs from table"""
        try:
            query = f"SELECT TOP 100 {id_column} FROM {table}"
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"⚠️  Could not fetch IDs from {table}: {e}")
            return []
    
    def execute_operation(self, operation_type: str, query: str) -> bool:
        """Execute INSERT, UPDATE, or DELETE operation"""
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.operations_log.append({
                'type': operation_type,
                'timestamp': datetime.now(),
                'status': 'SUCCESS'
            })
            return True
        except Exception as e:
            print(f"⚠️  Operation failed: {e}")
            self.operations_log.append({
                'type': operation_type,
                'timestamp': datetime.now(),
                'status': 'FAILED',
                'error': str(e)
            })
            if self.stop_on_error:
                raise
            return False

    # Helpers for SQL formatting based on config
    def _format_bool_sql(self, val):
        if self.sql_boolean_as_int:
            return '1' if val else '0'
        return "'TRUE'" if val else "'FALSE'"

    def _format_nullable(self, val):
        return 'NULL' if val is None else str(val)
    
    def insert_new_customer(self) -> bool:
        """Insert new customer record"""
        customer = customer_generator.generate_customer()
        query = f"""
        INSERT INTO customers 
        (customer_id, first_name, last_name, email, phone, date_of_birth,
         street, city, state, zip_code, country, created_at)
        VALUES ('{customer['customer_id']}', '{customer['first_name']}', 
                '{customer['last_name']}', '{customer['email']}', '{customer['phone']}',
                '{customer['date_of_birth']}', '{customer['street']}', '{customer['city']}',
                '{customer['state']}', '{customer['zip_code']}', '{customer['country']}',
                GETDATE())
        """
        result = self.execute_operation('INSERT_CUSTOMER', query)
        if result:
            print(f"  ➕ Inserted customer: {customer['customer_id']}")
        return result
    
    def update_customer_contact(self) -> bool:
        """Update existing customer contact information"""
        customer_ids = self.get_existing_ids('customers', 'customer_id')
        if not customer_ids:
            return False
        
        customer_id = random.choice(customer_ids)
        new_phone = f"+1{random.randint(2000000000, 9999999999)}"
        new_email = f"{names.FIRST_NAMES[random.randint(0, len(names.FIRST_NAMES)-1)]}.{random.randint(1000, 9999)}@email.com"
        
        query = f"""
        UPDATE customers 
        SET phone = '{new_phone}', email = '{new_email}'
        WHERE customer_id = '{customer_id}'
        """
        result = self.execute_operation('UPDATE_CUSTOMER', query)
        if result:
            print(f"  ✏️  Updated customer contact: {customer_id}")
        return result
    
    def insert_new_account(self) -> bool:
        """Insert new account for existing customer"""
        customer_ids = self.get_existing_ids('customers', 'customer_id')
        if not customer_ids:
            return False
        
        customer_id = random.choice(customer_ids)
        account = account_generator.generate_account(customer_id)
        
        query = f"""
        INSERT INTO accounts 
        (account_id, customer_id, account_number, account_type, balance, 
         currency, status, opened_date, created_at)
        VALUES ('{account['account_id']}', '{customer_id}', '{account['account_number']}',
                '{account['account_type']}', {account['balance']}, '{account['currency']}',
                '{account['status']}', '{account['opened_date']}', GETDATE())
        """
        result = self.execute_operation('INSERT_ACCOUNT', query)
        if result:
            print(f"  ➕ Inserted account: {account['account_id']} for customer: {customer_id}")
        return result
    
    def update_account_balance(self) -> bool:
        """Update account balance (simulate transaction effect)"""
        account_ids = self.get_existing_ids('accounts', 'account_id')
        if not account_ids:
            return False
        
        account_id = random.choice(account_ids)
        amount_change = random.uniform(-5000, 5000)
        
        query = f"""
        UPDATE accounts 
        SET balance = balance + {amount_change}
        WHERE account_id = '{account_id}'
        """
        result = self.execute_operation('UPDATE_ACCOUNT_BALANCE', query)
        if result:
            print(f"  ✏️  Updated account balance: {account_id} (change: {amount_change:.2f})")
        return result
    
    def insert_transaction(self) -> bool:
        """Insert new transaction"""
        account_ids = self.get_existing_ids('accounts', 'account_id')
        if not account_ids:
            return False
        
        account_id = random.choice(account_ids)
        transaction = transaction_generator.generate_transaction(account_id)
        
        query = f"""
        INSERT INTO transactions 
        (transaction_id, account_id, transaction_type, amount, currency,
         transaction_date, transaction_time, description, status, created_at)
        VALUES ('{transaction['transaction_id']}', '{account_id}', 
                '{transaction['transaction_type']}', {transaction['amount']},
                '{transaction['currency']}', '{transaction['transaction_date']}',
                '{transaction['transaction_time']}', '{transaction['description']}',
                '{transaction['status']}', GETDATE())
        """
        result = self.execute_operation('INSERT_TRANSACTION', query)
        if result:
            print(f"  ➕ Inserted transaction: {transaction['transaction_id']}")
        return result
    
    def update_transaction_status(self) -> bool:
        """Update transaction status"""
        self.cursor.execute("SELECT TOP 50 transaction_id FROM transactions")
        transaction_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not transaction_ids:
            return False
        
        transaction_id = random.choice(transaction_ids)
        new_status = random.choice(['COMPLETED', 'PENDING', 'FAILED', 'REVERSED'])
        
        query = f"""
        UPDATE transactions 
        SET status = '{new_status}'
        WHERE transaction_id = '{transaction_id}'
        """
        result = self.execute_operation('UPDATE_TRANSACTION_STATUS', query)
        if result:
            print(f"  ✏️  Updated transaction status: {transaction_id} -> {new_status}")
        return result
    
    def insert_card(self) -> bool:
        """Insert new card for existing account"""
        account_ids = self.get_existing_ids('accounts', 'account_id')
        if not account_ids:
            return False
        
        account_id = random.choice(account_ids)
        self.cursor.execute(f"SELECT customer_id FROM accounts WHERE account_id = '{account_id}'")
        result = self.cursor.fetchone()
        if not result:
            return False
        
        customer_id = result[0]
        card = card_generator.generate_card(customer_id, account_id)
        
        query = f"""
        INSERT INTO cards 
        (card_id, customer_id, account_id, card_number, card_type, card_network,
         expiration_date, cvv, credit_limit, status, created_at)
        VALUES ('{card['card_id']}', '{customer_id}', '{account_id}', '{card['card_number']}',
                '{card['card_type']}', '{card['card_network']}', '{card['expiration_date']}',
                '{card['cvv']}', {card['credit_limit']}, '{card['status']}', GETDATE())
        """
        result = self.execute_operation('INSERT_CARD', query)
        if result:
            print(f"  ➕ Inserted card: {card['card_id']}")
        return result
    
    def update_card_status(self) -> bool:
        """Update card status (activate/deactivate)"""
        card_ids = self.get_existing_ids('cards', 'card_id')
        if not card_ids:
            return False
        
        card_id = random.choice(card_ids)
        new_status = random.choice(['ACTIVE', 'INACTIVE', 'BLOCKED', 'EXPIRED'])
        
        query = f"""
        UPDATE cards 
        SET status = '{new_status}'
        WHERE card_id = '{card_id}'
        """
        result = self.execute_operation('UPDATE_CARD_STATUS', query)
        if result:
            print(f"  ✏️  Updated card status: {card_id} -> {new_status}")
        return result
    
    def insert_loan(self) -> bool:
        """Insert new loan for existing customer and account"""
        customer_ids = self.get_existing_ids('customers', 'customer_id')
        if not customer_ids:
            return False
        
        customer_id = random.choice(customer_ids)
        # Use TOP 1 for compatibility across SQL Server versions
        self.cursor.execute(f"SELECT TOP 1 account_id FROM accounts WHERE customer_id = '{customer_id}'")
        result = self.cursor.fetchone()
        if not result:
            return False
        
        account_id = result[0]
        loan = loan_generator.generate_loan(customer_id, account_id)
        
        query = f"""
        INSERT INTO loans 
        (loan_id, customer_id, account_id, loan_type, loan_amount, interest_rate,
         term_months, start_date, end_date, monthly_payment, remaining_balance,
         status, interest_type, created_at)
        VALUES ('{loan['loan_id']}', '{customer_id}', '{account_id}', '{loan['loan_type']}',
                {loan['loan_amount']}, {loan['interest_rate']}, {loan['term_months']},
                '{loan['start_date']}', '{loan['end_date']}', {loan['monthly_payment']},
                {loan['remaining_balance']}, '{loan['status']}', '{loan['interest_type']}',
                GETDATE())
        """
        result = self.execute_operation('INSERT_LOAN', query)
        if result:
            print(f"  ➕ Inserted loan: {loan['loan_id']}")
        return result
    
    def update_loan_status(self) -> bool:
        """Update loan status"""
        loan_ids = self.get_existing_ids('loans', 'loan_id')
        if not loan_ids:
            return False
        
        loan_id = random.choice(loan_ids)
        new_status = random.choice(['ACTIVE', 'PAID_OFF', 'DEFAULT', 'CLOSED'])
        
        query = f"""
        UPDATE loans 
        SET status = '{new_status}'
        WHERE loan_id = '{loan_id}'
        """
        result = self.execute_operation('UPDATE_LOAN_STATUS', query)
        if result:
            print(f"  ✏️  Updated loan status: {loan_id} -> {new_status}")
        return result
    
    def delete_customer_detail(self) -> bool:
        """Delete customer detail record"""
        self.cursor.execute("SELECT TOP 20 detail_id FROM customer_details")
        detail_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not detail_ids:
            return False
        
        detail_id = random.choice(detail_ids)
        query = f"DELETE FROM customer_details WHERE detail_id = {detail_id}"
        
        result = self.execute_operation('DELETE_CUSTOMER_DETAIL', query)
        if result:
            print(f"  ❌ Deleted customer detail: {detail_id}")
        return result
    
    def insert_fraud_alert(self) -> bool:
        """Insert fraud alert for transaction"""
        self.cursor.execute("SELECT TOP 50 transaction_id, account_id FROM transactions WHERE status = 'COMPLETED'")
        results = self.cursor.fetchall()
        
        if not results:
            return False
        
        transaction_id, account_id = random.choice(results)
        self.cursor.execute(f"SELECT customer_id FROM accounts WHERE account_id = '{account_id}'")
        customer_result = self.cursor.fetchone()
        if not customer_result:
            return False
        
        customer_id = customer_result[0]
        fraud_alert = fraud_alert_generator.generate_fraud_alert(transaction_id, account_id, customer_id)
        
        # Safely format boolean and nullable values for SQL using simulator config
        is_false_positive_val = self._format_bool_sql(fraud_alert.get('is_false_positive'))
        financial_loss_val = self._format_nullable(fraud_alert.get('financial_loss'))

        query = f"""
        INSERT INTO fraud_alerts 
        (alert_id, transaction_id, account_id, customer_id, alert_timestamp,
         detection_method, fraud_reason, fraud_type, severity, severity_score,
         alert_status, financial_loss, is_false_positive, created_at)
        VALUES ({fraud_alert['alert_id']}, '{transaction_id}', '{account_id}', '{customer_id}',
            GETDATE(), '{fraud_alert['detection_method']}', '{fraud_alert['fraud_reason']}',
            '{fraud_alert['fraud_type']}', '{fraud_alert['severity']}',
            {fraud_alert['severity_score']}, '{fraud_alert['alert_status']}',
            {financial_loss_val}, {is_false_positive_val}, GETDATE())
        """
        result = self.execute_operation('INSERT_FRAUD_ALERT', query)
        if result:
            print(f"  ➕ Inserted fraud alert: {fraud_alert['alert_id']}")
        return result
    
    def insert_user_login(self) -> bool:
        """Insert user login record"""
        customer_ids = self.get_existing_ids('customers', 'customer_id')
        if not customer_ids:
            return False
        
        customer_id = random.choice(customer_ids)
        login = user_login_generator.generate_user_login(customer_id)
        
        # Format nullable and boolean fields for SQL using simulator config
        session_minutes_val = self._format_nullable(login.get('session_duration_minutes'))
        is_vpn_val = self._format_bool_sql(login.get('is_vpn_used'))

        query = f"""
        INSERT INTO user_logins 
        (login_id, customer_id, login_timestamp, ip_address, device_type,
         browser, operating_system, login_method, login_status, session_duration_minutes,
         is_vpn_used, created_at)
        VALUES ({login['login_id']}, '{customer_id}', GETDATE(), '{login['ip_address']}',
            '{login['device_type']}', '{login['browser']}', '{login['operating_system']}',
            '{login['login_method']}', '{login['login_status']}',
            {session_minutes_val}, {is_vpn_val}, GETDATE())
        """
        result = self.execute_operation('INSERT_USER_LOGIN', query)
        if result:
            print(f"  ➕ Inserted user login: {login['login_id']}")
        return result
    
    def simulate_cdc_operations(self, num_operations: int = None):
        """Simulate mixed INSERT, UPDATE, DELETE operations"""
        # Build operations list and allow overriding weights from config
        base_operations = [
            ('INSERT_CUSTOMER', self.insert_new_customer),
            ('UPDATE_CUSTOMER', self.update_customer_contact),
            ('INSERT_ACCOUNT', self.insert_new_account),
            ('UPDATE_ACCOUNT', self.update_account_balance),
            ('INSERT_TRANSACTION', self.insert_transaction),
            ('UPDATE_TRANSACTION', self.update_transaction_status),
            ('INSERT_CARD', self.insert_card),
            ('UPDATE_CARD', self.update_card_status),
            ('INSERT_LOAN', self.insert_loan),
            ('UPDATE_LOAN', self.update_loan_status),
            ('INSERT_FRAUD_ALERT', self.insert_fraud_alert),
            ('INSERT_LOGIN', self.insert_user_login),
        ]

        operations = []
        for name, func in base_operations:
            weight = self.operation_weights_cfg.get(name, 0.0)
            operations.append((name, weight, func))

        num_operations = num_operations or self.default_num_operations
        
        print(f"\n{'='*70}")
        print(f"SIMULATING {num_operations} CDC OPERATIONS")
        print(f"{'='*70}\n")
        
        success_count = 0
        for i in range(num_operations):
            # Weighted random selection
            operation_name, weight, operation_func = random.choices(
                operations, weights=[op[1] for op in operations], k=1
            )[0]
            
            print(f"[{i+1}/{num_operations}] {operation_name}...")
            if operation_func():
                success_count += 1
            print()
        
        print(f"\n{'='*70}")
        print(f"OPERATIONS COMPLETE")
        print(f"{'='*70}")
        print(f"Total Executed: {num_operations}")
        print(f"Successful: {success_count}")
        print(f"Failed: {num_operations - success_count}")
        print(f"{'='*70}\n")


def main():
    
    mssql_cfg = settings.CONFIG.get("mssql_import", {})
    if not mssql_cfg:
        print("❌ MSSQL configuration not found in config.py")
        return
    
    simulator = CDCDataSimulator(
        mssql_cfg.get("server"),
        mssql_cfg.get("database"),
        mssql_cfg.get("username"),
        mssql_cfg.get("password")
    )
    
    if not simulator.connect():
        return
    
    try:
        num_ops = int(input("Enter number of operations to simulate (default 20): ") or "20")
        simulator.simulate_cdc_operations(num_ops)
    finally:
        simulator.close()


if __name__ == "__main__":
    main()