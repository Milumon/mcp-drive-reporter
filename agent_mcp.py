#!/usr/bin/env python3
"""
MCP-based Reports Agent
Uses official MCP SDK to orchestrate PostgreSQL and Gmail servers.
Reference: https://github.com/modelcontextprotocol/python-sdk
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

from report_generator import ReportGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPReportsAgent:
    """
    Reports Agent using MCP SDK.
    Orchestrates PostgreSQL and Gmail MCP servers to generate and send reports.
    """
    
    def __init__(self):
        """Initialize the MCP agent."""
        self.report_generator = ReportGenerator()
        
        # Server parameters
        self.postgres_server = StdioServerParameters(
            command="python3",
            args=["mcp_server_postgres.py"]
        )
        
        self.gmail_server = StdioServerParameters(
            command="python3",
            args=["mcp_server_gmail.py"]
        )
    
    async def generate_and_send_report(
        self,
        date_from: str,
        date_to: str,
        recipients: list[str],
        subject: Optional[str] = None
    ):
        """
        Generate and send a report using MCP servers.
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            recipients: List of email addresses
            subject: Email subject (optional)
        """
        logger.info(f"📊 Generating report for {date_from} to {date_to}")
        
        try:
            # Step 1: Connect to PostgreSQL MCP server and fetch data
            logger.info("🔍 Step 1/4: Fetching data from PostgreSQL...")
            async with stdio_client(self.postgres_server) as (pg_read, pg_write):
                async with ClientSession(pg_read, pg_write) as pg_session:
                    await pg_session.initialize()
                    
                    # Get ventas data
                    ventas_result = await pg_session.call_tool(
                        "query_ventas",
                        {"date_from": date_from, "date_to": date_to}
                    )
                    logger.info("✅ Ventas data fetched")
                    
                    # Get KPIs
                    kpis_result = await pg_session.call_tool(
                        "get_kpis",
                        {"date_from": date_from, "date_to": date_to}
                    )
                    logger.info("✅ KPIs fetched")
                    
                    # Get top products
                    top_result = await pg_session.call_tool(
                        "get_top_productos",
                        {"date_from": date_from, "date_to": date_to, "limit": 5}
                    )
                    logger.info("✅ Top products fetched")
            
            # Step 2: Process results and generate report
            logger.info("📝 Step 2/4: Generating report...")
            
            # Extract text from MCP responses
            ventas_text = self._extract_text(ventas_result)
            kpis_text = self._extract_text(kpis_result)
            top_text = self._extract_text(top_result)
            
            # Generate HTML report
            html_report = self._generate_html_report(
                date_from, date_to, ventas_text, kpis_text, top_text
            )
            
            # Generate CSV (simplified for demo)
            csv_report = self._generate_csv_report(ventas_text)
            
            logger.info("✅ Report generated")
            
            # Step 3: Prepare email with attachment
            logger.info("📧 Step 3/4: Preparing email...")
            
            if not subject:
                subject = f"Reporte de Ventas - {date_from} al {date_to}"
            
            # Encode CSV as base64
            import base64
            csv_base64 = base64.b64encode(csv_report.encode('utf-8')).decode('utf-8')
            
            # Step 4: Send email via Gmail MCP server
            logger.info("📤 Step 4/4: Sending email...")
            async with stdio_client(self.gmail_server) as (gmail_read, gmail_write):
                async with ClientSession(gmail_read, gmail_write) as gmail_session:
                    await gmail_session.initialize()
                    
                    # Send email with attachment
                    send_result = await gmail_session.call_tool(
                        "send_email",
                        {
                            "to": recipients,
                            "subject": subject,
                            "body_html": html_report,
                            "attachments": [
                                {
                                    "filename": f"reporte_{date_from}_al_{date_to}.csv",
                                    "content_base64": csv_base64
                                }
                            ]
                        }
                    )
                    
                    send_text = self._extract_text(send_result)
                    logger.info(f"✅ {send_text}")
            
            print("\n" + "="*60)
            print("✅ REPORT SENT SUCCESSFULLY")
            print("="*60)
            print(f"\n📊 Period: {date_from} to {date_to}")
            print(f"📧 Recipients: {', '.join(recipients)}")
            print(f"📎 Attachment: reporte_{date_from}_al_{date_to}.csv")
            print("\n" + "="*60 + "\n")
            
            return {"status": "success", "message": "Report sent successfully"}
            
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def _extract_text(self, result) -> str:
        """Extract text from MCP tool result."""
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    return content.text
        return str(result)
    
    def _generate_html_report(
        self,
        date_from: str,
        date_to: str,
        ventas_text: str,
        kpis_text: str,
        top_text: str
    ) -> str:
        """Generate HTML report from text data."""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Ventas</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        pre {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Reporte de Ventas</h1>
            <p><strong>Periodo:</strong> {date_from} al {date_to}</p>
            <p><strong>Generado:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="section">
            <h2>📈 KPIs</h2>
            <pre>{kpis_text}</pre>
        </div>

        <div class="section">
            <h2>🏆 Top Productos</h2>
            <pre>{top_text}</pre>
        </div>

        <div class="section">
            <h2>📋 Detalle de Ventas</h2>
            <pre>{ventas_text}</pre>
        </div>

        <div class="footer">
            Reporte generado automáticamente por MCP Reports Agent<br>
            Powered by <a href="https://github.com/modelcontextprotocol/python-sdk">MCP Python SDK</a><br>
            © 2025 - Todos los derechos reservados
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def _generate_csv_report(self, ventas_text: str) -> str:
        """Generate simple CSV from ventas text."""
        # Simplified CSV generation
        csv = "Fecha,Producto,Importe\n"
        csv += "# Ver adjunto para datos completos\n"
        csv += f"# Periodo consultado\n"
        return csv


async def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🚀 MCP REPORTS AGENT")
    print("Using Official MCP Python SDK")
    print("="*60 + "\n")
    
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🔍 Testing MCP servers...\n")
        
        # Test PostgreSQL server
        print("Testing PostgreSQL MCP server...")
        agent = MCPReportsAgent()
        try:
            async with stdio_client(agent.postgres_server) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    print(f"✅ PostgreSQL MCP: {len(tools.tools)} tools available")
                    for tool in tools.tools:
                        print(f"   - {tool.name}: {tool.description}")
        except Exception as e:
            print(f"❌ PostgreSQL MCP error: {e}")
        
        # Test Gmail server
        print("\nTesting Gmail MCP server...")
        try:
            async with stdio_client(agent.gmail_server) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    print(f"✅ Gmail MCP: {len(tools.tools)} tools available")
                    for tool in tools.tools:
                        print(f"   - {tool.name}: {tool.description}")
        except Exception as e:
            print(f"❌ Gmail MCP error: {e}")
        
        print("\n" + "="*60)
        return
    
    # Interactive mode
    print("📝 Report Configuration\n")
    
    # Get dates
    default_to = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    default_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    date_from = input(f"Start date (YYYY-MM-DD) [{default_from}]: ").strip() or default_from
    date_to = input(f"End date (YYYY-MM-DD) [{default_to}]: ").strip() or default_to
    
    # Get recipients
    recipients_str = input("Recipients (comma-separated): ").strip()
    if not recipients_str:
        print("❌ Error: At least one recipient is required")
        return
    
    recipients = [email.strip() for email in recipients_str.split(',')]
    
    # Get subject
    subject = input("Subject (Enter for default): ").strip() or None
    
    # Generate and send report
    print("\n" + "="*60)
    agent = MCPReportsAgent()
    await agent.generate_and_send_report(date_from, date_to, recipients, subject)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

