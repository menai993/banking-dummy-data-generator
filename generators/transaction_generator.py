import random
from datetime import datetime, timedelta
from constants.banking_terms import TRANSACTION_TYPES, TRANSACTION_STATUS, CURRENCIES
from utils.helpers import BadDataGenerator

class TransactionGenerator:
    def __init__(self, accounts_data, cards_data, bad_data_percentage=0.0):
        self.accounts = accounts_data
        self.cards = cards_data
        self.bad_data_percentage = bad_data_percentage
        self.transaction_ids = set()
        self.transactions = []
        
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        while True:
            trans_id = f"TXN{random.randint(100000000, 999999999)}"
            if trans_id not in self.transaction_ids:
                self.transaction_ids.add(trans_id)
                return trans_id
    
    def generate_amount(self, account_type, transaction_type, invalid=False):
        """Generate transaction amount"""
        if invalid:
            invalid_amounts = [
                -10000.00,  # Negative for non-refund
                99999999.99,  # Too high
                0.00,  # Zero amount
                -0.01,  # Slightly negative
                1000000000.00  # Extremely high
            ]
            return random.choice(invalid_amounts)
        
        if transaction_type in ["Deposit", "Transfer"]:
            base_amount = random.uniform(100, 10000)
        elif transaction_type == "Payment":
            base_amount = random.uniform(50, 5000)
        else:  # Withdrawal, Purchase
            base_amount = random.uniform(10, 1000)
        
        # Adjust based on account type
        if account_type == "Savings":
            base_amount *= random.uniform(0.5, 2)
        elif account_type == "Certificate of Deposit":
            base_amount *= random.uniform(2, 5)
        
        return round(base_amount, 2)
    
    def generate_description(self, transaction_type, invalid=False):
        """Generate transaction description"""
        if invalid:
            invalid_descriptions = [
                "",  # Empty
                "X" * 500,  # Too long
                "NULL",
                "<script>alert(1)</script>",
                "DROP TABLE transactions;",
                "Description with null\x00 character"
            ]
            return random.choice(invalid_descriptions)
        
        descriptions = {
            "Deposit": ["Salary Deposit", "Check Deposit", "Cash Deposit", "ATM Deposit", "Mobile Deposit"],
            "Withdrawal": ["ATM Withdrawal", "Cash Withdrawal", "Bank Withdrawal"],
            "Transfer": ["Transfer to Savings", "Bill Payment", "Money Transfer", "Online Transfer"],
            "Payment": ["Credit Card Payment", "Loan Payment", "Utility Bill", "Mortgage Payment"],
            "Purchase": ["Grocery Store", "Gas Station", "Online Shopping", "Restaurant", "Retail Store"],
            "Refund": ["Purchase Refund", "Service Refund", "Overcharge Refund"]
        }
        
        return random.choice(descriptions.get(transaction_type, ["Transaction"]))
    
    def generate_invalid_date(self):
        """Generate invalid date"""
        invalid_dates = [
            "2025-13-01",  # Invalid month
            "2025-02-30",  # Invalid day
            "0000-00-00",  # All zeros
            "9999-12-31",  # Far future
            "1800-01-01",  # Far past
            "2025/01/01",  # Wrong format
            "01-JAN-2025",  # Wrong format
            ""  # Empty
        ]
        return random.choice(invalid_dates)
    
    def introduce_bad_data_transaction(self, transaction):
        """Introduce bad data into transaction record"""
        bad_data_type = BadDataGenerator.get_bad_data_type()
        
        if bad_data_type == "missing_data":
            fields_to_corrupt = random.sample(["amount", "description", "status", "transaction_date"], k=random.randint(1, 3))
            return BadDataGenerator.generate_missing_data(transaction, fields_to_corrupt)
        
        elif bad_data_type == "invalid_format":
            if random.choice([True, False]):
                transaction["transaction_date"] = self.generate_invalid_date()
            elif random.choice([True, False]):
                transaction["description"] = self.generate_description(transaction["transaction_type"], invalid=True)
            else:
                transaction["currency"] = "XXX"  # Invalid currency
            transaction["is_bad_data"] = True
            transaction["bad_data_type"] = "invalid_format"
        
        elif bad_data_type == "out_of_range":
            if random.choice([True, False]):
                # Future transaction date
                future_date = datetime.now() + timedelta(days=random.randint(1, 365))
                transaction["transaction_date"] = future_date.strftime("%Y-%m-%d")
                transaction["transaction_time"] = future_date.strftime("%H:%M:%S")
            else:
                # Invalid amount
                transaction["amount"] = self.generate_amount(
                    transaction.get("account_type", "Checking"),
                    transaction["transaction_type"],
                    invalid=True
                )
            transaction["is_bad_data"] = True
            transaction["bad_data_type"] = "out_of_range"
        
        elif bad_data_type == "inconsistent_data":
            # Status vs amount inconsistency
            if transaction["status"] == "Failed" and transaction["amount"] > 0:
                # Failed transaction shouldn't have positive amount
                transaction["amount"] = -abs(transaction["amount"])
            transaction["is_bad_data"] = True
            transaction["bad_data_type"] = "inconsistent_data"
        
        elif bad_data_type == "malformed_data":
            field = random.choice(["description", "transaction_type", "status"])
            return BadDataGenerator.generate_malformed_data(transaction, field)
        
        return transaction
    
    def generate(self, transactions_per_account_min=5, transactions_per_account_max=50):
        """Generate transactions for accounts with bad data"""
        self.transactions = []
        bad_transaction_count = 0
        
        for account in self.accounts:
            num_transactions = random.randint(transactions_per_account_min, transactions_per_account_max)
            account_cards = [card for card in self.cards if card.get("account_id") == account["account_id"]]
            
            for i in range(num_transactions):
                # Generate transaction date
                opened_date = datetime.strptime(account["opened_date"], "%Y-%m-%d")
                days_since_opened = (datetime.now() - opened_date).days
                
                if days_since_opened <= 0:
                    continue
                
                transaction_date = opened_date + timedelta(days=random.randint(0, days_since_opened))
                
                # Select transaction type
                if account_cards:
                    transaction_type = random.choices(
                        TRANSACTION_TYPES,
                        weights=[0.15, 0.2, 0.15, 0.2, 0.25, 0.05]
                    )[0]
                else:
                    transaction_type = random.choices(
                        ["Deposit", "Withdrawal", "Transfer", "Payment"],
                        weights=[0.3, 0.3, 0.25, 0.15]
                    )[0]
                
                # Select card (if applicable)
                card_id = None
                if account_cards and transaction_type in ["Purchase", "Refund"]:
                    card = random.choice(account_cards)
                    card_id = card["card_id"]
                
                transaction = {
                    "transaction_id": self.generate_transaction_id(),
                    "account_id": account["account_id"],
                    "card_id": card_id,
                    "transaction_type": transaction_type,
                    "amount": self.generate_amount(account["account_type"], transaction_type),
                    "currency": account["currency"],
                    "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                    "transaction_time": transaction_date.strftime("%H:%M:%S"),
                    "description": self.generate_description(transaction_type),
                    "status": random.choices(TRANSACTION_STATUS, weights=[0.9, 0.05, 0.03, 0.02])[0],
                    "created_at": transaction_date.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Introduce bad data
                if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
                    transaction = self.introduce_bad_data_transaction(transaction)
                    bad_transaction_count += 1
                
                self.transactions.append(transaction)
        
        # Sort transactions by date
        self.transactions.sort(key=lambda x: (x["transaction_date"], x["transaction_time"]))
        
        print(f"Generated {len(self.transactions)} transactions ({bad_transaction_count} with bad data)")
        return self.transactions