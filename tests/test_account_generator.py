"""Tests for account_generator.py"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generators.account_generator import AccountGenerator


class TestAccountGenerator:
    """Test AccountGenerator class"""
    
    @pytest.fixture
    def sample_customers(self):
        """Create sample customers for testing"""
        from datetime import datetime
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return [
            {"customer_id": "C12345678", "first_name": "John", "last_name": "Doe", "created_at": created_at},
            {"customer_id": "C23456789", "first_name": "Jane", "last_name": "Smith", "created_at": created_at},
            {"customer_id": "C34567890", "first_name": "Bob", "last_name": "Johnson", "created_at": created_at}
        ]
    
    @pytest.fixture
    def generator(self, sample_customers):
        """Create an AccountGenerator instance"""
        return AccountGenerator(customers_data=sample_customers, bad_data_percentage=0.0)
    
    def test_initialization(self, generator, sample_customers):
        """Test generator initialization"""
        assert generator.customers == sample_customers
        assert generator.bad_data_percentage == 0.0
        assert len(generator.account_ids) == 0
    
    def test_generate_account_id(self, generator):
        """Test account ID generation"""
        account_id = generator.generate_account_id()
        
        # Check format (ACC followed by 7 digits)
        assert account_id.startswith('ACC')
        assert len(account_id) == 10
        assert account_id[3:].isdigit()
        
        # Check uniqueness
        ids = set()
        for _ in range(100):
            acc_id = generator.generate_account_id()
            assert acc_id not in ids
            ids.add(acc_id)
    
    def test_generate_accounts(self, generator):
        """Test account generation"""
        accounts = generator.generate(accounts_per_customer_min=1, accounts_per_customer_max=2)
        
        # Should generate at least 3 accounts (1 per customer minimum)
        assert len(accounts) >= 3
        
        # Check structure of first account
        first_account = accounts[0]
        assert 'account_id' in first_account
        assert 'customer_id' in first_account
        assert 'account_type' in first_account
        assert 'balance' in first_account
        assert 'currency' in first_account
        
        # Check that balance is a number
        assert isinstance(first_account['balance'], (int, float))
    
    def test_accounts_per_customer_range(self, sample_customers):
        """Test that accounts per customer are within range"""
        generator = AccountGenerator(customers_data=sample_customers, bad_data_percentage=0.0)
        accounts = generator.generate(accounts_per_customer_min=2, accounts_per_customer_max=3)
        
        # Count accounts per customer
        customer_account_counts = {}
        for account in accounts:
            cust_id = account['customer_id']
            customer_account_counts[cust_id] = customer_account_counts.get(cust_id, 0) + 1
        
        # Each customer should have between 2 and 3 accounts
        for count in customer_account_counts.values():
            assert 2 <= count <= 3
    
    def test_generate_with_bad_data(self, sample_customers):
        """Test account generation with bad data"""
        generator = AccountGenerator(customers_data=sample_customers, bad_data_percentage=0.5)
        accounts = generator.generate(accounts_per_customer_min=1, accounts_per_customer_max=2)
        
        # Count bad records
        bad_accounts = [a for a in accounts if a.get('is_bad_data', False)]
        
        # Should have some bad data with 50% probability
        assert len(bad_accounts) >= 1
        
        # Check bad data has proper flags
        if bad_accounts:
            bad_account = bad_accounts[0]
            assert bad_account['is_bad_data'] is True
            assert 'bad_data_type' in bad_account
    
    def test_all_account_ids_unique(self, sample_customers):
        """Test that all generated account IDs are unique"""
        generator = AccountGenerator(customers_data=sample_customers, bad_data_percentage=0.0)
        accounts = generator.generate(accounts_per_customer_min=3, accounts_per_customer_max=5)
        
        account_ids = [a['account_id'] for a in accounts]
        assert len(account_ids) == len(set(account_ids)), "All account IDs should be unique"
    
    def test_customer_ids_match(self, sample_customers):
        """Test that all accounts belong to valid customers"""
        generator = AccountGenerator(customers_data=sample_customers, bad_data_percentage=0.0)
        accounts = generator.generate(accounts_per_customer_min=1, accounts_per_customer_max=2)
        
        valid_customer_ids = {c['customer_id'] for c in sample_customers}
        
        for account in accounts:
            # Skip bad data records which might have intentionally invalid customer_ids
            if not account.get('is_bad_data', False):
                assert account['customer_id'] in valid_customer_ids
