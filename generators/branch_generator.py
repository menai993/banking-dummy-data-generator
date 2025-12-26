import random
from datetime import datetime, timedelta
from constants.addresses import CITIES, STATES
from constants.banking_products import BRANCH_TYPES
from utils.helpers import BadDataGenerator

class BranchGenerator:
    def __init__(self, num_branches=50, bad_data_percentage=0.0):
        self.num_branches = num_branches
        self.bad_data_percentage = bad_data_percentage
        self.branch_ids = set()
        self.branches = []
        
    def generate_branch_id(self):
        """Generate unique branch ID"""
        while True:
            branch_id = f"BR{random.randint(1000, 9999)}"
            if branch_id not in self.branch_ids:
                self.branch_ids.add(branch_id)
                return branch_id
    
    def generate_branch_code(self, city):
        """Generate branch code based on city"""
        city_code = ''.join([c for c in city if c.isalpha()])[:3].upper()
        return f"{city_code}{random.randint(100, 999)}"
    
    def generate_phone(self):
        """Generate branch phone number"""
        return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    def generate_email(self, branch_code):
        """Generate branch email"""
        domains = ["bank.com", "financial.com", "banking-services.com"]
        return f"branch.{branch_code.lower()}@{random.choice(domains)}"
    
    def generate_manager_name(self):
        """Generate branch manager name"""
        from constants.names import FIRST_NAMES, LAST_NAMES
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    
    def introduce_bad_data_branch(self, branch):
        """Introduce bad data into branch record"""
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields_to_corrupt = random.sample(["manager_name", "phone", "email", "branch_type"], k=random.randint(1, 2))
                for field in fields_to_corrupt:
                    if field in branch:
                        branch[field] = None
                branch['is_bad_data'] = True
                branch['bad_data_type'] = 'missing_data'
            
            elif bad_data_type == "invalid_format":
                branch["phone"] = "invalid-phone"
                branch["is_bad_data"] = True
                branch["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "inconsistent_data":
                # City-state mismatch
                branch["state"] = "XX"
                branch["is_bad_data"] = True
                branch["bad_data_type"] = "inconsistent_data"
        
        return branch
    
    def generate(self):
        """Generate branch data"""
        self.branches = []
        bad_branch_count = 0  # INITIALIZE THE COUNTER
        
        for _ in range(self.num_branches):
            city = random.choice(CITIES)
            state = random.choice(STATES)
            
            branch = {
                "branch_id": self.generate_branch_id(),
                "branch_name": f"{city} {random.choice(['Main', 'Central', 'Downtown', 'Plaza'])} Branch",
                "branch_code": self.generate_branch_code(city),
                "branch_type": random.choice(BRANCH_TYPES),
                "street": f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Broadway'])} St",
                "city": city,
                "state": state,
                "zip_code": f"{random.randint(10000, 99999)}",
                "country": "USA",
                "phone": self.generate_phone(),
                "email": self.generate_email(self.generate_branch_code(city)),
                "manager_name": self.generate_manager_name(),
                "opening_date": (datetime.now() - timedelta(days=random.randint(365, 365*20))).strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            branch = self.introduce_bad_data_branch(branch)
            if branch.get('is_bad_data'):
                bad_branch_count += 1
            
            self.branches.append(branch)
        
        print(f"Generated {len(self.branches)} branches ({bad_branch_count} with bad data)")
        return self.branches