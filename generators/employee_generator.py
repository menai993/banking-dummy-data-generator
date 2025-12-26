import random
from datetime import datetime, timedelta
from constants.names import FIRST_NAMES, LAST_NAMES
from constants.banking_products import EMPLOYEE_ROLES, DEPARTMENT_TYPES

class EmployeeGenerator:
    def __init__(self, branches_data, num_employees=200, bad_data_percentage=0.0):
        self.branches = branches_data
        self.num_employees = num_employees
        self.bad_data_percentage = bad_data_percentage
        self.employee_ids = set()
        self.employees = []
        
    def generate_employee_id(self):
        """Generate unique employee ID"""
        while True:
            emp_id = f"EMP{random.randint(10000, 99999)}"
            if emp_id not in self.employee_ids:
                self.employee_ids.add(emp_id)
                return emp_id
    
    @staticmethod
    def generate_email(first_name, last_name):
        """Generate employee email"""
        return f"{first_name.lower()}.{last_name.lower()}@bank.com"
    
    @staticmethod
    def generate_phone_extension():
        """Generate phone extension"""
        return f"x{random.randint(1000, 9999)}"
    
    @staticmethod
    def generate_salary(role):
        """Generate salary based on role"""
        base_salaries = {
            "Teller": (30000, 45000),
            "Customer Service": (35000, 50000),
            "Loan Officer": (50000, 80000),
            "Branch Manager": (70000, 120000),
            "Operations": (45000, 70000),
            "Compliance": (60000, 90000)
        }
        
        min_salary, max_salary = base_salaries.get(role, (40000, 60000))
        return random.randint(min_salary, max_salary)
    
    def generate_manager_id(self, branch_id, role):
        """Generate manager ID for non-manager employees"""
        if role == "Branch Manager":
            return None
        
        # Find branch manager for this branch
        branch_managers = [emp for emp in self.employees 
                          if emp.get('branch_id') == branch_id and emp.get('role') == "Branch Manager"]
        
        if branch_managers:
            return random.choice(branch_managers)["employee_id"]
        return None
    
    def introduce_bad_data_employee(self, employee):
        """Introduce bad data into employee record"""
        from utils.helpers import BadDataGenerator
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["email", "phone_extension", "salary", "department"]
                return BadDataGenerator.generate_missing_data(employee, random.sample(fields, 2))
            
            elif bad_data_type == "out_of_range":
                employee["salary"] = -50000  # Negative salary
                employee["is_bad_data"] = True
                employee["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Teller with manager salary
                if employee["role"] == "Teller":
                    employee["salary"] = 100000
                employee["is_bad_data"] = True
                employee["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                employee["email"] = "invalid-email"
                employee["is_bad_data"] = True
                employee["bad_data_type"] = "invalid_format"
        
        return employee
    
    def generate(self):
        """Generate employee data"""
        self.employees = []
        bad_employee_count = 0
        
        # First, ensure each branch has a manager
        for branch in self.branches:
            # Generate branch manager
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            manager = {
                "employee_id": self.generate_employee_id(),
                "branch_id": branch["branch_id"],
                "first_name": first_name,
                "last_name": last_name,
                "email": self.generate_email(first_name, last_name),
                "phone_extension": self.generate_phone_extension(),
                "role": "Branch Manager",
                "department": "Branch Management",
                "salary": self.generate_salary("Branch Manager"),
                "hire_date": (datetime.now() - timedelta(days=random.randint(365, 365*10))).strftime("%Y-%m-%d"),
                "manager_id": None,
                "status": "Active",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            manager = self.introduce_bad_data_employee(manager)
            if manager.get('is_bad_data'):
                bad_employee_count += 1
            
            self.employees.append(manager)
        
        # Generate remaining employees
        remaining_employees = self.num_employees - len(self.branches)
        
        for _ in range(remaining_employees):
            branch = random.choice(self.branches)
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            role = random.choice(EMPLOYEE_ROLES)
            
            employee = {
                "employee_id": self.generate_employee_id(),
                "branch_id": branch["branch_id"],
                "first_name": first_name,
                "last_name": last_name,
                "email": self.generate_email(first_name, last_name),
                "phone_extension": self.generate_phone_extension(),
                "role": role,
                "department": random.choice(DEPARTMENT_TYPES),
                "salary": self.generate_salary(role),
                "hire_date": (datetime.now() - timedelta(days=random.randint(30, 365*5))).strftime("%Y-%m-%d"),
                "manager_id": self.generate_manager_id(branch["branch_id"], role),
                "status": random.choices(["Active", "Inactive", "On Leave"], weights=[0.9, 0.05, 0.05])[0],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            employee = self.introduce_bad_data_employee(employee)
            if employee.get('is_bad_data'):
                bad_employee_count += 1
            
            self.employees.append(employee)
        
        print(f"Generated {len(self.employees)} employees ({bad_employee_count} with bad data)")
        return self.employees