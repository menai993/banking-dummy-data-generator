import pandas as pd
import os
import random
from datetime import datetime

class DataExporter:
    @staticmethod
    def export_to_csv(data, filename, output_dir="output"):
        """Export data to CSV file"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        print(f"Exported {len(data)} records to {filepath}")
        
        # Also export a metadata file about bad data
        bad_data_count = sum(1 for record in data if record.get('is_bad_data', False))
        if bad_data_count > 0:
            metadata = {
                "total_records": len(data),
                "bad_data_count": bad_data_count,
                "bad_data_percentage": round(bad_data_count / len(data) * 100, 2),
                "export_timestamp": datetime.now().isoformat(),
                "file_name": filename
            }
            
            metadata_file = os.path.join(output_dir, f"{filename}_metadata.json")
            pd.DataFrame([metadata]).to_json(metadata_file, indent=2)
            print(f"Metadata exported to {metadata_file}")
        
        return filepath
    
    @staticmethod
    def export_to_sql_files(data_dict, output_dir="output/sql"):
        """Generate SQL INSERT statements for each table"""
        os.makedirs(output_dir, exist_ok=True)
        
        sql_files = {}
        for table_name, data in data_dict.items():
            if not data:
                continue
            
            filename = f"{table_name}.sql"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"-- INSERT statements for {table_name}\n")
                f.write(f"-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Count bad data
                bad_data_count = sum(1 for record in data if record.get('is_bad_data', False))
                f.write(f"-- Total records: {len(data)}, Bad data: {bad_data_count} ({round(bad_data_count/len(data)*100, 2)}%)\n\n")
                
                for record in data:
                    columns = ', '.join([col for col in record.keys() if col != 'is_bad_data'])
                    values = ', '.join([f"'{str(v).replace("'", "''")}'" if v is not None else 'NULL' for k, v in record.items() if k != 'is_bad_data'])
                    f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n")
            
            sql_files[table_name] = filepath
            print(f"Generated SQL file: {filepath} with {len(data)} INSERT statements ({bad_data_count} bad records)")
        
        return sql_files

class BadDataGenerator:
    """Helper class for generating bad data"""
    
    @staticmethod
    def should_generate_bad_data(bad_data_percentage):
        """Determine if we should generate bad data for this record"""
        return random.random() < bad_data_percentage
    
    @staticmethod
    def get_bad_data_type():
        """Randomly select a type of bad data to generate"""
        types = [
            "missing_data",
            "invalid_format", 
            "out_of_range",
            "inconsistent_data",
            "malformed_data"
        ]
        return random.choice(types)
    
    @staticmethod
    def generate_missing_data(record, fields_to_corrupt):
        """Set specified fields to None"""
        for field in fields_to_corrupt:
            if field in record:
                record[field] = None
        record['is_bad_data'] = True
        record['bad_data_type'] = 'missing_data'
        return record
    
    @staticmethod
    def generate_invalid_format(record, field, invalid_value):
        """Set field to invalid format"""
        if field in record:
            record[field] = invalid_value
        record['is_bad_data'] = True
        record['bad_data_type'] = 'invalid_format'
        return record
    
    @staticmethod
    def generate_out_of_range(record, field, min_val=None, max_val=None):
        """Set field value out of valid range"""
        if field in record:
            if min_val is not None and max_val is not None:
                # Generate value outside the range
                if random.choice([True, False]):
                    record[field] = min_val - abs(min_val) * random.uniform(0.1, 2)
                else:
                    record[field] = max_val + abs(max_val) * random.uniform(0.1, 2)
            elif isinstance(record[field], (int, float)):
                record[field] = record[field] * random.uniform(-2, -0.1)  # Negative value
        record['is_bad_data'] = True
        record['bad_data_type'] = 'out_of_range'
        return record
    
    @staticmethod
    def generate_inconsistent_data(record, field_pairs):
        """Create inconsistency between related fields"""
        for field1, field2 in field_pairs:
            if field1 in record and field2 in record:
                # Make fields inconsistent
                record[field2] = f"MISMATCH_{record[field1]}"
        record['is_bad_data'] = True
        record['bad_data_type'] = 'inconsistent_data'
        return record
    
    @staticmethod
    def generate_malformed_data(record, field):
        """Add malformed characters or SQL injection patterns"""
        sql_injection_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "null\x00",
            "very_long_string_" + "x" * 1000
        ]
        
        if field in record and record[field] is not None:
            pattern = random.choice(sql_injection_patterns)
            record[field] = f"{record[field]}{pattern}"
        record['is_bad_data'] = True
        record['bad_data_type'] = 'malformed_data'
        return record
    
    @staticmethod
    def generate_duplicate_data(record, fields_to_duplicate):
        """Duplicate values in different fields"""
        for field1, field2 in fields_to_duplicate:
            if field1 in record and field2 in record:
                record[field2] = record[field1]
        record['is_bad_data'] = True
        record['bad_data_type'] = 'duplicate_data'
        return record