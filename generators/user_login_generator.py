# generators/user_login_generator.py
import random
from datetime import datetime, timedelta
from utils.helpers import BadDataGenerator
from constants.login_constants import (
    DEVICE_TYPES, BROWSERS, OPERATING_SYSTEMS,
    LOGIN_METHODS, FAILURE_REASONS, 
)

class UserLoginGenerator:
    def __init__(self, min_logins=8, max_logins=30, bad_data_percentage=0.0, customers=None):
        self.min_logins = min_logins
        self.max_logins = max_logins
        self.bad_data_percentage = bad_data_percentage
        self.customers = customers or []
        self.user_logins = []
        
    def introduce_bad_data_login(self, login):
        """Introduce bad data into user login"""
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["ip_address", "device_type", "browser"]
                return BadDataGenerator.generate_missing_data(login, fields)
            
            elif bad_data_type == "out_of_range":
                login["session_duration_minutes"] = 10000  # Too long
                login["login_timestamp"] = "2050-01-01 25:61:61"  # Future date
                login["is_bad_data"] = True
                login["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Login successful but has failure reason
                login["login_status"] = "SUCCESS"
                login["failure_reason"] = "INVALID_PASSWORD"
                login["is_bad_data"] = True
                login["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                login["ip_address"] = "999.999.999.999"
                login["login_timestamp"] = "2024/13/45"
                login["is_bad_data"] = True
                login["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "malformed_data":
                login["device_type"] = "<script>alert('xss')</script>"
                login["browser"] = "'; DROP TABLE users; --"
                login["is_bad_data"] = True
                login["bad_data_type"] = "malformed_data"
            
            elif bad_data_type == "duplicate_data":
                # This would require tracking previous logins
                login["is_bad_data"] = True
                login["bad_data_type"] = "duplicate_data"
        
        return login
    
    def generate(self):
        """Generate user login records"""
        self.user_logins = []
        bad_login_count = 0
        
        # Generate for each customer
        for customer_index, customer in enumerate(self.customers[:100] if len(self.customers) > 100 else self.customers):
            customer_id = customer.get('customer_id', customer_index + 1)
            
            # Random number of logins for this customer
            num_logins = random.randint(self.min_logins, self.max_logins)
            
            # Generate login timeline (last 90 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            for _ in range(num_logins):
                # Create login timestamp
                login_time = start_date + timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
                
                # Determine login success
                is_successful = random.random() > 0.05  # 95% success rate
                login_status = "SUCCESS" if is_successful else random.choice(["FAILED", "BLOCKED"])
                
                # Generate IP address
                ip_address = f"{random.randint(192, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
                
                # On failure, sometimes use suspicious IPs
                if not is_successful and random.random() > 0.5:
                    suspicious_prefixes = ['10.0.0.', '192.168.', '172.16.']
                    ip_address = random.choice(suspicious_prefixes) + str(random.randint(1, 255))
                
                login = {
                    "login_id": len(self.user_logins) + 1,
                    "customer_id": customer_id,
                    "login_timestamp": login_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "ip_address": ip_address,
                    "device_type": random.choice(DEVICE_TYPES),
                    "browser": random.choice(BROWSERS),
                    "operating_system": random.choice(OPERATING_SYSTEMS),
                    "login_method": random.choice(LOGIN_METHODS),
                    "login_status": login_status,
                    "failure_reason": None,
                    "session_duration_minutes": None,
                    "geolocation": f"{random.uniform(-90, 90):.4f},{random.uniform(-180, 180):.4f}",
                    "is_vpn_used": random.choice([True, False]),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add failure reason if login failed
                if not is_successful:
                    login["failure_reason"] = random.choice(FAILURE_REASONS)
                else:
                    login["session_duration_minutes"] = random.randint(1, 240)
                
                # Introduce bad data
                login = self.introduce_bad_data_login(login)
                if login.get('is_bad_data'):
                    bad_login_count += 1
                
                self.user_logins.append(login)
            
            # Add occasional brute force attacks
            if random.random() > 0.95:  # 5% of customers get attacks
                attack_logins = random.randint(5, 20)
                for _ in range(attack_logins):
                    attack_time = start_date + timedelta(
                        days=random.randint(0, 90),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    attack_login = {
                        "login_id": len(self.user_logins) + 1,
                        "customer_id": customer_id,
                        "login_timestamp": attack_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "ip_address": f"10.0.0.{random.randint(1, 255)}",
                        "device_type": "Unknown Device",
                        "browser": "UNKNOWN",
                        "operating_system": "UNKNOWN",
                        "login_method": "PASSWORD",
                        "login_status": "FAILED",
                        "failure_reason": "BRUTE_FORCE_ATTEMPT",
                        "session_duration_minutes": 0,
                        "geolocation": None,
                        "is_vpn_used": True,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.user_logins.append(attack_login)
        
        print(f"Generated {len(self.user_logins)} user login records ({bad_login_count} with bad data)")
        return self.user_logins


def generate_user_login(customer_id: str):
    """Compatibility shim: generate a single user login record for given customer."""
    customer = {"customer_id": customer_id}
    gen = UserLoginGenerator(customers=[customer])
    logins = gen.generate()
    return logins[0] if logins else None