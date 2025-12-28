# generators/fraud_alert_generator.py - Updated date parsing logic
import random
from datetime import datetime, timedelta
from constants.fraud_constants import (
    FRAUD_REASONS, ALERT_STATUSES, DETECTION_METHODS, FRAUD_TYPES
)
from utils.helpers import BadDataGenerator  # Import at top level

class FraudAlertGenerator:
    def __init__(self, fraud_rate=0.05, bad_data_percentage=0.0, transactions=None, accounts=None):
        self.fraud_rate = fraud_rate
        self.bad_data_percentage = bad_data_percentage
        self.transactions = transactions or []
        self.accounts = accounts or []
        self._account_to_customer = {
            acc.get("account_id"): acc.get("customer_id")
            for acc in self.accounts
            if acc and acc.get("account_id")
        }
        self.fraud_alerts = []
        
    def introduce_bad_data_fraud(self, alert):
        """Introduce bad data into fraud alert"""
        if BadDataGenerator.should_generate_bad_data(self.bad_data_percentage):
            bad_data_type = BadDataGenerator.get_bad_data_type()
            
            if bad_data_type == "missing_data":
                fields = ["fraud_reason", "severity", "detection_method"]
                return BadDataGenerator.generate_missing_data(alert, fields)
            
            elif bad_data_type == "out_of_range":
                alert["severity_score"] = -10  # Negative score
                alert["financial_loss"] = -500000  # Negative loss
                alert["is_bad_data"] = True
                alert["bad_data_type"] = "out_of_range"
            
            elif bad_data_type == "inconsistent_data":
                # Status doesn't match dates
                alert["alert_status"] = "RESOLVED"
                alert["resolution_date"] = None  # Should have date if resolved
                alert["is_bad_data"] = True
                alert["bad_data_type"] = "inconsistent_data"
            
            elif bad_data_type == "invalid_format":
                alert["alert_timestamp"] = "2024/13/45 25:61:61"
                alert["fraud_reason"] = "INVALID_REASON_XYZ"
                alert["is_bad_data"] = True
                alert["bad_data_type"] = "invalid_format"
            
            elif bad_data_type == "malformed_data":
                alert["fraud_reason"] = "<script>alert('xss')</script>"
                alert["is_bad_data"] = True
                alert["bad_data_type"] = "malformed_data"
            
            elif bad_data_type == "duplicate_data":
                # This would require tracking previous alerts
                alert["is_bad_data"] = True
                alert["bad_data_type"] = "duplicate_data"
        
        return alert
    
    @staticmethod
    def parse_transaction_date(transaction):
        """Safely parse transaction date with multiple fallbacks"""
        try:
            # Try to get the transaction date
            transaction_date = transaction.get('transaction_date')
            
            if not transaction_date:
                # If no date, use random recent date
                return datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Handle different date formats
            if isinstance(transaction_date, datetime):
                return transaction_date
            elif isinstance(transaction_date, str):
                # Try different date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y/%m/%d',
                    '%d-%m-%Y',
                    '%d/%m/%Y'
                ]
                
                for date_format in date_formats:
                    try:
                        return datetime.strptime(transaction_date, date_format)
                    except ValueError:
                        continue
                
                # If all formats fail, use default
                return datetime.now() - timedelta(days=random.randint(1, 30))
            else:
                # If it's some other type, use default
                return datetime.now() - timedelta(days=random.randint(1, 30))
                
        except Exception as e:
            # Fallback to default date
            return datetime.now() - timedelta(days=random.randint(1, 30))
    
    def generate(self):
        """Generate fraud alerts"""
        self.fraud_alerts = []
        bad_alert_count = 0


        # Calculate number of alerts
        num_alerts = int(len(self.transactions) * self.fraud_rate)
        num_alerts = min(num_alerts, len(self.transactions)) if self.transactions else num_alerts
        
        # Sample transactions for alerts
        if self.transactions and num_alerts < len(self.transactions):
            alert_transactions = random.sample(self.transactions, num_alerts)
        elif self.transactions:
            alert_transactions = self.transactions.copy()
        else:
            # Generate dummy transactions if none provided
            alert_transactions = [{"transaction_id": i + 1, "amount": random.uniform(10, 10000)} 
                                 for i in range(num_alerts)]
        
        next_alert_id = 1
        
        for transaction in alert_transactions:
            # Parse transaction date safely
            trans_date = self.parse_transaction_date(transaction)
            
            # Generate alert date (1-72 hours after transaction)
            try:
                alert_date = trans_date + timedelta(hours=random.randint(1, 72))
            except OverflowError:
                alert_date = trans_date 
            
            # Determine severity
            amount = 0
            try:
                amount = abs(float(transaction.get('amount', 0)))
            except (ValueError, TypeError):
                amount = random.uniform(10, 10000)
            
            if amount > 10000:
                severity = 'CRITICAL'
                severity_score = random.randint(80, 100)
            elif amount > 5000:
                severity = 'HIGH'
                severity_score = random.randint(60, 79)
            elif amount > 1000:
                severity = 'MEDIUM'
                severity_score = random.randint(40, 59)
            else:
                severity = 'LOW'
                severity_score = random.randint(20, 39)
            
            # Get transaction and account IDs
            transaction_id = transaction.get('transaction_id', next_alert_id)
            account_id = transaction.get('account_id')

            # Derive customer_id from the account mapping (transactions do not carry customer_id)
            # If we cannot resolve it, keep NULL to avoid foreign key violations.
            customer_id = None
            if account_id is not None:
                customer_id = self._account_to_customer.get(account_id)
            
            alert = {
                "alert_id": next_alert_id,
                "transaction_id": transaction_id,
                "account_id": account_id,
                "customer_id": customer_id,
                "alert_timestamp": alert_date.strftime("%Y-%m-%d %H:%M:%S"),
                "detection_method": random.choice(DETECTION_METHODS),
                "fraud_reason": random.choice(FRAUD_REASONS),
                "fraud_type": random.choice(FRAUD_TYPES),
                "severity": severity,
                "severity_score": severity_score,
                "alert_status": random.choice(ALERT_STATUSES),
                "assigned_analyst_id": f"ANALYST_{random.randint(100, 999)}" if random.random() > 0.4 else None,
                "resolution_date": None,
                "financial_loss": round(amount * random.uniform(0, 0.8), 2) if random.random() > 0.5 else 0,
                "is_false_positive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Set resolution date if status is resolved
            if alert['alert_status'] in ['RESOLVED', 'FALSE_POSITIVE', 'CONFIRMED_FRAUD']:
                days_to_resolve = random.randint(1, 30)                
                try:
                    alert['resolution_date'] = (alert_date + timedelta(days=days_to_resolve)).strftime("%Y-%m-%d %H:%M:%S")
                except OverflowError:
                    alert['resolution_date'] = alert_date
            # Introduce bad data
            alert = self.introduce_bad_data_fraud(alert)
            if alert.get('is_bad_data'):
                bad_alert_count += 1
            
            self.fraud_alerts.append(alert)
            next_alert_id += 1
        
        print(f"Generated {len(self.fraud_alerts)} fraud alerts ({bad_alert_count} with bad data)")
        return self.fraud_alerts


def generate_fraud_alert(transaction_id, account_id, customer_id):
    """Compatibility shim: generate a single fraud alert for given transaction/account/customer."""
    transaction = {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "customer_id": customer_id,
        "amount": random.uniform(10, 20000)
    }
    # Force at least one alert for this shim by setting fraud_rate=1.0
    # Provide a minimal accounts mapping so customer_id can be resolved correctly
    accounts = [{"account_id": account_id, "customer_id": customer_id}]
    gen = FraudAlertGenerator(fraud_rate=1.0, transactions=[transaction], accounts=accounts)
    alerts = gen.generate()
    return alerts[0] if alerts else None