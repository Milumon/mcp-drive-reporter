#!/usr/bin/env python3
"""
Loader for fact_transacciones_cripto from an Excel file.

Usage:
  python3 load_crypto_transactions.py --file /path/to/data.xlsx [--sheet Hoja1]

Expected columns (case-insensitive, accents ignored):
  - fecha (date)
  - usuario (text)
  - tipo_transaccion (text)
  - criptomoneda (text)
  - monto (number)
  - tc (number, optional)
"""

import os
import argparse
import logging
import unicodedata
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load env
load_dotenv()


def normalize_column_name(name: str) -> str:
    """Normalize column names: lowercase, remove accents/spaces."""
    if name is None:
        return ''
    # Remove accents
    name = ''.join(c for c in unicodedata.normalize('NFKD', str(name)) if not unicodedata.combining(c))
    name = name.strip().lower()
    name = name.replace(' ', '_')
    return name


def get_connection():
    cfg = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'dbname': os.getenv('DB_NAME', 'reports_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASS', ''),
    }
    return psycopg2.connect(**cfg)


def ensure_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS fact_transacciones_cripto (
        id SERIAL PRIMARY KEY,
        fecha DATE NOT NULL,
        usuario TEXT NOT NULL,
        tipo_transaccion TEXT NOT NULL,
        criptomoneda TEXT NOT NULL,
        monto NUMERIC(38, 10) NOT NULL,
        tc NUMERIC(18, 8),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_ftc_fecha ON fact_transacciones_cripto(fecha);
    CREATE INDEX IF NOT EXISTS idx_ftc_usuario ON fact_transacciones_cripto(usuario);
    CREATE INDEX IF NOT EXISTS idx_ftc_cripto ON fact_transacciones_cripto(criptomoneda);
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def parse_args():
    p = argparse.ArgumentParser(description='Load Excel data into fact_transacciones_cripto')
    p.add_argument('--file', required=True, help='Path to Excel file (.xlsx)')
    p.add_argument('--sheet', default=None, help='Sheet name (optional)')
    return p.parse_args()


def load_dataframe(excel_path: str, sheet: str | None) -> pd.DataFrame:
    if sheet:
        df = pd.read_excel(excel_path, sheet_name=sheet)
    else:
        df = pd.read_excel(excel_path)

    # Normalize column names
    df.columns = [normalize_column_name(c) for c in df.columns]

    # Column mapping and validation
    required = ['fecha', 'usuario', 'tipo_transaccion', 'criptomoneda', 'monto']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Optional tc
    if 'tc' not in df.columns:
        df['tc'] = None

    # Type conversions
    # fecha
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    # monto and tc
    df['monto'] = pd.to_numeric(df['monto'], errors='coerce')
    df['tc'] = pd.to_numeric(df['tc'], errors='coerce')

    # Drop rows with null requireds
    df = df.dropna(subset=['fecha', 'usuario', 'tipo_transaccion', 'criptomoneda', 'monto'])
    return df[['fecha', 'usuario', 'tipo_transaccion', 'criptomoneda', 'monto', 'tc']]


def bulk_insert(conn, df: pd.DataFrame):
    records = list(df.itertuples(index=False, name=None))
    if not records:
        logger.info('No records to insert.')
        return
    sql = """
        INSERT INTO fact_transacciones_cripto
            (fecha, usuario, tipo_transaccion, criptomoneda, monto, tc)
        VALUES %s
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, records, page_size=1000)
    conn.commit()


def main():
    args = parse_args()
    excel_path = args.file
    sheet = args.sheet

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File not found: {excel_path}")

    logger.info(f"Reading Excel: {excel_path} {'['+sheet+']' if sheet else ''}")
    df = load_dataframe(excel_path, sheet)
    logger.info(f"Loaded rows: {len(df)}")

    conn = get_connection()
    try:
        ensure_table(conn)
        bulk_insert(conn, df)
        logger.info("✅ Load completed successfully")
    finally:
        conn.close()


if __name__ == '__main__':
    main()


