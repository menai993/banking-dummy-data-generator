# Streamlit Web UI - User Guide

## Overview

The Banking Data Generator now includes a user-friendly web interface built with Streamlit. This interface provides easy access to all features without needing to run Python scripts from the command line.

## Features

The web UI provides access to four main features:

1. **📊 Data Generation** - Generate realistic banking data with configurable settings
2. **📥 MSSQL Import** - Import generated data into Microsoft SQL Server
3. **🔄 CDC Management** - Enable/Disable Change Data Capture on database and tables
4. **⚡ CDC Simulation** - Simulate real-time data changes for CDC testing

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- streamlit>=1.28.0
- pandas>=1.5.0
- pyodbc>=4.0.0
- openpyxl>=3.0.0

## Running the Web UI

### Start the Application

From the project root directory, run:

```bash
streamlit run app.py
```

The application will start and automatically open in your default web browser at `http://localhost:8501`.

### Alternative: Specify Port

To run on a different port:

```bash
streamlit run app.py --server.port 8502
```

## Using the Web UI

### Navigation

Use the sidebar menu on the left to navigate between different pages:
- 🏠 Home
- 📊 Data Generation
- 📥 MSSQL Import
- 🔄 CDC Management
- ⚡ CDC Simulation

### 1. Home Page

The home page provides:
- Overview of all features
- Current configuration summary
- Quick reference guide

### 2. Data Generation Page

#### Volume Settings Tab
Configure the amount of data to generate:
- **Number of Customers** (10-100,000)
- **Number of Branches** (1-1,000)
- **Number of Employees** (1-10,000)
- **Number of Merchants** (1-10,000)
- **Accounts per Customer** (min/max)
- **Transactions per Account** (min/max)

#### Bad Data Settings Tab
Configure the percentage of bad data for each entity type:
- Customers, Accounts, Cards, Transactions
- Branches, Employees, Merchants
- Loans, Loan Payments, Audit Logs
- Exchange Rates, Investment Accounts
- Fraud Alerts, User Logins

Use sliders to set percentages from 0.0 to 1.0 (0% to 100%).

#### Output Settings Tab
Configure output options:
- **Output Formats**: Select CSV, SQL, and/or Excel
- **Output Directory**: Specify where files should be saved (default: "output")

#### Generate Data
Click the **🚀 Generate Data** button to start generation. The UI will show:
- Progress bar with current step
- Generation statistics table
- List of generated files
- Execution time

### 3. MSSQL Import Page

#### Database Configuration
Enter your SQL Server connection details:
- **Server**: SQL Server hostname or IP (e.g., "localhost")
- **Database**: Database name
- **Username**: SQL Server login username
- **Password**: SQL Server password (hidden input)
- **Data Directory**: Location of CSV files to import
- **Batch Size**: Number of rows per batch (default: 1000)
- **Create Database Views**: Option to create analysis views

#### Actions

**🔌 Test Connection**
- Test database connectivity before proceeding
- Validates credentials and server availability

**🏗️ Create Tables**
- Creates all required database tables
- Includes data quality tracking columns
- Drops existing tables if present (use with caution!)

**📥 Import Data**
- Imports all CSV files from the data directory
- Shows progress for each table
- Displays import statistics including:
  - Total rows imported
  - Error count
  - Bad records count
  - Import percentage

### 4. CDC Management Page

#### Database Configuration
Enter connection details (similar to MSSQL Import).

#### Check CDC Status
Click **🔍 Check CDC Status** to view:
- Whether CDC is enabled on the database
- List of tables with CDC enabled
- Current CDC configuration

#### Enable/Disable CDC

**✅ Enable CDC**
- Enables CDC on the database
- Enables CDC on all defined tables
- Creates CDC infrastructure

**❌ Disable CDC**
- Disables CDC on all tables
- Disables CDC on the database
- Removes CDC infrastructure

### 5. CDC Simulation Page

#### Database Configuration
Enter connection details for the target database.

#### Simulation Settings

**Number of Operations**
- Specify how many operations to simulate (1-1,000)
- Each operation is a random INSERT, UPDATE, or DELETE

