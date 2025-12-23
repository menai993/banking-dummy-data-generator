import random
from datetime import datetime, timedelta
from constants.banking_terms import ACCOUNT_TYPES, ACCOUNT_STATUS, CURRENCIES
from utils.helpers import BadDataGenerator

class AccountGenerator:
    def __init__(self, customers_data, bad_data_percentage=0.0):
        self.customers = customers_data
        self.bad_data_percentage = bad_data_percentage
        self.account_ids = set()
        self.accounts = []
        
    def generate_account_number(self, invalid=False):
        """Generate account number"""
        if invalid:
            invalid_numbers = [
                "123",  # Too short
                "1" * 50,  # Too long
                "ABC123XYZ",  # Letters
                "0000000000",  # All zeros
                "",  # Empty
                "123-456-789",  # With dashes
                "NULL"
            ]
            return random.choice(invalid_numbers)
        
        while True:
            account_num = f"{random.randint(1000000000, 9999999999)}"
            if account_num not in [acc.get('account_number') for acc in self.accounts]:
                return account_num
    
    def generate_account_id(self):
        """Generate unique account ID"""
        while True:
            acc_id = f"ACC{random.randint(1000000, 9999999)}"
            if acc_id not in self.account_ids:
                self.account_ids.add(acc_id)
                return acc_id
    
    def generate_balance(self, account_type, invalid=False):
        """Generate balance"""
        if invalid:
            invalid_balances = [
                -10000.00,  # Negative
                9999999999.99,  # Too high
                0.00,  # Zero for non-zero account types
                -0.01,  # Slightly negative
                1000000000.00  # Extremely high
            ]
            return random.choice(invalid_balances)
        
        if account_type == "Savings":
            return round(random.uniform(100, 50000), 2)
        elif account_type == "Checking":
            return round(random.uniform(500, 100000), 2)
        elif account_type == "Money Market":
            return round(random.uniform(1000, 250000), 2)
        else:  # Certificate of Deposit
            return round(random.uniform(5000, 1000000), 2)
    
    def introduce_bad_data_account(self, account):
        """Introduce bad data into account record"""
        bad_data_type = BadDataGenerator.get_bad_data_type()
        
        if bad_data_type == "missing_data":
            fields_to_corrupt = random.sample(["account_number", "balance", "currency", "status"], k=random.randint(1, 3))
            return BadDataGenerator.generate_missing_data(account, fields_to_corrupt)
        
        elif bad_data_type == "invalid_format":
            if random.choice([True, False]):
                account["account_number"] = self.generate_account_number(invalid=True)
            else:
                account["currency"] = "XYZ"  # Invalid currency code
            account["is_bad_data"] = True
            account["bad_data_type"] = "invalid_format"
        
        elif bad_data_type == "out_of_range":
            if random.choice([True, False]):
                account["balance"] = self.generate_balance(account["account_type"], invalid=True)
            else:
                # Account opened in future
                future_date = datetime.now() + timedelta(days=random.randint(1, 365))
                account["opened_date"] = future_date.strftime("%Y-%m-%d")
                account["created_at"] = future_date.strftime("%Y-%m-%d %H:%M:%S")
            account["is_bad_data"] = True
            account["bad_data_type"] = "out_of_range"
        
        elif bad_data_type == "inconsistent_data":
            # Status vs balance inconsistency
            if account["status"] == "Closed" and account["balance"] > 1000:
                account["balance"] = 0.00  # Closed account shouldn't have balance
            account["is_bad_data"] = True
            account["bad_data_type"] = "inconsistent_data"
        
        elif bad_data_type == "malformed_data":
            field = random.choice(["account_type", "status"])
            return BadDataGenerator.generate_malformed_data(account, field)
        
        return account
    
    def generate(self, accounts_per_customer_min=1, accounts_per_customer_max=3):
        """Generate accounts for customers with bad data"""
        self.accounts = []
        bad_account_count = 0
        
        for customer in self.customers:
            num_accounts = random.randint(accounts_per_customer_min, accounts_per_customer_max)
            
            for _ in range(num_accounts):
                account_type = random.choice(ACCOUNT_TYPES)
                created_at = datetime.strptime(customer["created_at"], "%Y-%m-%d %H:%M:%S")
                account_created = created_at + timedelta(days=random.randint(0, 30))
                
                account = {
                    "account_id": self.generate_account_id(),
                    "customer_id": customer["customer_id"],
                    "account_number": self.generate_account_number(),
                    "account_type": account_type,
                    "balance": self.generate_balance(account_type),
                    "currency": random.choice(CURRENCIES),
                    "status": random.choices(ACCOUNT_STATUS, weights=[0.8, 0.05, 0.05, 0.05, 0.05])[0],
                    "opened_date": account_created.strftime("%Y-%m-%d"),
                    "created_at": account_created.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Introduce bad data
                if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
                    account = self.introduce_bad_data_account(account)
                    bad_account_count += 1
                
                self.accounts.append(account)
        
        print(f"Generated {len(self.accounts)} accounts ({bad_account_count} with bad data)")
        return self.accounts