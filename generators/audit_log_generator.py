import random
from datetime import datetime, timedelta

class AuditLogGenerator:
    def __init__(self, users_data, bad_data_percentage=0.0):
        self.users = users_data  # Could be customers, employees, or system users
        self.bad_data_percentage = bad_data_percentage
        self.audit_logs = []
        
    @staticmethod
    def generate_audit_id():
        """Generate audit log ID"""
        return f"AUD{random.randint(100000000, 999999999)}"
    
    @staticmethod
    def generate_action_types():
        """Generate different audit action types"""
        return [
            "LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE", 
            "VIEW", "APPROVE", "REJECT", "TRANSFER", "WITHDRAWAL",
            "PASSWORD_CHANGE", "PROFILE_UPDATE", "ACCOUNT_CREATE",
            "LOAN_APPLICATION", "CARD_ISSUE", "STATEMENT_GENERATE"
        ]
    
    @staticmethod
    def generate_entity_types():
        """Generate entity types for audit logs"""
        return [
            "CUSTOMER", "ACCOUNT", "TRANSACTION", "LOAN", "CARD",
            "EMPLOYEE", "BRANCH", "MERCHANT", "USER", "SYSTEM"
        ]
    
    @staticmethod
    def generate_status_codes():
        """Generate status codes"""
        return ["SUCCESS", "FAILURE", "PENDING", "ERROR", "WARNING"]
    
    @staticmethod
    def generate_ip_address():
        """Generate random IP address"""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    
    @staticmethod
    def generate_user_agent():
        """Generate random user agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 11; Mobile) AppleWebKit/537.36",
            "PostmanRuntime/7.28.4",
            "curl/7.68.0"
        ]
        return random.choice(user_agents)
    
    def introduce_bad_data_audit(self, audit_log):
        """Introduce bad data into audit log"""
        from utils.helpers import BadDataGenerator
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["ip_address", "user_agent", "status_code", "action_details"]
                return BadDataGenerator.generate_missing_data(audit_log, random.sample(fields, 2))
            
            elif bad_data_type == "invalid_format":
                audit_log["ip_address"] = "999.999.999.999"  # Invalid IP
                audit_log["is_bad_data"] = True
                audit_log["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "inconsistent_data":
                # Success status with error message
                if audit_log["status_code"] == "SUCCESS":
                    audit_log["error_message"] = "Critical error occurred"
                audit_log["is_bad_data"] = True
                audit_log["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "malformed_data":
                return BadDataGenerator.generate_malformed_data(audit_log, "action_details")
        
        return audit_log
    
    def generate(self, logs_per_user_min=5, logs_per_user_max=50):
        """Generate audit logs"""
        self.audit_logs = []
        bad_audit_count = 0
        
        for user in self.users:
            user_id = user.get('customer_id') or user.get('employee_id') or user.get('user_id', 'SYS')
            num_logs = random.randint(logs_per_user_min, logs_per_user_max)
            
            for _ in range(num_logs):
                action_date = datetime.now() - timedelta(days=random.randint(0, 365))
                
                audit_log = {
                    "audit_id": self.generate_audit_id(),
                    "user_id": user_id,
                    "action_type": random.choice(self.generate_action_types()),
                    "entity_type": random.choice(self.generate_entity_types()),
                    "entity_id": f"ENT{random.randint(10000, 99999)}",
                    "action_date": action_date.strftime("%Y-%m-%d"),
                    "action_time": action_date.strftime("%H:%M:%S"),
                    "ip_address": self.generate_ip_address(),
                    "user_agent": self.generate_user_agent(),
                    "status_code": random.choices(self.generate_status_codes(), weights=[0.85, 0.08, 0.04, 0.02, 0.01])[0],
                    "action_details": f"Performed {random.choice(['created', 'updated', 'viewed', 'deleted'])} operation",
                    "error_message": None if random.random() > 0.1 else random.choice([
                        "Access denied", "Invalid input", "System error", "Timeout", "Connection failed"
                    ]),
                    "created_at": action_date.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add error message for failed status
                if audit_log["status_code"] in ["FAILURE", "ERROR"] and not audit_log["error_message"]:
                    audit_log["error_message"] = random.choice([
                        "Database connection failed", 
                        "Invalid credentials",
                        "Insufficient permissions",
                        "Resource not found",
                        "Validation error"
                    ])
                
                audit_log = self.introduce_bad_data_audit(audit_log)
                if audit_log.get('is_bad_data'):
                    bad_audit_count += 1
                
                self.audit_logs.append(audit_log)
        
        # Sort by date
        self.audit_logs.sort(key=lambda x: (x["action_date"], x["action_time"]))
        
        print(f"Generated {len(self.audit_logs)} audit logs ({bad_audit_count} with bad data)")
        return self.audit_logs