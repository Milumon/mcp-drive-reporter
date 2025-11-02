#!/usr/bin/env python3
"""
MCP Server for PostgreSQL
Exposes database queries as MCP tools following the official SDK pattern.
Reference: https://github.com/modelcontextprotocol/python-sdk
"""

import os
import logging
import asyncio
from typing import Any
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("postgres-mcp")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'reports_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASS', ''),
}


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def _fetch_all(sql: str, params: dict) -> list[dict]:
    """Helper to run a query and return list of dict rows."""
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available database tools."""
    return [
        Tool(
            name="query_ventas",
            description="Query sales data (ventas) for a specific date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                },
                "required": ["date_from", "date_to"],
            },
        ),
        Tool(
            name="get_kpis",
            description="Get aggregated KPIs (total sales, average, transactions, etc.) for a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                },
                "required": ["date_from", "date_to"],
            },
        ),
        Tool(
            name="get_top_productos",
            description="Get top N products by sales for a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top products to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["date_from", "date_to"],
            },
        ),
        Tool(
            name="execute_custom_query",
            description="Execute a custom SQL query (read-only SELECT statements)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query to execute",
                    },
                },
                "required": ["sql"],
            },
        ),
        # Crypto tools
        Tool(
            name="top_clientes_compra",
            description="Top N users by total purchased (fact_transacciones_cripto)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["date_from", "date_to"]
            },
        ),
        Tool(
            name="top_clientes_venta",
            description="Top N users by total sold (fact_transacciones_cripto)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["date_from", "date_to"]
            },
        ),
        Tool(
            name="top_monedas_compra",
            description="Top N coins by amount purchased (fact_transacciones_cripto)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["date_from", "date_to"]
            },
        ),
        Tool(
            name="top_monedas_venta",
            description="Top N coins by amount sold (fact_transacciones_cripto)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["date_from", "date_to"]
            },
        ),
        Tool(
            name="totales_compra_venta",
            description="Totals for purchases and sales in date range (fact_transacciones_cripto)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string"},
                    "date_to": {"type": "string"}
                },
                "required": ["date_from", "date_to"]
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "query_ventas":
            return await query_ventas(arguments["date_from"], arguments["date_to"])
        elif name == "get_kpis":
            return await get_kpis(arguments["date_from"], arguments["date_to"])
        elif name == "get_top_productos":
            limit = arguments.get("limit", 5)
            return await get_top_productos(arguments["date_from"], arguments["date_to"], limit)
        elif name == "execute_custom_query":
            return await execute_custom_query(arguments["sql"])
        # Crypto summaries
        elif name == "top_clientes_compra":
            limit = arguments.get("limit", 5)
            return await top_clientes(date_from=arguments["date_from"], date_to=arguments["date_to"], tipo="compra", limit=limit)
        elif name == "top_clientes_venta":
            limit = arguments.get("limit", 5)
            return await top_clientes(date_from=arguments["date_from"], date_to=arguments["date_to"], tipo="venta", limit=limit)
        elif name == "top_monedas_compra":
            limit = arguments.get("limit", 5)
            return await top_monedas(date_from=arguments["date_from"], date_to=arguments["date_to"], tipo="compra", limit=limit)
        elif name == "top_monedas_venta":
            limit = arguments.get("limit", 5)
            return await top_monedas(date_from=arguments["date_from"], date_to=arguments["date_to"], tipo="venta", limit=limit)
        elif name == "totales_compra_venta":
            return await totales_compra_venta(arguments["date_from"], arguments["date_to"])
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def query_ventas(date_from: str, date_to: str) -> list[TextContent]:
    """Query sales data."""
    sql = """
        SELECT 
            fecha,
            producto,
            categoria,
            cliente,
            cantidad,
            precio_unitario,
            importe,
            region
        FROM ventas
        WHERE fecha BETWEEN %(date_from)s AND %(date_to)s
        ORDER BY fecha DESC, importe DESC
    """
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql, {"date_from": date_from, "date_to": date_to})
        rows = cursor.fetchall()
        
        # Format results
        result_text = f"Found {len(rows)} sales records from {date_from} to {date_to}\n\n"
        
        if rows:
            # Show first 10 rows
            for i, row in enumerate(rows[:10], 1):
                result_text += f"{i}. {row['fecha']} - {row['producto']} - ${row['importe']:.2f}\n"
            
            if len(rows) > 10:
                result_text += f"\n... and {len(rows) - 10} more records"
        else:
            result_text += "No records found for this period."
        
        return [TextContent(type="text", text=result_text)]
    finally:
        conn.close()


async def top_clientes(date_from: str, date_to: str, tipo: str, limit: int = 5) -> list[TextContent]:
    """Top N clientes by total monto for tipo (compra/venta)."""
    sql = """
        SELECT 
            usuario,
            SUM(monto * COALESCE(tc, 1)) AS total_monto,
            COUNT(*) AS transacciones
        FROM fact_transacciones_cripto
        WHERE fecha BETWEEN %(date_from)s AND %(date_to)s
          AND LOWER(tipo_transaccion) = %(tipo)s
        GROUP BY usuario
        ORDER BY total_monto DESC
        LIMIT %(limit)s
    """
    rows = _fetch_all(sql, {"date_from": date_from, "date_to": date_to, "tipo": tipo.lower(), "limit": limit})
    title = "Top clientes con mayor compra" if tipo.lower() == "compra" else "Top clientes con mayor venta"
    text = f"🏆 {title} ({date_from} → {date_to})\n\n"
    if rows:
        for i, r in enumerate(rows, 1):
            text += f"{i}. {r['usuario']} — Total: {r['total_monto']:,.6f} ({r['transacciones']} tx)\n"
    else:
        text += "Sin datos para el rango."
    return [TextContent(type="text", text=text)]


async def top_monedas(date_from: str, date_to: str, tipo: str, limit: int = 5) -> list[TextContent]:
    """Top N criptomonedas by total monto for tipo (compra/venta)."""
    sql = """
        SELECT 
            criptomoneda,
            SUM(monto * COALESCE(tc, 1)) AS total_monto,
            COUNT(*) AS transacciones
        FROM fact_transacciones_cripto
        WHERE fecha BETWEEN %(date_from)s AND %(date_to)s
          AND LOWER(tipo_transaccion) = %(tipo)s
        GROUP BY criptomoneda
        ORDER BY total_monto DESC
        LIMIT %(limit)s
    """
    rows = _fetch_all(sql, {"date_from": date_from, "date_to": date_to, "tipo": tipo.lower(), "limit": limit})
    title = "Top monedas más compradas" if tipo.lower() == "compra" else "Top monedas más vendidas"
    text = f"💠 {title} ({date_from} → {date_to})\n\n"
    if rows:
        for i, r in enumerate(rows, 1):
            text += f"{i}. {r['criptomoneda']} — Total: {r['total_monto']:,.6f} ({r['transacciones']} tx)\n"
    else:
        text += "Sin datos para el rango."
    return [TextContent(type="text", text=text)]


async def totales_compra_venta(date_from: str, date_to: str) -> list[TextContent]:
    """Totals for purchases and sales in date range."""
    sql = """
        SELECT LOWER(tipo_transaccion) AS tipo, COALESCE(SUM(monto * COALESCE(tc, 1)), 0) AS total
        FROM fact_transacciones_cripto
        WHERE fecha BETWEEN %(date_from)s AND %(date_to)s
          AND LOWER(tipo_transaccion) IN ('compra', 'venta')
        GROUP BY LOWER(tipo_transaccion)
    """
    rows = _fetch_all(sql, {"date_from": date_from, "date_to": date_to})
    tot_compra = next((r['total'] for r in rows if r['tipo'] == 'compra'), 0)
    tot_venta = next((r['total'] for r in rows if r['tipo'] == 'venta'), 0)
    text = (
        f"📊 Totales ({date_from} → {date_to})\n\n"
        f"• Total comprado: {tot_compra:,.6f}\n"
        f"• Total vendido: {tot_venta:,.6f}\n"
    )
    return [TextContent(type="text", text=text)]


async def get_kpis(date_from: str, date_to: str) -> list[TextContent]:
    """Get aggregated KPIs."""
    sql = """
        SELECT 
            COUNT(*) as total_transacciones,
            SUM(importe) as total_ventas,
            AVG(importe) as promedio_venta,
            SUM(cantidad) as total_productos_vendidos,
            COUNT(DISTINCT cliente) as clientes_unicos,
            COUNT(DISTINCT producto) as productos_unicos
        FROM ventas
        WHERE fecha BETWEEN %(date_from)s AND %(date_to)s
    """
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql, {"date_from": date_from, "date_to": date_to})
        row = cursor.fetchone()
        
        if row and row['total_transacciones'] > 0:
            result_text = f"""📊 KPIs for {date_from} to {date_to}:

