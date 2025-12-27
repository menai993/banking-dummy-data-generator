import pyodbc
import os
import importlib.util
import config
from typing import List, Optional


# -------------------------------------------------------
# Load CREATE_STATEMENTS dynamically
# -------------------------------------------------------
_cs_path = os.path.join(os.path.dirname(__file__), "config", "create_statements.py")
if os.path.exists(_cs_path):
    spec = importlib.util.spec_from_file_location("create_statements_module", _cs_path)
    _cs_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_cs_mod)
    CREATE_STATEMENTS = getattr(_cs_mod, "CREATE_STATEMENTS", {})
else:
    CREATE_STATEMENTS = {}


# -------------------------------------------------------
# Connection helpers
# -------------------------------------------------------
def get_connection() -> pyodbc.Connection:
    cfg = config.CONFIG.get("mssql_import")
    if not cfg:
        raise ValueError("Missing CONFIG['mssql_import'] in config.py")

    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={cfg['server']};"
        f"Database={cfg['database']};"
        f"Uid={cfg['username']};"
        f"Pwd={cfg['password']}"
    )
    return pyodbc.connect(conn_str)


# -------------------------------------------------------
# CDC status helpers
# -------------------------------------------------------
def is_cdc_enabled_db(cursor) -> bool:
    cursor.execute("SELECT is_cdc_enabled FROM sys.databases WHERE name = DB_NAME()")
    return bool(cursor.fetchone()[0])


def get_enabled_tables(cursor) -> List[str]:
    cursor.execute(
        """
        SELECT OBJECT_NAME(object_id) as name
        FROM cdc.change_tables
        ORDER BY object_id
        """
    )
    return [row[0] for row in cursor.fetchall()]


def get_capture_instance(cursor, table: str) -> Optional[str]:
    cursor.execute(
        """
        SELECT capture_instance
        FROM cdc.change_tables
        WHERE source_object_id = OBJECT_ID(?)
        """,
        table,
    )
    row = cursor.fetchone()
    return row[0] if row else None


# -------------------------------------------------------
# ENABLE
# -------------------------------------------------------
def enable_cdc_db(cursor):
    if not is_cdc_enabled_db(cursor):
        print("📊 Enabling CDC on database...")
        cursor.execute("EXEC sys.sp_cdc_enable_db")
        print("✅ CDC enabled on database")
    else:
        print("ℹ️  CDC already enabled on database")


def enable_cdc_table(cursor, schema: str, table: str):
    if get_capture_instance(cursor, table):
        print(f"ℹ️  CDC already enabled on table: {table}")
        return

    print(f"➕ Enabling CDC on table: {table}")
    cursor.execute(
        """
        EXEC sys.sp_cdc_enable_table
            @source_schema = ?,
            @source_name = ?,
            @role_name = NULL
        """,
        schema,
        table,
    )


# -------------------------------------------------------
# DISABLE
# -------------------------------------------------------
def disable_cdc_table(cursor, schema: str, table: str):
    capture_instance = get_capture_instance(cursor, table)
    if not capture_instance:
        print(f"ℹ️  CDC already disabled on table: {table}")
        return

    print(f"➖ Disabling CDC on table: {table}")
    cursor.execute(
        """
        EXEC sys.sp_cdc_disable_table
            @source_schema = ?,
            @source_name = ?,
            @capture_instance = ?
        """,
        schema,
        table,
        capture_instance,
    )


def disable_cdc_db(cursor):
    if is_cdc_enabled_db(cursor):
        print("📊 Disabling CDC on database...")
        cursor.execute("EXEC sys.sp_cdc_disable_db")
        print("✅ CDC disabled on database")
    else:
        print("ℹ️  CDC already disabled on database")


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
def main():
    tables = list(CREATE_STATEMENTS.keys())

    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("\n================ CDC STATUS ================\n")

        db_enabled = is_cdc_enabled_db(cursor)

        print(f"Database CDC enabled: {'YES' if db_enabled else 'NO'}")
        if db_enabled:
            enabled_tables = get_enabled_tables(cursor)

            print(f"Tables with CDC enabled ({len(enabled_tables)}):")

            if enabled_tables:
                for t in enabled_tables:
                    print(f"  • {t}")
            else:
                print("  (none)")

        print("\n============================================\n")

        action = input("Choose action [enable / disable / exit]: ").strip().lower()

        if action == "enable":
            enable_cdc_db(cursor)
            for table in tables:
                enable_cdc_table(cursor, "dbo", table)

        elif action == "disable":
            for table in tables:
                disable_cdc_table(cursor, "dbo", table)
            disable_cdc_db(cursor)

        elif action == "exit":
            print("👋 Exiting without changes")
            return

        else:
            print("❌ Invalid option. Use: enable, disable, or exit.")
            return

        conn.commit()
        print("\n✨ CDC operation completed successfully")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ CDC operation failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
