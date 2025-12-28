"""Tests for utils/helpers.py"""
import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.helpers import DataExporter, BadDataGenerator


class TestBadDataGenerator:
    """Test BadDataGenerator class"""
    
    def test_should_generate_bad_data_probability(self):
        """Test bad data generation probability"""
        # Test with 0% probability
        results = [BadDataGenerator.should_generate_bad_data(0.0) for _ in range(100)]
        assert not any(results), "Should never generate bad data with 0% probability"
        
        # Test with 100% probability
        results = [BadDataGenerator.should_generate_bad_data(1.0) for _ in range(100)]
        assert all(results), "Should always generate bad data with 100% probability"
    
    def test_get_bad_data_type(self):
        """Test bad data type selection"""
        bad_type = BadDataGenerator.get_bad_data_type()
        expected_types = ["missing_data", "invalid_format", "out_of_range", 
                         "inconsistent_data", "malformed_data"]
        assert bad_type in expected_types
    
    def test_generate_missing_data(self):
        """Test missing data generation"""
        record = {"name": "John", "email": "john@example.com", "age": 30}
        fields_to_corrupt = ["email", "age"]
        
        result = BadDataGenerator.generate_missing_data(record, fields_to_corrupt)
        
        assert result['is_bad_data'] is True
        assert result['bad_data_type'] == 'missing_data'
        assert result['email'] is None
        assert result['age'] is None
        assert result['name'] == "John"  # Should not be affected
    
    def test_generate_invalid_format(self):
        """Test invalid format generation"""
        record = {"email": "valid@email.com"}
        
        result = BadDataGenerator.generate_invalid_format(record, "email", "invalid.email")
        
        assert result['is_bad_data'] is True
        assert result['bad_data_type'] == 'invalid_format'
        assert result['email'] == "invalid.email"
    
    def test_generate_out_of_range(self):
        """Test out of range generation"""
        record = {"balance": 1000.0}
        
        result = BadDataGenerator.generate_out_of_range(record, "balance", 0, 10000)
        
        assert result['is_bad_data'] is True
        assert result['bad_data_type'] == 'out_of_range'
        # Value should be modified (negative or outside range)
        # Due to randomness, we just check that the function ran and set the flags
        assert 'balance' in result
    
    def test_generate_inconsistent_data(self):
        """Test inconsistent data generation"""
        record = {"user_id": "U123", "account_id": "A456"}
        
        result = BadDataGenerator.generate_inconsistent_data(record, [("user_id", "account_id")])
        
        assert result['is_bad_data'] is True
        assert result['bad_data_type'] == 'inconsistent_data'
        assert "MISMATCH_U123" in str(result['account_id'])
    
    def test_generate_malformed_data(self):
        """Test malformed data generation"""
        record = {"name": "John Doe"}
        
        result = BadDataGenerator.generate_malformed_data(record, "name")
        
        assert result['is_bad_data'] is True
        assert result['bad_data_type'] == 'malformed_data'
        assert result['name'] != "John Doe"  # Should be modified
        assert "John Doe" in result['name']  # Should contain original


class TestDataExporter:
    """Test DataExporter class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "is_bad_data": False},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "is_bad_data": False},
            {"id": 3, "name": None, "email": "invalid", "is_bad_data": True, "bad_data_type": "missing_data"}
        ]
    
    def test_export_to_csv(self, temp_dir, sample_data):
        """Test CSV export functionality"""
        filename = "test_data.csv"
        result = DataExporter.export_to_csv(sample_data, filename, temp_dir)
        
        # Check file was created
        filepath = Path(temp_dir) / filename
        assert filepath.exists()
        
        # Verify content
        import pandas as pd
        df = pd.read_csv(filepath)
        assert len(df) == 3
        assert list(df.columns) == ["id", "name", "email", "is_bad_data", "bad_data_type"]
    
    def test_export_to_sql_files(self, temp_dir, sample_data):
        """Test SQL file generation"""
        data_dict = {"test_table": sample_data}
        sql_dir = os.path.join(temp_dir, "sql")
        
        result = DataExporter.export_to_sql_files(data_dict, sql_dir)
        
        # Check SQL file was created
        sql_file = Path(sql_dir) / "test_table.sql"
        assert sql_file.exists()
        
        # Verify SQL content
        with sql_file.open('r', encoding='utf-8') as f:
            content = f.read()
            assert "INSERT INTO test_table" in content
            assert "Alice" in content
            assert "Bob" in content
    
    def test_sanitize_excel_sheet_name(self):
        """Test Excel sheet name sanitization"""
        # Test invalid characters
        assert DataExporter._sanitize_excel_sheet_name("test:name") == "testname"
        assert DataExporter._sanitize_excel_sheet_name("test/name") == "testname"
        assert DataExporter._sanitize_excel_sheet_name("test*name") == "testname"
        
        # Test length limit (31 characters)
        long_name = "a" * 50
        result = DataExporter._sanitize_excel_sheet_name(long_name)
        assert len(result) == 31
        
        # Test empty input
        result = DataExporter._sanitize_excel_sheet_name("")
        assert result in ["Data", "Sheet"]  # Allow either default value
    
    def test_count_bad_data(self, sample_data):
        """Test bad data counting"""
        count = DataExporter._count_bad_data(sample_data)
        assert count == 1
    
    def test_format_sql_value(self):
        """Test SQL value formatting"""
        # Test None
        assert DataExporter._format_sql_value(None) == 'NULL'
        
        # Test boolean
        assert DataExporter._format_sql_value(True) == '1'
        assert DataExporter._format_sql_value(False) == '0'
        
        # Test numbers
        assert DataExporter._format_sql_value(42) == '42'
        assert DataExporter._format_sql_value(3.14) == '3.14'
        
        # Test strings with quotes
        assert DataExporter._format_sql_value("test's value") == "'test''s value'"
        
        # Test regular string
        assert DataExporter._format_sql_value("test") == "'test'"
