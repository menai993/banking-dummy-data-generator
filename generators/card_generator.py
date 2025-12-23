import random
from datetime import datetime, timedelta
from constants.banking_terms import CARD_TYPES, CARD_NETWORKS
from utils.helpers import BadDataGenerator

class CardGenerator:
    def __init__(self, customers_data, accounts_data, bad_data_percentage=0.0):
        self.customers = customers_data
        self.accounts = accounts_data
        self.bad_data_percentage = bad_data_percentage
        self.card_ids = set()
        self.cards = []
        
    def generate_card_number(self, network, invalid=False):
        """Generate card number"""
        if invalid:
            invalid_numbers = [
                "1234567890123456",  # Not Luhn valid
                "1111-2222-3333-4444",  # With dashes
                "abcd-efgh-ijkl-mnop",  # Letters
                "1" * 19,  # Wrong length
                "0000000000000000",  # All zeros
                "",  # Empty
                "NULL"
            ]
            return random.choice(invalid_numbers)
        
        # Generate valid card number with Luhn algorithm
        if network == "American Express":
            prefix = "3" + str(random.choice([4, 7]))
            length = 15
        else:
            prefix = str(random.choice([4, 5]))
            length = 16
        
        number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(length - len(prefix) - 1)])
        
        # Calculate check digit using Luhn algorithm
        digits = [int(d) for d in number]
        for i in range(len(digits)-1, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        total = sum(digits)
        check_digit = (10 - (total % 10)) % 10
        number += str(check_digit)
        
        return number
    
    def generate_card_id(self):
        """Generate unique card ID"""
        while True:
            card_id = f"CRD{random.randint(1000000, 9999999)}"
            if card_id not in self.card_ids:
                self.card_ids.add(card_id)
                return card_id
    
    def generate_expiry_date(self, expired=False):
        """Generate expiry date"""
        if expired:
            # Generate past date
            past_date = datetime.now() - timedelta(days=random.randint(1, 365*3))
            return past_date.strftime("%m/%y")
        else:
            # Generate future date (1-5 years from now)
            expiry_date = datetime.now() + timedelta(days=random.randint(365, 365*5))
            return expiry_date.strftime("%m/%y")
    
    def generate_invalid_expiry_date(self):
        """Generate invalid expiry date"""
        invalid_dates = [
            "13/25",  # Invalid month
            "00/23",  # Zero month
            "AA/BB",  # Letters
            "05/2025",  # Wrong format
            "05-25",  # Wrong separator
            "",  # Empty
            "99/99"  # Invalid
        ]
        return random.choice(invalid_dates)
    
    def generate_cvv(self, invalid=False):
        """Generate CVV"""
        if invalid:
            invalid_cvvs = [
                "12",  # Too short
                "12345",  # Too long
                "abc",  # Letters
                "000",  # All zeros
                "",  # Empty
                "NULL"
            ]
            return random.choice(invalid_cvvs)
        return f"{random.randint(100, 999)}"
    
    def generate_credit_limit(self, card_type, credit_score, invalid=False):
        """Generate credit limit"""
        if invalid:
            invalid_limits = [
                -5000.00,  # Negative
                99999999.99,  # Too high
                0.00,  # Zero for credit cards
                -0.01,  # Slightly negative
                100000000.00  # Extremely high
            ]
            return random.choice(invalid_limits)
        
        if card_type != "Credit":
            return 0
        
        base_limit = 1000
        if credit_score >= 800:
            base_limit = 25000
        elif credit_score >= 750:
            base_limit = 15000
        elif credit_score >= 700:
            base_limit = 10000
        elif credit_score >= 650:
            base_limit = 5000
        elif credit_score >= 600:
            base_limit = 2000
        
        return round(base_limit * random.uniform(0.8, 1.2), 2)
    
    def introduce_bad_data_card(self, card):
        """Introduce bad data into card record"""
        bad_data_type = BadDataGenerator.get_bad_data_type()
        
        if bad_data_type == "missing_data":
            fields_to_corrupt = random.sample(["card_number", "expiration_date", "cvv", "credit_limit"], k=random.randint(1, 3))
            return BadDataGenerator.generate_missing_data(card, fields_to_corrupt)
        
        elif bad_data_type == "invalid_format":
            if random.choice([True, False]):
                card["card_number"] = self.generate_card_number(card["card_network"], invalid=True)
            elif random.choice([True, False]):
                card["expiration_date"] = self.generate_invalid_expiry_date()
            else:
                card["cvv"] = self.generate_cvv(invalid=True)
            card["is_bad_data"] = True
            card["bad_data_type"] = "invalid_format"
        
        elif bad_data_type == "out_of_range":
            if random.choice([True, False]):
                # Expired card
                card["expiration_date"] = self.generate_expiry_date(expired=True)
            else:
                # Invalid credit limit
                card["credit_limit"] = self.generate_credit_limit(card["card_type"], 700, invalid=True)
            card["is_bad_data"] = True
            card["bad_data_type"] = "out_of_range"
        
        elif bad_data_type == "inconsistent_data":
            # Card type vs network inconsistency
            if card["card_type"] == "Credit" and card["card_network"] == "Visa":
                card["card_network"] = "InvalidNetwork"  # Should be Visa/MasterCard/Amex
            card["is_bad_data"] = True
            card["bad_data_type"] = "inconsistent_data"
        
        elif bad_data_type == "malformed_data":
            field = random.choice(["card_type", "card_network", "status"])
            return BadDataGenerator.generate_malformed_data(card, field)
        
        return card
    
    def generate(self, cards_per_customer_min=0, cards_per_customer_max=2):
        """Generate cards for customers with bad data"""
        self.cards = []
        bad_card_count = 0
        
        for customer in self.customers:
            num_cards = random.randint(cards_per_customer_min, cards_per_customer_max)
            customer_accounts = [acc for acc in self.accounts if acc["customer_id"] == customer["customer_id"]]
            
            if not customer_accounts:
                continue
            
            for _ in range(num_cards):
                account = random.choice(customer_accounts)
                card_type = random.choice(CARD_TYPES)
                network = random.choice(CARD_NETWORKS)
                created_at = datetime.strptime(account["created_at"], "%Y-%m-%d %H:%M:%S")
                card_created = created_at + timedelta(days=random.randint(0, 60))
                
                # Generate credit score
                credit_score = random.randint(600, 850)
                
                card = {
                    "card_id": self.generate_card_id(),
                    "customer_id": customer["customer_id"],
                    "account_id": account["account_id"],
                    "card_number": self.generate_card_number(network),
                    "card_type": card_type,
                    "card_network": network,
                    "expiration_date": self.generate_expiry_date(),
                    "cvv": self.generate_cvv(),
                    "credit_limit": self.generate_credit_limit(card_type, credit_score),
                    "status": random.choices(["Active", "Inactive", "Blocked", "Expired"], weights=[0.85, 0.05, 0.05, 0.05])[0],
                    "created_at": card_created.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Introduce bad data
                if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
                    card = self.introduce_bad_data_card(card)
                    bad_card_count += 1
                
                self.cards.append(card)
        
        print(f"Generated {len(self.cards)} cards ({bad_card_count} with bad data)")
        return self.cards