import random
from datetime import datetime, timedelta
from constants.banking_terms import TRANSACTION_TYPES, TRANSACTION_STATUS
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
    
    @staticmethod
    def generate_amount(account_type, transaction_type, invalid=False):
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
    
    @staticmethod
    def generate_description(transaction_type, invalid=False):
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
    
    @staticmethod
    def generate_invalid_date():
        """Generate invalid date"""
        invalid_dates = [
            "9999-12-31",  # Far future
            "1800-01-01",  # Far past
            ""  # Empty
        ]
        return random.choice(invalid_dates)
    
    def introduce_bad_data_transaction(self, transaction):
        """Introduce bad data into transaction record"""
        bad_data_type = BadDataGenerator.get_bad_data_type()
        
        if bad_data_type == "missing_data":
            fields_to_corrupt = random.sample(["amount", "description", "status", "transaction_date", "transaction_time"], k=random.randint(1, 3))
            for field in fields_to_corrupt:
                if field in transaction:
                    transaction[field] = None
            transaction['is_bad_data'] = True
            transaction['bad_data_type'] = 'missing_data'
        
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
                    "Checking",  # Default account type
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
            if field in transaction and transaction[field] is not None:
                sql_injection_patterns = [
                    "' OR '1'='1",
                    "'; DROP TABLE transactions; --",
                    "<script>alert('xss')</script>",
                    "../../../etc/passwd",
                    "null\x00"
                ]
                pattern = random.choice(sql_injection_patterns)
                transaction[field] = f"{transaction[field]}{pattern}"
            transaction["is_bad_data"] = True
            transaction["bad_data_type"] = "malformed_data"
        
        return transaction
    
    @staticmethod
    def _safe_sort_key(transaction):
        """Safe sorting key that handles None values"""
        date = transaction.get("transaction_date")
        time = transaction.get("transaction_time")
        
        # Handle None values by putting them at the end
        if date is None:
            date = "9999-12-31"  # Far future date
        if time is None:
            time = "23:59:59"    # End of day
        
        return (date, time)
    
    def generate(self, transactions_per_account_min=5, transactions_per_account_max=50):
        """Generate transactions for accounts with bad data"""
        self.transactions = []
        bad_transaction_count = 0
        
        for account in self.accounts:
            # Skip if account has invalid opened_date
            try:
                opened_date = datetime.strptime(account["opened_date"], "%Y-%m-%d")
                days_since_opened = (datetime.now() - opened_date).days
                
                if days_since_opened <= 0:
                    continue
            except (ValueError, KeyError):
                # Invalid date format or missing field
                continue
            
            num_transactions = random.randint(transactions_per_account_min, transactions_per_account_max)
            account_cards = [card for card in self.cards if card.get("account_id") == account["account_id"]]
            
            for i in range(num_transactions):
                # Generate transaction date within account lifespan
                days_offset = random.randint(0, days_since_opened)
                transaction_date = opened_date + timedelta(days=days_offset)
                
                transaction_date_str = transaction_date.strftime("%Y-%m-%d")
                transaction_time_str = transaction_date.strftime("%H:%M:%S")
                
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
                    "amount": self.generate_amount(account.get("account_type", "Checking"), transaction_type),
                    "currency": account.get("currency", "USD"),
                    "transaction_date": transaction_date_str,
                    "transaction_time": transaction_time_str,
                    "description": self.generate_description(transaction_type),
                    "status": random.choices(TRANSACTION_STATUS, weights=[0.9, 0.05, 0.03, 0.02])[0],
                    "created_at": f"{transaction_date_str} {transaction_time_str}"
                }
                
                # Introduce bad data
                if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
                    transaction = self.introduce_bad_data_transaction(transaction)
                    bad_transaction_count += 1
                
                self.transactions.append(transaction)
        
        # Sort transactions by date and time, safely handling None values
        self.transactions.sort(key=self._safe_sort_key)
        
        print(f"Generated {len(self.transactions)} transactions ({bad_transaction_count} with bad data)")
        return self.transactions


def generate_transaction(account_id: str):
    """Compatibility shim: generate a single transaction for an account_id."""
    account = {
        "account_id": account_id,
        "account_type": "Checking",
        "currency": "USD",
        "opened_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    gen = TransactionGenerator([account], [])
    transactions = gen.generate(1, 1)
    return transactions[0] if transactions else None