import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import pyodbc
import csv
import os

# =========================
# CONFIGURACION
# =========================

PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "data_migration"
PG_USER = "postgres"
PG_PASSWORD = "root"

SQL_SERVER = "localhost"
SQL_DATABASE = "data_migration"

CSV_FOLDER = "C:/Migracion"

# =========================
# EXPORTAR POSTGRESQL
# =========================

def export_table(table_name):

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

    cur = conn.cursor()

    csv_path = os.path.join(
        CSV_FOLDER,
        f"{table_name}.csv"
    )

    with open(csv_path, "w", newline="", encoding="utf-8") as f:

        cur.copy_expert(
            f"COPY empresa.{table_name} TO STDOUT WITH CSV HEADER",
            f
        )

    cur.close()
    conn.close()

    return csv_path

# =========================
# SQL SERVER
# =========================

def get_sql_connection():

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return conn

# =========================
# CREAR TABLAS
# =========================

def create_tables():

    conn = get_sql_connection()

    cursor = conn.cursor()

    cursor.execute("""

    IF OBJECT_ID('clientes','U') IS NULL

    CREATE TABLE clientes(
        cliente_id INT PRIMARY KEY,
        nombres VARCHAR(100),
        apellidos VARCHAR(100),
        cedula VARCHAR(10),
        correo VARCHAR(120),
        ciudad VARCHAR(80),
        fecha_registro DATETIME
    )

    """)

    cursor.execute("""

    IF OBJECT_ID('productos','U') IS NULL

    CREATE TABLE productos(
        producto_id INT PRIMARY KEY,
        nombre VARCHAR(100),
        categoria VARCHAR(50),
        precio DECIMAL(10,2),
        stock INT
    )

    """)

    cursor.execute("""

    IF OBJECT_ID('ventas','U') IS NULL

    CREATE TABLE ventas(
        venta_id INT PRIMARY KEY,
        cliente_id INT,
        fecha_venta DATETIME,
        total DECIMAL(12,2)
    )

    """)

    cursor.execute("""

    IF OBJECT_ID('detalle_ventas','U') IS NULL

    CREATE TABLE detalle_ventas(
        detalle_id INT PRIMARY KEY,
        venta_id INT,
        producto_id INT,
        cantidad INT,
        precio_unitario DECIMAL(10,2)
    )

    """)

    conn.commit()
    conn.close()

# =========================
# IMPORTAR CSV
# =========================

def import_csv(table_name):

    csv_file = os.path.join(
        CSV_FOLDER,
        f"{table_name}.csv"
    )

    conn = get_sql_connection()

    cursor = conn.cursor()

    cursor.execute(f"TRUNCATE TABLE {table_name}")

    sql = f"""
    BULK INSERT {table_name}
    FROM '{csv_file}'
    WITH (
        FIRSTROW = 2,
        FIELDTERMINATOR = ',',
        ROWTERMINATOR = '0x0A',
        KEEPNULLS
    )
    """

    cursor.execute(sql)

    conn.commit()
    conn.close()

# =========================
# MIGRAR
# =========================

def migrate():

    try:
        

        status.set("Exportando clientes...")
        root.update()

        export_table("clientes")

        status.set("Exportando productos...")
        root.update()

        export_table("productos")

        status.set("Exportando ventas...")
        root.update()

        export_table("ventas")

        status.set("Exportando detalle_ventas...")
        root.update()

        export_table("detalle_ventas")

        status.set("Creando tablas...")
        root.update()

        create_tables()

        status.set("Importando clientes...")
        root.update()

        import_csv("clientes")

        status.set("Importando productos...")
        root.update()

        import_csv("productos")

        status.set("Importando ventas...")
        root.update()

        import_csv("ventas")

        status.set("Importando detalle_ventas...")
        root.update()

        import_csv("detalle_ventas")

        status.set("Migración completada")

        messagebox.showinfo(
            "Éxito",
            "Migración completada correctamente"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

# =========================
# INTERFAZ
# =========================

root = tk.Tk()

root.title("Migrador PostgreSQL → SQL Server")
root.geometry("500x250")

titulo = tk.Label(
    root,
    text="Migrador PostgreSQL → SQL Server",
    font=("Arial",16,"bold")
)

titulo.pack(pady=20)

status = tk.StringVar()
status.set("Listo")

lbl = tk.Label(
    root,
    textvariable=status,
    font=("Arial",11)
)

lbl.pack(pady=10)

btn = ttk.Button(
    root,
    text="Migrar",
    command=migrate
)

btn.pack(pady=20)

root.mainloop()