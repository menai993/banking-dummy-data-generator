import random
from datetime import datetime
from constants.banking_products import MERCHANT_CATEGORIES
from constants.addresses import CITIES

class MerchantGenerator:
    def __init__(self, num_merchants=500, bad_data_percentage=0.0):
        self.num_merchants = num_merchants
        self.bad_data_percentage = bad_data_percentage
        self.merchant_ids = set()
        self.merchants = []
        
    def generate_merchant_id(self):
        """Generate unique merchant ID"""
        while True:
            merchant_id = f"MER{random.randint(100000, 999999)}"
            if merchant_id not in self.merchant_ids:
                self.merchant_ids.add(merchant_id)
                return merchant_id
    
    def generate_merchant_name(self, category):
        """Generate merchant name based on category"""
        prefixes = {
            "Retail": ["Best", "Super", "Mega", "Quality", "Prime"],
            "Restaurant": ["Golden", "Royal", "Tasty", "Delicious", "Gourmet"],
            "Travel": ["Global", "Express", "First Class", "Premium", "Luxury"],
            "Entertainment": ["Star", "Magic", "Dream", "Fantasy", "Epic"],
            "Utilities": ["City", "Metro", "National", "Regional", "Local"],
            "Healthcare": ["Medi", "Health", "Care", "Wellness", "Clinic"]
        }
        
        suffixes = {
            "Retail": ["Mart", "Store", "Shop", "Center", "Outlet"],
            "Restaurant": ["Grill", "Bistro", "Cafe", "Kitchen", "Diner"],
            "Travel": ["Travels", "Tours", "Airlines", "Hotels", "Cruises"],
            "Entertainment": ["Cinema", "Theater", "Games", "Fun", "Entertainment"],
            "Utilities": ["Services", "Utility", "Company", "Corp", "Inc"],
            "Healthcare": ["Hospital", "Clinic", "Center", "Care", "Medical"]
        }
        
        prefix = random.choice(prefixes.get(category, ["Super"]))
        suffix = random.choice(suffixes.get(category, ["Store"]))
        
        return f"{prefix} {suffix}"
    
    def generate_mcc(self, category):
        """Generate Merchant Category Code"""
        mcc_codes = {
            "Retail": ["5411", "5311", "5331", "5399"],
            "Restaurant": ["5812", "5814", "5813"],
            "Travel": ["4722", "4511", "4111", "4131"],
            "Entertainment": ["7832", "7996", "7997", "7999"],
            "Utilities": ["4900", "4814", "4899"],
            "Healthcare": ["8011", "8021", "8031", "8049"]
        }
        
        return random.choice(mcc_codes.get(category, ["5399"]))
    
    def introduce_bad_data_merchant(self, merchant):
        """Introduce bad data into merchant record"""
        from utils.helpers import BadDataGenerator
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["mcc_code", "phone", "email", "category"]
                return BadDataGenerator.generate_missing_data(merchant, random.sample(fields, 2))
            
            elif bad_data_type == "invalid_format":
                merchant["mcc_code"] = "ABCD"  # Invalid MCC
                merchant["is_bad_data"] = True
                merchant["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "inconsistent_data":
                # Category and MCC mismatch
                merchant["mcc_code"] = "0000"
                merchant["is_bad_data"] = True
                merchant["bad_data_type"] = "inconsistent_data"
        
        return merchant
    
    def generate(self):
        """Generate merchant data"""
        self.merchants = []
        bad_merchant_count = 0
        
        for _ in range(self.num_merchants):
            category = random.choice(MERCHANT_CATEGORIES)
            city = random.choice(CITIES)
            
            merchant = {
                "merchant_id": self.generate_merchant_id(),
                "merchant_name": self.generate_merchant_name(category),
                "category": category,
                "mcc_code": self.generate_mcc(category),
                "street": f"{random.randint(1, 9999)} {random.choice(['Commerce', 'Market', 'Business'])} Ave",
                "city": city,
                "state": random.choice(["CA", "NY", "TX", "FL", "IL"]),
                "zip_code": f"{random.randint(10000, 99999)}",
                "country": "USA",
                "phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "email": f"info@{self.generate_merchant_name(category).replace(' ', '').lower()}.com",
                "website": f"www.{self.generate_merchant_name(category).replace(' ', '').lower()}.com",
                "status": random.choices(["Active", "Inactive", "Suspended"], weights=[0.9, 0.07, 0.03])[0],
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 365*5))).strftime("%Y-%m-%d %H:%M:%S")
            }
            
            merchant = self.introduce_bad_data_merchant(merchant)
            if merchant.get('is_bad_data'):
                bad_merchant_count += 1
            
            self.merchants.append(merchant)
        
        print(f"Generated {len(self.merchants)} merchants ({bad_merchant_count} with bad data)")
        return self.merchments