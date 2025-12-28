"""Tests for config.py"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


class TestConfig:
    """Test configuration settings"""
    
    def test_config_exists(self):
        """Test that CONFIG dictionary exists"""
        assert hasattr(config, 'CONFIG')
        assert isinstance(config.CONFIG, dict)
    
    def test_volume_controls_exist(self):
        """Test that volume controls are defined"""
        assert 'num_customers' in config.CONFIG
        assert 'num_branches' in config.CONFIG
        assert 'num_employees' in config.CONFIG
        assert 'num_merchants' in config.CONFIG
        assert isinstance(config.CONFIG['num_customers'], int)
        assert config.CONFIG['num_customers'] > 0
    
    def test_relationship_controls_exist(self):
        """Test that relationship controls are defined"""
        assert 'accounts_per_customer_min' in config.CONFIG
        assert 'accounts_per_customer_max' in config.CONFIG
        assert 'cards_per_customer_min' in config.CONFIG
        assert 'cards_per_customer_max' in config.CONFIG
        assert config.CONFIG['accounts_per_customer_min'] <= config.CONFIG['accounts_per_customer_max']
    
    def test_output_configuration(self):
        """Test output configuration settings"""
        assert 'output_formats' in config.CONFIG
        assert 'output_directory' in config.CONFIG
        assert isinstance(config.CONFIG['output_formats'], list)
        assert len(config.CONFIG['output_formats']) > 0
    
    def test_bad_data_percentage(self):
        """Test bad data percentage configuration"""
        assert 'bad_data_percentage' in config.CONFIG
        assert isinstance(config.CONFIG['bad_data_percentage'], dict)
        
        # Check that percentages are valid (between 0 and 1)
        for table, percentage in config.CONFIG['bad_data_percentage'].items():
            assert 0 <= percentage <= 1, f"Invalid percentage for {table}: {percentage}"
    
    def test_bad_data_types(self):
        """Test bad data types configuration"""
        assert 'bad_data_types' in config.CONFIG
        assert isinstance(config.CONFIG['bad_data_types'], dict)
        
        expected_types = ['missing_data', 'invalid_format', 'out_of_range', 
                         'inconsistent_data', 'duplicate_data', 'malformed_data']
        for data_type in expected_types:
            assert data_type in config.CONFIG['bad_data_types']
            assert isinstance(config.CONFIG['bad_data_types'][data_type], bool)
    
    def test_mssql_import_config(self):
        """Test MSSQL import configuration"""
        assert 'mssql_import' in config.CONFIG
        assert isinstance(config.CONFIG['mssql_import'], dict)
        
        required_keys = ['server', 'database', 'username', 'password', 
                        'data_directory', 'enable_quality_tracking']
        for key in required_keys:
            assert key in config.CONFIG['mssql_import']
