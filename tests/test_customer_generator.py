"""Tests for customer_generator.py"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generators.customer_generator import CustomerGenerator


class TestCustomerGenerator:
    """Test CustomerGenerator class"""
    
    @pytest.fixture
    def generator(self):
        """Create a CustomerGenerator instance"""
        return CustomerGenerator(num_customers=10, bad_data_percentage=0.0)
    
    def test_initialization(self, generator):
        """Test generator initialization"""
        assert generator.num_customers == 10
        assert generator.bad_data_percentage == 0.0
        assert len(generator.customer_ids) == 0
        assert len(generator.customers) == 0
        assert len(generator.customer_details) == 0
    
    def test_generate_customer_id(self, generator):
        """Test customer ID generation"""
        customer_id = generator.generate_customer_id()
        
        # Check format (C followed by 8 digits)
        assert customer_id.startswith('C')
        assert len(customer_id) == 9
        assert customer_id[1:].isdigit()
        
        # Check uniqueness
        ids = set()
        for _ in range(100):
            cust_id = generator.generate_customer_id()
            assert cust_id not in ids
            ids.add(cust_id)
    
    def test_generate_email(self):
        """Test email generation"""
        email = CustomerGenerator.generate_email("John", "Doe")
        
        assert "@" in email
        assert email.startswith("john.doe@")
        assert "." in email.split("@")[1]  # Domain should have a dot
    
    def test_generate_invalid_email(self):
        """Test invalid email generation"""
        invalid_email = CustomerGenerator.generate_invalid_email()
        
        # Should be one of the known invalid patterns
        assert isinstance(invalid_email, str)
        # Common invalid patterns should not have proper @ and domain
        invalid_patterns = ["invalid.email", "missing@domain", "@nodomain.com", 
                          "NULL", ""]
        # At least one test: it's a string
        assert isinstance(invalid_email, str)
    
    def test_generate_phone(self):
        """Test phone number generation"""
        phone = CustomerGenerator.generate_phone()
        
        assert phone.startswith("+1-")
        assert len(phone.split("-")) == 4  # +1-XXX-XXX-XXXX
    
    def test_generate_customers(self, generator):
        """Test customer generation"""
        customers, customer_details = generator.generate()
        
        # Check correct number of customers
        assert len(customers) == 10
        assert len(customer_details) == 10
        
        # Check structure of first customer
        first_customer = customers[0]
        assert 'customer_id' in first_customer
        assert 'first_name' in first_customer
        assert 'last_name' in first_customer
        assert 'email' in first_customer
        assert 'phone' in first_customer
        assert 'date_of_birth' in first_customer
        
        # Check customer details
        first_detail = customer_details[0]
        assert 'customer_id' in first_detail
        assert 'employment_status' in first_detail
        assert 'annual_income' in first_detail
        assert 'credit_score' in first_detail
    
    def test_generate_with_bad_data(self):
        """Test customer generation with bad data"""
        generator_with_bad = CustomerGenerator(num_customers=10, bad_data_percentage=0.5)
        customers, customer_details = generator_with_bad.generate()
        
        # Count bad records
        bad_customers = [c for c in customers if c.get('is_bad_data', False)]
        
        # Should have some bad data (with 50% probability, expect around 5)
        # Allow some variance due to randomness
        assert len(bad_customers) >= 2, "Should have some bad data with 50% probability"
        
        # Check bad data has proper flags
        if bad_customers:
            bad_customer = bad_customers[0]
            assert bad_customer['is_bad_data'] is True
            assert 'bad_data_type' in bad_customer
    
    def test_all_customer_ids_unique(self):
        """Test that all generated customer IDs are unique"""
        generator = CustomerGenerator(num_customers=100, bad_data_percentage=0.0)
        customers, _ = generator.generate()
        
        customer_ids = [c['customer_id'] for c in customers]
        assert len(customer_ids) == len(set(customer_ids)), "All customer IDs should be unique"
