import random
from datetime import datetime, timedelta
from constants.banking_products import LOAN_TYPES, LOAN_STATUS, LOAN_TERMS, INTEREST_TYPES
from utils.helpers import BadDataGenerator

class LoanGenerator:
    def __init__(self, customers_data, accounts_data, bad_data_percentage=0.0):
        self.customers = customers_data
        self.accounts = accounts_data
        self.bad_data_percentage = bad_data_percentage
        self.loan_ids = set()
        self.loans = []
        self.loan_payments = []
        
    def generate_loan_id(self):
        """Generate unique loan ID"""
        while True:
            loan_id = f"LN{random.randint(1000000, 9999999)}"
            if loan_id not in self.loan_ids:
                self.loan_ids.add(loan_id)
                return loan_id
    
    @staticmethod
    def generate_loan_amount(loan_type):
        """Generate loan amount based on type"""
        if loan_type == "Personal Loan":
            return round(random.uniform(1000, 50000), 2)
        elif loan_type == "Auto Loan":
            return round(random.uniform(5000, 100000), 2)
        elif loan_type == "Home Loan":
            return round(random.uniform(100000, 1000000), 2)
        elif loan_type == "Mortgage":
            return round(random.uniform(150000, 2000000), 2)
        else:
            return round(random.uniform(5000, 250000), 2)
    
    @staticmethod
    def generate_interest_rate(loan_type, credit_score):
        """Generate interest rate based on loan type and credit score"""
        base_rate = 0.05  # 5%
        
        # Adjust based on credit score
        if credit_score >= 750:
            base_rate -= 0.02
        elif credit_score >= 700:
            base_rate -= 0.015
        elif credit_score >= 650:
            base_rate -= 0.01
        elif credit_score >= 600:
            base_rate -= 0.005
        
        # Adjust based on loan type
        if loan_type in ["Home Loan", "Mortgage"]:
            base_rate += 0.01
        elif loan_type == "Personal Loan":
            base_rate += 0.03
        
        # Add random variation
        base_rate += random.uniform(-0.005, 0.005)
        
        return round(max(0.02, base_rate), 4)  # Minimum 2%
    
    @staticmethod
    def calculate_monthly_payment(principal, annual_rate, months):
        """Calculate monthly payment using amortization formula with error handling"""
        try:
            # Convert to float if needed
            principal = float(principal)
            annual_rate = float(annual_rate)
            months = int(months)
            
            # Handle edge cases
            if months <= 0:
                months = 12
            if principal <= 0:
                return 0.00
            if annual_rate <= 0:
                return round(principal / months, 2)
            
            monthly_rate = annual_rate / 12
            
            # Handle negative or extreme rates
            if monthly_rate <= -1:  # Avoid division by zero
                monthly_rate = -0.99
            
            payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
            return round(payment, 2)
        except (ValueError, TypeError, ZeroDivisionError):
            # Fallback to simple calculation
            return round(float(principal) / max(1, int(months)), 2)
    
    def generate_loan_schedule(self, loan):
        """Generate loan payment schedule with robust error handling"""
        payments = []
        
        # SAFELY extract and convert values with error handling
        try:
            principal = float(loan["loan_amount"])
        except (ValueError, TypeError):
            principal = 10000.0  # Default if invalid
        
        try:
            interest_rate = float(loan["interest_rate"])
        except (ValueError, TypeError):
            interest_rate = 0.05  # Default 5% if invalid
        
        try:
            term_months = int(loan["term_months"])
        except (ValueError, TypeError):
            term_months = 12  # Default 12 months if invalid
        
        # Ensure term_months is positive
        if term_months <= 0:
            term_months = 12
        
        # Get or calculate monthly payment
        monthly_payment = loan.get("monthly_payment")
        if monthly_payment is None:
            try:
                monthly_payment = self.calculate_monthly_payment(principal, interest_rate, term_months)
            except:
                monthly_payment = round(principal / term_months, 2)  # Simple division as fallback
        
        # Calculate monthly rate
        monthly_rate = interest_rate / 12
        
        # Handle start date
        try:
            payment_date = datetime.strptime(loan["start_date"], "%Y-%m-%d")
        except (ValueError, KeyError):
            # Default to current date if invalid
            payment_date = datetime.now()
        
        remaining_balance = principal
        
        for payment_num in range(1, term_months + 1):
            try:
                interest_amount = round(remaining_balance * monthly_rate, 2)
                principal_amount = round(min(monthly_payment - interest_amount, remaining_balance), 2)
                
                # Adjust last payment
                if payment_num == term_months:
                    principal_amount = round(remaining_balance, 2)
                    monthly_payment = principal_amount + interest_amount
                
                remaining_balance = round(max(0, remaining_balance - principal_amount), 2)
            except:
                # If calculation fails, use simple values
                interest_amount = 0.00
                principal_amount = round(monthly_payment, 2)
                remaining_balance = max(0, remaining_balance - principal_amount)
            
            payment = {
                "payment_id": f"PAY{loan.get('loan_id', 'LN0000000')[2:]}{payment_num:03d}{loan.get('customer_id', 'UNKNOWN')[1:]}",
                "loan_id": loan.get("loan_id", "UNKNOWN"),
                "customer_id": loan.get("customer_id", "UNKNOWN"),
                "payment_number": payment_num,
                "payment_date": payment_date.strftime("%Y-%m-%d"),
                "due_date": payment_date.strftime("%Y-%m-%d"),
                "amount_due": round(monthly_payment, 2),
                "principal_amount": principal_amount,
                "interest_amount": interest_amount,
                "total_paid": 0.00,
                "status": "Pending",
                "created_at": payment_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            payments.append(payment)
            payment_date += timedelta(days=30)  # Approximate month
            
        return payments
    
    def introduce_bad_data_loan(self, loan):
        """Introduce bad data into loan record"""
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["interest_rate", "term_months", "monthly_payment", "loan_type"]
                fields_to_corrupt = random.sample(fields, min(2, len(fields)))
                for field in fields_to_corrupt:
                    if field in loan:
                        loan[field] = None
                loan["is_bad_data"] = True
                loan["bad_data_type"] = "missing_data"
            
            elif bad_data_type == "out_of_range":
                loan["interest_rate"] = random.uniform(-0.1, -0.01)  # Negative interest
                loan["is_bad_data"] = True
                loan["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Loan amount vs monthly payment inconsistency
                if "monthly_payment" in loan and "loan_amount" in loan:
                    if loan["monthly_payment"] > loan["loan_amount"]:
                        loan["monthly_payment"] = loan["loan_amount"] * 0.01  # Too small
                loan["is_bad_data"] = True
                loan["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                # Keep value SQL-insertable (DECIMAL) while still marking as invalid.
                # Using an unrealistic interest rate avoids conversion failures during MSSQL import.
                loan["interest_rate"] = 999.9999
                loan["is_bad_data"] = True
                loan["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "malformed_data":
                field = random.choice(["loan_type", "status"])
                if field in loan and loan[field] is not None:
                    sql_injection_patterns = [
                        "' OR '1'='1",
                        "'; DROP TABLE loans; --",
                        "<script>alert('xss')</script>"
                    ]
                    pattern = random.choice(sql_injection_patterns)
                    loan[field] = f"{loan[field]}{pattern}"
                loan["is_bad_data"] = True
                loan["bad_data_type"] = "malformed_data"
        
        return loan
    
    def introduce_bad_data_payment(self, payment):
        """Introduce bad data into payment record"""
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage * 0.5):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["amount_due", "principal_amount", "interest_amount"]
                fields_to_corrupt = random.sample(fields, min(2, len(fields)))
                for field in fields_to_corrupt:
                    if field in payment:
                        payment[field] = None
                payment["is_bad_data"] = True
                payment["bad_data_type"] = "missing_data"
            
            elif bad_data_type == "out_of_range":
                if "amount_due" in payment:
                    payment["total_paid"] = payment["amount_due"] * 2  # Overpayment
                payment["is_bad_data"] = True
                payment["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Payment made before due date but status is late
                payment["status"] = "Late"
                payment["is_bad_data"] = True
                payment["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                # Keep value SQL-insertable (DATE) while still marking as invalid.
                # Use a far-future date rather than an unparsable date string.
                if "payment_date" in payment:
                    payment["payment_date"] = "9999-12-31"
                payment["is_bad_data"] = True
                payment["bad_data_type"] = "invalid_format"
        
        return payment
    
    def generate(self, loans_per_customer_min=0, loans_per_customer_max=2):
        """Generate loans and payment schedules"""
        self.loans = []
        self.loan_payments = []
        bad_loan_count = 0
        
        for customer in self.customers:
            num_loans = random.randint(loans_per_customer_min, loans_per_customer_max)
            customer_accounts = [acc for acc in self.accounts if acc["customer_id"] == customer["customer_id"]]
            
            if not customer_accounts or num_loans == 0:
                continue
            
            for _ in range(num_loans):
                account = random.choice(customer_accounts)
                loan_type = random.choice(LOAN_TYPES)
                credit_score = random.randint(600, 850)  # In real scenario, get from customer_details
                
                loan_amount = self.generate_loan_amount(loan_type)
                term_months = random.choice(LOAN_TERMS)
                interest_rate = self.generate_interest_rate(loan_type, credit_score)
                monthly_payment = self.calculate_monthly_payment(loan_amount, interest_rate, term_months)
                
                start_date = (datetime.now() - timedelta(days=random.randint(0, 365*5))).strftime("%Y-%m-%d")
                
                loan = {
                    "loan_id": self.generate_loan_id(),
                    "customer_id": customer["customer_id"],
                    "account_id": account["account_id"],
                    "loan_type": loan_type,
                    "loan_amount": loan_amount,
                    "interest_rate": interest_rate,
                    "term_months": term_months,
                    "start_date": start_date,
                    "end_date": (datetime.strptime(start_date, "%Y-%m-%d") + 
                                timedelta(days=term_months*30)).strftime("%Y-%m-%d"),
                    "monthly_payment": monthly_payment,
                    "remaining_balance": loan_amount,
                    "status": random.choices(LOAN_STATUS, weights=[0.6, 0.2, 0.05, 0.1, 0.04, 0.01])[0],
                    "interest_type": random.choice(INTEREST_TYPES),
                    "created_at": start_date + " 00:00:00"
                }
                
                # Introduce bad data
                loan = self.introduce_bad_data_loan(loan)
                if loan.get('is_bad_data'):
                    bad_loan_count += 1
                
                self.loans.append(loan)
                
                # Generate payment schedule (skip if loan is too bad)
                try:
                    if loan.get("loan_amount") and loan.get("interest_rate") and loan.get("term_months"):
                        payments = self.generate_loan_schedule(loan)
                        
                        # Mark some payments as paid, late, or missed
                        for payment in payments:
                            # Randomly update payment status
                            rand = random.random()
                            if rand < 0.7:  # 70% paid on time
                                payment["total_paid"] = payment["amount_due"]
                                payment["status"] = "Paid"
                            elif rand < 0.85:  # 15% late
                                payment["total_paid"] = payment["amount_due"] * random.uniform(0.5, 0.95)
                                payment["status"] = "Late"
                            elif rand < 0.95:  # 10% missed
                                payment["total_paid"] = 0.00
                                payment["status"] = "Missed"
                            else:  # 5% partially paid
                                payment["total_paid"] = payment["amount_due"] * random.uniform(0.1, 0.5)
                                payment["status"] = "Partial"
                            
                            # Introduce bad data in payments
                            payment = self.introduce_bad_data_payment(payment)
                            
                            self.loan_payments.append(payment)
                except Exception as e:
                    print(f"Warning: Could not generate schedule for loan {loan.get('loan_id', 'UNKNOWN')}: {e}")
                    continue
        
        print(f"Generated {len(self.loans)} loans ({bad_loan_count} with bad data)")
        print(f"Generated {len(self.loan_payments)} loan payments")
        
        return self.loans, self.loan_payments


def generate_loan(customer_id: str, account_id: str):
    """Compatibility shim: generate a single loan for given customer and account."""
    customer = {"customer_id": customer_id, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    account = {"account_id": account_id, "customer_id": customer_id, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    gen = LoanGenerator([customer], [account])
    loans, _ = gen.generate(1, 1)
    return loans[0] if loans else None