**Operation Weights**
Configure the probability of each operation type:
- **INSERT_CUSTOMER** - Add new customer
- **UPDATE_CUSTOMER** - Update customer contact info
- **INSERT_ACCOUNT** - Create new account
- **UPDATE_ACCOUNT** - Modify account balance
- **INSERT_TRANSACTION** - Add transaction
- **UPDATE_TRANSACTION** - Change transaction status
- **INSERT_CARD** - Issue new card
- **UPDATE_CARD** - Update card status
- **INSERT_LOAN** - Create loan
- **UPDATE_LOAN** - Update loan status
- **INSERT_FRAUD_ALERT** - Generate fraud alert
- **INSERT_LOGIN** - Record user login

#### Run Simulation
Click **⚡ Run Simulation** to:
- Execute the specified number of operations
- Show real-time operation log
- Display success/failure statistics
- Track operation types executed

## Configuration File

The application uses `config.py` for default settings. You can modify this file to change:
- Default volume settings
- Bad data percentages
- MSSQL connection details
- Simulator operation weights

Example configuration:

```python
CONFIG = {
    "num_customers": 1000,
    "num_branches": 50,
    "output_formats": ["csv", "sql"],
    "bad_data_percentage": {
        "customers": 0.20,
        "accounts": 0.15,
        # ... more settings
    },
    "mssql_import": {
        "server": "localhost",
        "database": "YourDatabase",
        "username": "YourUsername",
        "password": "YourPassword",
        # ... more settings
    }
}
```

## Tips and Best Practices

### Data Generation
1. Start with smaller volumes (e.g., 100 customers) to test your configuration
2. Increase bad data percentages for more comprehensive quality testing
3. Use CSV format for quick inspection, SQL for direct import
4. Check the generated `bad_data_report.json` for quality insights

### MSSQL Import
1. Always test the connection first
2. Backup existing database before dropping tables
3. Adjust batch size based on your SQL Server performance
4. Check `import_errors.txt` for any import issues
5. Large datasets may take several minutes to import

### CDC Management
1. Ensure you have appropriate SQL Server permissions (db_owner role)
2. CDC requires SQL Server Agent to be running
3. Check CDC status after enabling to verify success
4. Disable CDC before dropping tables to avoid issues

### CDC Simulation
1. Import data before running simulation (needs existing records)
2. Start with fewer operations (20-50) to observe behavior
3. Monitor database size - CDC tracking tables grow over time
4. Use varied operation weights to simulate realistic patterns

## Troubleshooting

### Common Issues

**"Module not found" Error**
```bash
pip install -r requirements.txt
```

**Cannot Connect to Database**
- Verify SQL Server is running
- Check connection details (server, database, credentials)
- Ensure ODBC Driver 17 for SQL Server is installed
- Check firewall settings

**CDC Enable Fails**
- Verify you have db_owner permissions
- Ensure SQL Server Agent is running
- Check that the database exists
- Restart SQL Server if needed

**Import Errors**
- Check CSV file format and encoding (UTF-8)
- Verify foreign key relationships in data
- Check disk space on SQL Server
- Review `import_errors.txt` for specific errors

**Slow Performance**
- Reduce batch size for imports
- Decrease number of customers/transactions
- Close other applications using resources
- Check SQL Server resource utilization

## Advanced Usage

### Customizing the UI

You can modify `app.py` to:
- Add custom themes or styling
- Include additional metrics or visualizations
- Add new data generation options
- Implement custom validation rules

### Automation

Use Streamlit's session state to:
- Save favorite configurations
- Create preset profiles
- Implement workflow automation
- Track historical runs

### Integration

The UI can be integrated with:
- CI/CD pipelines for automated testing
- Data quality monitoring systems
- ETL processes
- Database migration workflows

## Support

For issues or questions:
1. Check this README
2. Review the main project README.md
3. Check the code comments in `app.py`
4. Open an issue on GitHub

## License

This web UI is part of the Banking Dummy Data Generator project and follows the same license terms.
