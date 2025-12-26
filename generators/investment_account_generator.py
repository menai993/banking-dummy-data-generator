# generators/investment_account_generator.py
import random
from datetime import datetime, timedelta
from utils.helpers import BadDataGenerator
from constants.investment_products import (
    INVESTMENT_TYPES, RISK_TOLERANCE, ACCOUNT_STATUSES,
    INVESTMENT_STRATEGIES, ASSET_CLASSES
)

class InvestmentAccountGenerator:
    def __init__(self, num_accounts=None, bad_data_percentage=0.0, customers=None, accounts=None):
        self.num_accounts = num_accounts
        self.bad_data_percentage = bad_data_percentage
        self.customers = customers or []
        self.accounts = accounts or []
        self.investment_accounts = []
        
    def introduce_bad_data_investment(self, account):
        """Introduce bad data into investment account"""
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["investment_type", "risk_tolerance", "management_fee_rate"]
                return BadDataGenerator.generate_missing_data(account, fields)
            
            elif bad_data_type == "out_of_range":
                account["current_balance"] = -1000000  # Negative balance
                account["annual_return_rate"] = 5.5  # > 5.0
                account["is_bad_data"] = True
                account["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Risk tolerance doesn't match investment type
                account["risk_tolerance"] = "LOW"
                account["investment_type"] = "AGGRESSIVE_PORTFOLIO"
                account["is_bad_data"] = True
                account["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                account["investment_type"] = "INVALID_TYPE_XYZ"
                account["risk_tolerance"] = "EXTREME"
                account["is_bad_data"] = True
                account["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "malformed_data":
                account["account_status"] = "<script>alert('xss')</script>"
                account["is_bad_data"] = True
                account["bad_data_type"] = "malformed_data"
        
        return account
    
    def generate(self):
        """Generate investment accounts"""
        self.investment_accounts = []
        bad_account_count = 0
        
        # Determine how many accounts to create
        if not self.num_accounts:
            # Default: create for 30% of customers who have accounts
            customers_with_accounts = [c for c in self.customers if any(
                a['customer_id'] == c['customer_id'] for a in self.accounts
            )]
            num_accounts = int(len(customers_with_accounts) * 0.3)
        else:
            num_accounts = self.num_accounts
        
        # Get accounts that can have investment sub-accounts
        eligible_accounts = [a for a in self.accounts if a.get('account_type') in ['SAVINGS', 'CHECKING']]
        
        if not eligible_accounts:
            eligible_accounts = self.accounts[:min(50, len(self.accounts))]
        
        next_account_id = 1
        
        for _ in range(num_accounts):
            # Pick a random customer with accounts
            if not self.customers:
                customer_id = random.randint(1, 1000)
            else:
                customer = random.choice(self.customers)
                customer_id = customer['customer_id']
            
            # Link to an existing account
            if eligible_accounts:
                base_account = random.choice(eligible_accounts)
                account_id = base_account.get('account_id', random.randint(1, 1000))
            else:
                account_id = random.randint(1, 1000)
            
            # Create investment account
            opening_date = datetime.now() - timedelta(days=random.randint(30, 365*5))
            current_balance = round(random.uniform(1000, 500000), 2)
            
            account = {
                "investment_account_id": next_account_id,
                "customer_id": customer_id,
                "account_id": account_id,
                "investment_type": random.choice(INVESTMENT_TYPES),
                "risk_tolerance": random.choice(RISK_TOLERANCE),
                "account_status": random.choice(ACCOUNT_STATUSES),
                "investment_strategy": random.choice(INVESTMENT_STRATEGIES),
                "primary_asset_class": random.choice(ASSET_CLASSES),
                "opening_date": opening_date.strftime("%Y-%m-%d"),
                "current_balance": current_balance,
                "total_deposits": round(current_balance * random.uniform(0.7, 1.3), 2),
                "ytd_return_rate": round(random.uniform(-0.15, 0.25), 4),
                "annual_return_rate": round(random.uniform(-0.15, 0.25), 4),
                "management_fee_rate": round(random.uniform(0.001, 0.025), 4),
                "total_value": round(current_balance * (1 + random.uniform(-0.1, 0.1)), 2),
                "is_managed_account": random.choice([True, False]),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Introduce bad data
            account = self.introduce_bad_data_investment(account)
            if account.get('is_bad_data'):
                bad_account_count += 1
            
            self.investment_accounts.append(account)
            next_account_id += 1
        
        print(f"Generated {len(self.investment_accounts)} investment accounts ({bad_account_count} with bad data)")
        return self.investment_accounts