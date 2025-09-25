import os
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import URL

def make_engine(server: str, db: str, driver: str, encrypt: bool = True):
    """
    Engine SQLAlchemy para SQL Server con Windows Authentication.
    """
    enc = "yes" if encrypt else "no"
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={db};"
        "Trusted_Connection=yes;"
        f"Encrypt={enc};"
        "TrustServerCertificate=yes;"
    )
    url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_str})
    engine = create_engine(url, fast_executemany=True)

    @event.listens_for(engine, "before_cursor_execute")
    def _fastexec(conn, cursor, statement, params, context, executemany):
        try:
            cursor.fast_executemany = True
        except Exception:
            pass

    return engine

def ensure_database(server: str, driver: str, db: str):
    """
    Crea la BD si no existe, ejecutando CREATE DATABASE en AUTOCOMMIT.
    """
    enc = "yes"
    master_conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        f"Encrypt={enc};"
        "TrustServerCertificate=yes;"
    )
    master_url = URL.create("mssql+pyodbc", query={"odbc_connect": master_conn_str})
    master_engine = create_engine(master_url)

    # AUTOCOMMIT para CREATE DATABASE
    with master_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        exists = conn.execute(text("SELECT DB_ID(:dbname)"), {"dbname": db}).scalar()
        if exists is None:
            # CREATE DATABASE debe ir fuera de transaccion
            conn.exec_driver_sql(f"CREATE DATABASE [{db}]")

    master_engine.dispose()

def run_sql_file(engine, path: str):
    """
    Ejecuta un .sql completo. Soporta separadores 'GO' (case-insensitive).
    Es idempotente: tu script 01_schema.sql ya no contiene DROP.
    """
    with open(path, "r", encoding="utf-8") as f:
        sql_text = f.read()

    import re
    batches = re.split(r"(?im)^\s*GO\s*$", sql_text)
    with engine.connect() as conn:
        for batch in batches:
            chunk = batch.strip()
            if chunk:
                conn.execute(text(chunk))
        conn.commit()