💰 Total Sales: ${row['total_ventas']:,.2f}
📈 Average Sale: ${row['promedio_venta']:,.2f}
🛒 Total Transactions: {row['total_transacciones']:,}
📦 Products Sold: {row['total_productos_vendidos']:,}
👥 Unique Customers: {row['clientes_unicos']:,}
🏷️ Unique Products: {row['productos_unicos']:,}
"""
        else:
            result_text = f"No data found for period {date_from} to {date_to}"
        
        return [TextContent(type="text", text=result_text)]
    finally:
        conn.close()


async def get_top_productos(date_from: str, date_to: str, limit: int = 5) -> list[TextContent]:
    """Get top products by sales."""
    sql = """
        SELECT 
            producto,
            categoria,
            SUM(cantidad) as cantidad_total,
            SUM(importe) as ventas_totales,
            COUNT(*) as num_transacciones
        FROM ventas
        WHERE fecha BETWEEN %(date_from)s AND %(date_to)s
        GROUP BY producto, categoria
        ORDER BY ventas_totales DESC
        LIMIT %(limit)s
    """
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql, {"date_from": date_from, "date_to": date_to, "limit": limit})
        rows = cursor.fetchall()
        
        result_text = f"🏆 Top {limit} Products ({date_from} to {date_to}):\n\n"
        
        if rows:
            for i, row in enumerate(rows, 1):
                result_text += f"{i}. {row['producto']} ({row['categoria']})\n"
                result_text += f"   Sales: ${row['ventas_totales']:,.2f} | Qty: {row['cantidad_total']:,} | Transactions: {row['num_transacciones']}\n\n"
        else:
            result_text += "No products found for this period."
        
        return [TextContent(type="text", text=result_text)]
    finally:
        conn.close()


async def execute_custom_query(sql: str) -> list[TextContent]:
    """Execute a custom SQL query (read-only)."""
    # Security: Only allow SELECT statements
    if not sql.strip().upper().startswith('SELECT'):
        return [TextContent(type="text", text="Error: Only SELECT queries are allowed")]
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        result_text = f"Query returned {len(rows)} rows\n\n"
        
        if rows:
            # Show column names
            columns = list(rows[0].keys())
            result_text += " | ".join(columns) + "\n"
            result_text += "-" * 80 + "\n"
            
            # Show first 20 rows
            for row in rows[:20]:
                result_text += " | ".join(str(row[col]) for col in columns) + "\n"
            
            if len(rows) > 20:
                result_text += f"\n... and {len(rows) - 20} more rows"
        
        return [TextContent(type="text", text=result_text)]
    except Exception as e:
        return [TextContent(type="text", text=f"Query error: {str(e)}")]
    finally:
        conn.close()


async def main():
    """Run the MCP server."""
    logger.info("🚀 Starting PostgreSQL MCP Server...")
    
    # Test database connection
    try:
        conn = get_db_connection()
        conn.close()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

