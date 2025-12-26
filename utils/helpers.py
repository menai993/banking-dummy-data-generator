import os
import random
import re
from datetime import datetime
from pathlib import Path
import pandas as pd

class DataExporter:
    @staticmethod
    def log_to_txt(text, output_dir="output"):
        DataExporter._ensure_dir(output_dir)
        filepath = Path(output_dir) / "import_errors.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with filepath.open("a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n\n")

    @staticmethod
    def export_to_csv(data, filename, output_dir="output"):
        """Export data to CSV file with UTF-8 encoding"""
        DataExporter._ensure_dir(output_dir)
        filepath = Path(output_dir) / filename

        df = pd.DataFrame(data)

        # Drop helper columns in CSV export view if present
        df = DataExporter._drop_bad_columns(df)

        try:
            # Write using Path.open ensures we can control encoding consistently
            with filepath.open("w", encoding="utf-8", errors="replace") as f:
                df.to_csv(f, index=False)
        except Exception:
            # Fallback: let pandas handle defaults
            df.to_csv(filepath, index=False)

        print(f"Exported {len(data)} records to {filepath}")

        # Export metadata about bad data if any
        bad_data_count = DataExporter._count_bad_data(data)
        if bad_data_count > 0:
            metadata = {
                "total_records": len(data),
                "bad_data_count": bad_data_count,
                "bad_data_percentage": round(bad_data_count / len(data) * 100, 2),
                "export_timestamp": datetime.now().isoformat(),
                "file_name": filename,
            }

            metadata_file = Path(output_dir) / f"{filename}_metadata.json"
            pd.DataFrame([metadata]).to_json(metadata_file, indent=2, force_ascii=False)
            print(f"Metadata exported to {metadata_file}")

        return str(filepath)
    
    @staticmethod
    def export_to_sql_files(data_dict, output_dir="output/sql"):
        """Generate SQL INSERT statements for each table with UTF-8 encoding"""
        DataExporter._ensure_dir(output_dir)

        sql_files = {}
        for table_name, data in data_dict.items():
            if not data:
                continue

            filename = f"{table_name}.sql"
            filepath = Path(output_dir) / filename

            # Determine consistent columns: start with first record keys then add any missing keys
            bad_cols = {'is_bad_data', 'bad_data_type'}
            first_keys = [k for k in data[0].keys() if k not in bad_cols]
            # collect additional keys in deterministic order
            extras = []
            for rec in data:
                for k in rec.keys():
                    if k in bad_cols or k in first_keys or k in extras:
                        continue
                    extras.append(k)
            columns = first_keys + extras

            bad_data_count = sum(1 for record in data if record.get('is_bad_data', False))

            with filepath.open('w', encoding='utf-8', errors='replace') as f:
                f.write(f"-- INSERT statements for {table_name}\n")
                f.write(f"-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Total records: {len(data)}, Bad data: {bad_data_count} ({round(bad_data_count/len(data)*100, 2)}%)\n\n")

                col_sql = ', '.join(columns)
                for record in data:
                    values = ', '.join(DataExporter._format_sql_value(record.get(c)) for c in columns)
                    f.write(f"INSERT INTO {table_name} ({col_sql}) VALUES ({values});\n")

            sql_files[table_name] = str(filepath)
            print(f"Generated SQL file: {filepath} with {len(data)} INSERT statements ({bad_data_count} bad records)")

        return sql_files
    
    @staticmethod
    def _sanitize_excel_sheet_name(name):
        """Sanitize sheet name for Excel compatibility"""
        if not name:
            return "Sheet"
        
        # Remove invalid characters
        # Excel doesn't allow: : \ / ? * [ ]
        invalid_chars = r'[:\\/*?\[\]]'
        sanitized = re.sub(invalid_chars, '', str(name))
        
        # Remove leading/trailing apostrophes and spaces
        sanitized = sanitized.strip().strip("'")
        
        # Truncate to 31 characters (Excel limit)
        if len(sanitized) > 31:
            sanitized = sanitized[:31]
        
        # Ensure not empty
        if not sanitized:
            sanitized = "Data"
        
        # Cannot start or end with apostrophe
        while sanitized.startswith("'"):
            sanitized = sanitized[1:]
        while sanitized.endswith("'"):
            sanitized = sanitized[:-1]
        
        return sanitized

    @staticmethod
    def _ensure_dir(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _drop_bad_columns(df: pd.DataFrame) -> pd.DataFrame:
        cols = [c for c in df.columns if c not in {'is_bad_data', 'bad_data_type'}]
        return df[cols]

    @staticmethod
    def _count_bad_data(data) -> int:
        return sum(1 for record in data if record.get('is_bad_data', False))

    @staticmethod
    def _format_sql_value(value):
        if value is None:
            return 'NULL'
        if isinstance(value, bool):
            return '1' if value else '0'
        if isinstance(value, (int, float)):
            return str(value)
        # escape single quotes
        s = str(value).replace("'", "''")
        return f"'{s}'"
    
    @staticmethod
    def export_to_excel(data_dict, filename="banking_data.xlsx", output_dir="output"):
        """Export all data to Excel with multiple sheets - ROBUST VERSION"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            
            print(f"\nExporting to Excel file: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                sheet_number = 1
                sheets_created = []
                
                for original_sheet_name, data in data_dict.items():
                    if not data:
                        continue
                    
                    # Create DataFrame
                    df = pd.DataFrame(data)
                    
                    # Remove bad data indicator columns for cleaner Excel view
                    columns_to_drop = []
                    if 'is_bad_data' in df.columns:
                        columns_to_drop.append('is_bad_data')
                    if 'bad_data_type' in df.columns:
                        columns_to_drop.append('bad_data_type')
                    
                    if columns_to_drop:
                        df = df.drop(columns=columns_to_drop)
                    
                    # Generate safe sheet name
                    safe_name = DataExporter._sanitize_excel_sheet_name(original_sheet_name)
                    
                    # Ensure unique sheet name
                    base_name = safe_name
                    counter = 1
                    while base_name in writer.sheets or base_name in sheets_created:
                        if len(safe_name) > 27:
                            base_name = f"{safe_name[:27]}_{counter}"
                        else:
                            base_name = f"{safe_name}_{counter}"
                        counter += 1
                        if counter > 99:
                            base_name = f"Sheet_{sheet_number}"
                            break
                    
                    # Write to Excel
                    try:
                        df.to_excel(writer, sheet_name=base_name, index=False)
                        sheets_created.append(base_name)
                        print(f"  Created sheet: {base_name} (from '{original_sheet_name}') with {len(data)} records")
                        sheet_number += 1
                    except Exception as e:
                        print(f"    Warning: Could not write sheet '{base_name}': {e}")
                        # Try with a simple sheet name
                        simple_name = f"Sheet_{sheet_number}"
                        df.to_excel(writer, sheet_name=simple_name, index=False)
                        sheets_created.append(simple_name)
                        sheet_number += 1
                
                # Create mapping sheet
                mapping_data = []
                for i, (original_name, data) in enumerate(data_dict.items(), 1):
                    if data and i-1 < len(sheets_created):
                        mapping_data.append({
                            "Excel Sheet": sheets_created[i-1],
                            "Original Table": original_name,
                            "Records": len(data)
                        })
                
                if mapping_data:
                    mapping_df = pd.DataFrame(mapping_data)
                    mapping_df.to_excel(writer, sheet_name="Sheet_Map", index=False)
                    print("  Created mapping sheet")
            
            print(f"✅ Excel export completed: {filepath}")
            print(f"   Total sheets created: {len(sheets_created)} + 1 mapping sheet")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            import traceback
            traceback.print_exc()
            # Try alternative approach
            return DataExporter._export_to_excel_fallback(data_dict, filename, output_dir)
    
    @staticmethod
    def _export_to_excel_fallback(data_dict, filename="banking_data.xlsx", output_dir="output"):
        """Fallback method for Excel export if main method fails"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            
            # Export each table as separate CSV first
            csv_files = []
            for sheet_name, data in data_dict.items():
                if data:
                    csv_file = os.path.join(output_dir, f"{sheet_name}.csv")
                    df = pd.DataFrame(data)
                    
                    # Remove bad data indicator columns
                    columns_to_drop = []
                    if 'is_bad_data' in df.columns:
                        columns_to_drop.append('is_bad_data')
                    if 'bad_data_type' in df.columns:
                        columns_to_drop.append('bad_data_type')
                    
                    if columns_to_drop:
                        df = df.drop(columns=columns_to_drop)
                    
                    df.to_csv(csv_file, index=False, encoding='utf-8')
                    csv_files.append((sheet_name, csv_file))
            
            print(f"Exported {len(csv_files)} tables as CSV files")
            print(f"Note: Excel export failed, check the CSV files in {output_dir}")
            return csv_files
            
        except Exception as e:
            print(f"Fallback export also failed: {e}")
            return None


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
        """Add malformed characters or SQL injection patterns (safer version)"""
        sql_injection_patterns = [
            " OR 1=1",
            "-- COMMENT",
            "/* COMMENT */",
            "null",
            "very_long_string_" + "x" * 50,
            "<test>",
            "[test]"
        ]
        
        if field in record and record[field] is not None:
            # Use safer patterns to avoid encoding issues
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