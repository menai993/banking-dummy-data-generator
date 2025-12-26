import random
from datetime import datetime, timedelta

class ExchangeRateGenerator:
    def __init__(self, num_days=365, bad_data_percentage=0.0):
        self.num_days = num_days
        self.bad_data_percentage = bad_data_percentage
        self.exchange_rates = []
        
    @staticmethod
    def generate_currency_pairs():
        """Generate currency pairs"""
        return [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "JPY"), ("USD", "CAD"),
            ("USD", "AUD"), ("USD", "CHF"), ("EUR", "GBP"), ("EUR", "JPY"),
            ("GBP", "JPY"), ("AUD", "USD"), ("CAD", "USD")
        ]
    
    @staticmethod
    def generate_base_rate(base_currency, target_currency):
        """Generate base exchange rate"""
        base_rates = {
            ("USD", "EUR"): 0.92,
            ("USD", "GBP"): 0.79,
            ("USD", "JPY"): 150.0,
            ("USD", "CAD"): 1.35,
            ("USD", "AUD"): 1.52,
            ("USD", "CHF"): 0.88,
            ("EUR", "GBP"): 0.86,
            ("EUR", "JPY"): 163.0,
            ("GBP", "JPY"): 190.0,
            ("AUD", "USD"): 0.66,
            ("CAD", "USD"): 0.74
        }
        
        return base_rates.get((base_currency, target_currency), 
                             round(random.uniform(0.5, 2.0), 4))
    
    def introduce_bad_data_exchange(self, rate):
        """Introduce bad data into exchange rate"""
        from utils.helpers import BadDataGenerator
        
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["buy_rate", "sell_rate", "mid_rate"]
                return BadDataGenerator.generate_missing_data(rate, fields)
            
            elif bad_data_type == "out_of_range":
                rate["buy_rate"] = -0.5  # Negative rate
                rate["is_bad_data"] = True
                rate["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Sell rate lower than buy rate
                rate["sell_rate"] = rate["buy_rate"] * 0.9
                rate["is_bad_data"] = True
                rate["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                rate["buy_rate"] = "invalid"
                rate["is_bad_data"] = True
                rate["bad_data_type"] = "invalid_format"
        
        return rate
    
    def generate(self):
        """Generate exchange rate history"""
        self.exchange_rates = []
        bad_rate_count = 0
        currency_pairs = self.generate_currency_pairs()
        start_date = datetime.now() - timedelta(days=self.num_days)
        
        for day_offset in range(self.num_days):
            current_date = start_date + timedelta(days=day_offset)
            
            for base_currency, target_currency in currency_pairs:
                # Generate realistic rates with some volatility
                base_rate = self.generate_base_rate(base_currency, target_currency)
                
                # Add daily variation (-2% to +2%)
                daily_variation = random.uniform(-0.02, 0.02)
                mid_rate = round(base_rate * (1 + daily_variation), 4)
                
                # Add spread (difference between buy and sell)
                spread = random.uniform(0.001, 0.005)
                buy_rate = round(mid_rate * (1 - spread/2), 4)
                sell_rate = round(mid_rate * (1 + spread/2), 4)
                
                rate = {
                    "rate_id": f"EXR{current_date.strftime('%Y%m%d')}{base_currency}{target_currency}",
                    "base_currency": base_currency,
                    "target_currency": target_currency,
                    "buy_rate": buy_rate,
                    "sell_rate": sell_rate,
                    "mid_rate": mid_rate,
                    "rate_date": current_date.strftime("%Y-%m-%d"),
                    "valid_from": f"{current_date.strftime('%Y-%m-%d')} 00:00:00",
                    "valid_to": f"{current_date.strftime('%Y-%m-%d')} 23:59:59",
                    "source": random.choice(["Central Bank", "Reuters", "Bloomberg", "Internal"]),
                    "created_at": current_date.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                rate = self.introduce_bad_data_exchange(rate)
                if rate.get('is_bad_data'):
                    bad_rate_count += 1
                
                self.exchange_rates.append(rate)
        
        print(f"Generated {len(self.exchange_rates)} exchange rates ({bad_rate_count} with bad data)")
        return self.exchange_rates