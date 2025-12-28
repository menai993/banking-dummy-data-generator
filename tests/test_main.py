"""Tests for main.py"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main


class TestMainFunctions:
    """Test main.py functions"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return {
            "customers": [
                {"customer_id": "C1", "name": "Alice", "is_bad_data": False},
                {"customer_id": "C2", "name": "Bob", "is_bad_data": True, "bad_data_type": "missing_data"},
                {"customer_id": "C3", "name": "Charlie", "is_bad_data": False}
            ],
            "accounts": [
                {"account_id": "A1", "customer_id": "C1", "balance": 1000, "is_bad_data": False},
                {"account_id": "A2", "customer_id": "C2", "balance": -500, "is_bad_data": True, "bad_data_type": "out_of_range"}
            ]
        }
    
    def test_calculate_statistics(self, sample_data, capsys):
        """Test calculate_statistics function"""
        main.calculate_statistics(sample_data)
        
        # Capture output
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that output contains expected information
        assert "BAD DATA STATISTICS" in output
        assert "customers" in output
        assert "accounts" in output
        assert "TOTAL" in output
    
    def test_generate_bad_data_report(self, sample_data, tmp_path):
        """Test generate_bad_data_report function"""
        import json
        
        output_dir = str(tmp_path)
        report_file = main.generate_bad_data_report(sample_data, output_dir)
        
        # Check that report file was created
        assert os.path.exists(report_file)
        
        # Load and verify report content
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Check report structure
        assert "generation_date" in report
        assert "configuration" in report
        assert "tables" in report
        
        # Check customers table stats
        assert "customers" in report["tables"]
        customer_stats = report["tables"]["customers"]
        assert customer_stats["total_records"] == 3
        assert customer_stats["bad_records"] == 1
        assert customer_stats["bad_percentage"] > 0
        
        # Check accounts table stats
        assert "accounts" in report["tables"]
        account_stats = report["tables"]["accounts"]
        assert account_stats["total_records"] == 2
        assert account_stats["bad_records"] == 1
    
    def test_empty_data_handling(self):
        """Test that functions handle empty data gracefully"""
        empty_data = {"customers": [], "accounts": []}
        
        # Should not raise an exception
        main.calculate_statistics(empty_data)
    
    def test_bad_data_examples_in_report(self, sample_data, tmp_path):
        """Test that report includes bad data examples"""
        import json
        
        output_dir = str(tmp_path)
        report_file = main.generate_bad_data_report(sample_data, output_dir)
        
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Check that examples are included
        customer_examples = report["tables"]["customers"]["examples"]
        assert len(customer_examples) > 0
        assert customer_examples[0]["is_bad_data"] is True
    
    def test_bad_by_type_in_report(self, sample_data, tmp_path):
        """Test that report includes breakdown by bad data type"""
        import json
        
        output_dir = str(tmp_path)
        report_file = main.generate_bad_data_report(sample_data, output_dir)
        
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Check bad_by_type structure
        customer_bad_types = report["tables"]["customers"]["bad_by_type"]
        assert "missing_data" in customer_bad_types
        assert customer_bad_types["missing_data"] == 1
        
        account_bad_types = report["tables"]["accounts"]["bad_by_type"]
        assert "out_of_range" in account_bad_types
        assert account_bad_types["out_of_range"] == 1
