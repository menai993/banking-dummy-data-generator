import random
from datetime import datetime, timedelta
from constants.names import FIRST_NAMES, LAST_NAMES
from constants.addresses import STREET_NAMES, STREET_TYPES, CITIES, STATES, ZIP_CODES, COUNTRIES
from constants.banking_terms import EMPLOYMENT_TYPES, EDUCATION_LEVELS, MARITAL_STATUSES
from utils.helpers import BadDataGenerator

class CustomerGenerator:
    def __init__(self, num_customers=1000, bad_data_percentage=0.0):
        self.num_customers = num_customers
        self.bad_data_percentage = bad_data_percentage
        self.customer_ids = set()
        self.customers = []
        self.customer_details = []
        
    def generate_customer_id(self):
        """Generate unique 8-digit customer ID"""
        while True:
            cust_id = f"C{random.randint(10000000, 99999999)}"
            if cust_id not in self.customer_ids:
                self.customer_ids.add(cust_id)
                return cust_id
    
    @staticmethod
    def generate_email(first_name, last_name):
        """Generate email address"""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com"]
        return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
    
    @staticmethod
    def generate_invalid_email():
        """Generate invalid email addresses"""
        invalid_emails = [
            "invalid.email",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "工具@工具.com",  # Non-ASCII
            "verylongemailaddress" + "x" * 50 + "@domain.com",
            "NULL",
            ""
        ]
        return random.choice(invalid_emails)
    
    @staticmethod
    def generate_phone():
        """Generate phone number"""
        return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    @staticmethod
    def generate_invalid_phone():
        """Generate invalid phone numbers"""
        invalid_phones = [
            "123",  # Too short
            "1" * 50,  # Too long
            "abc-def-ghij",  # Letters
            "123-456-789",  # Missing digit
            "000-000-0000",  # All zeros
            "+999-999-9999",  # Invalid country code
            ""
        ]
        return random.choice(invalid_phones)
    
    @staticmethod
    def generate_address():
        """Generate random address"""
        street_num = random.randint(1, 9999)
        street_name = random.choice(STREET_NAMES)
        street_type = random.choice(STREET_TYPES)
        city = random.choice(CITIES)
        state = random.choice(STATES)
        zip_code = ZIP_CODES.get(city, f"{random.randint(10000, 99999)}")
        
        return {
            "street": f"{street_num} {street_name} {street_type}",
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "country": random.choice(COUNTRIES)
        }
    
    @staticmethod
    def generate_invalid_address():
        """Generate invalid address"""
        invalid_addresses = [
            {"street": "", "city": "", "state": "XX", "zip_code": "00000", "country": ""},
            {"street": "123 Main St", "city": "InvalidCityName123", "state": "XX", "zip_code": "ABCDE", "country": "InvalidCountry"},
            {"street": "Very Long Street Name " * 10, "city": "C", "state": "USA", "zip_code": "123", "country": "U"},
            {"street": "NULL", "city": "NULL", "state": "NULL", "zip_code": "NULL", "country": "NULL"}
        ]
        return random.choice(invalid_addresses)
    
    @staticmethod
    def generate_date_of_birth(future_date=False):
        """Generate random date of birth"""
        if future_date:
            # Generate future date (invalid)
            future_date = datetime.now() + timedelta(days=random.randint(1, 365*10))
            return future_date.strftime("%Y-%m-%d")
        else:
            # Generate valid date (18-80 years old)
            end_date = datetime.now() - timedelta(days=365*18)
            start_date = end_date - timedelta(days=365*62)
            random_days = random.randint(0, (end_date - start_date).days)
            return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    @staticmethod
    def generate_credit_score(invalid=False):
        """Generate credit score"""
        if invalid:
            invalid_scores = [-100, 0, 1000, 9999, None]
            return random.choice(invalid_scores)
        return random.randint(300, 850)
    
    @staticmethod
    def generate_annual_income(invalid=False):
        """Generate annual income"""
        if invalid:
            invalid_incomes = [-50000, 0, 999999999, -1, None]
            return random.choice(invalid_incomes)
        
        brackets = [
            (20000, 50000, 0.3),
            (50000, 100000, 0.4),
            (100000, 200000, 0.2),
            (200000, 500000, 0.1)
        ]
        
        bracket = random.choices(brackets, weights=[w for _, _, w in brackets])[0]
        return random.randint(bracket[0], bracket[1])
    
    def introduce_bad_data_customer(self, customer):
        """Introduce various types of bad data into customer record"""
        bad_data_type = BadDataGenerator.get_bad_data_type()
        
        if bad_data_type == "missing_data":
            fields_to_corrupt = random.sample(["email", "phone", "street", "city"], k=random.randint(1, 3))
            return BadDataGenerator.generate_missing_data(customer, fields_to_corrupt)
        
        elif bad_data_type == "invalid_format":
            if random.choice([True, False]):
                customer["email"] = self.generate_invalid_email()
            else:
                customer["phone"] = self.generate_invalid_phone()
            customer["is_bad_data"] = True
            customer["bad_data_type"] = "invalid_format"
        
        elif bad_data_type == "out_of_range":
            if random.choice([True, False]):
                # Future birth date
                customer["date_of_birth"] = self.generate_date_of_birth(future_date=True)
            else:
                # Negative or extremely high values
                if "date_of_birth" in customer:
                    customer["date_of_birth"] = "1899-01-01"  # Too old
            customer["is_bad_data"] = True
            customer["bad_data_type"] = "out_of_range"
        
        elif bad_data_type == "inconsistent_data":
            # City and state mismatch
            customer["state"] = "XX"
            customer["is_bad_data"] = True
            customer["bad_data_type"] = "inconsistent_data"
        
        elif bad_data_type == "malformed_data":
            field = random.choice(["first_name", "last_name", "email"])
            return BadDataGenerator.generate_malformed_data(customer, field)
        
        return customer
    
    def introduce_bad_data_customer_detail(self, detail):
        """Introduce bad data into customer detail record"""
        bad_data_type = BadDataGenerator.get_bad_data_type()
        
        if bad_data_type == "missing_data":
            fields_to_corrupt = random.sample(["employment_status", "annual_income", "credit_score"], k=random.randint(1, 3))
            return BadDataGenerator.generate_missing_data(detail, fields_to_corrupt)
        
        elif bad_data_type == "out_of_range":
            if random.choice([True, False]):
                detail["credit_score"] = self.generate_credit_score(invalid=True)
            else:
                detail["annual_income"] = self.generate_annual_income(invalid=True)
            detail["is_bad_data"] = True
            detail["bad_data_type"] = "out_of_range"
        
        elif bad_data_type == "inconsistent_data":
            # Employment status vs income inconsistency
            if detail["employment_status"] == "Unemployed":
                detail["annual_income"] = random.randint(100000, 500000)  # High income for unemployed
            detail["is_bad_data"] = True
            detail["bad_data_type"] = "inconsistent_data"
        
        elif bad_data_type == "invalid_format":
            detail["employment_status"] = "InvalidStatus123"
            detail["is_bad_data"] = True
            detail["bad_data_type"] = "invalid_format"
        
        return detail
    
    def generate(self):
        """Generate customers and customer details with bad data"""
        self.customers = []
        self.customer_details = []
        
        bad_customer_count = 0
        bad_detail_count = 0
        
        for _ in range(self.num_customers):
            customer_id = self.generate_customer_id()
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = self.generate_email(first_name, last_name)
            phone = self.generate_phone()
            dob = self.generate_date_of_birth()
            address = self.generate_address()
            created_at = (datetime.now() - timedelta(days=random.randint(0, 365*5))).strftime("%Y-%m-%d %H:%M:%S")
            
            # Customer record
            customer = {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "date_of_birth": dob,
                "street": address["street"],
                "city": address["city"],
                "state": address["state"],
                "zip_code": address["zip_code"],
                "country": address["country"],
                "created_at": created_at
            }
            
            # Introduce bad data for customer
            if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
                customer = self.introduce_bad_data_customer(customer)
                bad_customer_count += 1
            
            self.customers.append(customer)
            
            # Customer details record
            detail = {
                "customer_id": customer_id,
                "employment_status": random.choice(EMPLOYMENT_TYPES),
                "annual_income": self.generate_annual_income(),
                "credit_score": self.generate_credit_score(),
                "marital_status": random.choice(MARITAL_STATUSES),
                "education_level": random.choice(EDUCATION_LEVELS),
                "created_at": created_at
            }
            
            # Introduce bad data for customer details (independent chance)
            if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
                detail = self.introduce_bad_data_customer_detail(detail)
                bad_detail_count += 1
            
            self.customer_details.append(detail)
        
        print(f"Generated {len(self.customers)} customers ({bad_customer_count} with bad data)")
        print(f"Generated {len(self.customer_details)} customer details ({bad_detail_count} with bad data)")
        
        return self.customers, self.customer_details


def generate_customer():
    """Convenience function to generate a single customer record.

    Returns the generated customer dict. Keeps backward compatibility
    with code expecting `generate_customer()` at module level.
    """
    gen = CustomerGenerator(num_customers=1)
    customers, _ = gen.generate()
    return customers[0] if customers else None