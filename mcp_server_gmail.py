#!/usr/bin/env python3
"""
MCP Server for Gmail
Exposes email sending as MCP tools following the official SDK pattern.
Reference: https://github.com/modelcontextprotocol/python-sdk
"""

import os
import logging
import asyncio
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Any

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
server = Server("gmail-mcp")

# Gmail configuration
GMAIL_FROM = os.getenv('GMAIL_FROM')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Gmail tools."""
    return [
        Tool(
            name="send_email",
            description="Send an email via Gmail with optional HTML body and attachments",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recipient email addresses",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body_html": {
                        "type": "string",
                        "description": "Email body in HTML format",
                    },
                    "attachments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "filename": {"type": "string"},
                                "content_base64": {"type": "string"},
                            },
                        },
                        "description": "Optional list of attachments (base64 encoded)",
                    },
                    "cc": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional CC recipients",
                    },
                },
                "required": ["to", "subject", "body_html"],
            },
        ),
        Tool(
            name="send_simple_email",
            description="Send a simple text email via Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body (plain text)",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "send_email":
            return await send_email(
                to=arguments["to"],
                subject=arguments["subject"],
                body_html=arguments["body_html"],
                attachments=arguments.get("attachments", []),
                cc=arguments.get("cc", []),
            )
        elif name == "send_simple_email":
            return await send_simple_email(
                to=arguments["to"],
                subject=arguments["subject"],
                body=arguments["body"],
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def send_email(
    to: list[str],
    subject: str,
    body_html: str,
    attachments: list[dict] = None,
    cc: list[str] = None,
) -> list[TextContent]:
    """Send an email with HTML and attachments."""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = GMAIL_FROM
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        # Add HTML body
        html_part = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                filename = attachment.get('filename', 'attachment.txt')
                content_b64 = attachment.get('content_base64', '')
                
                # Decode base64 content
                content = base64.b64decode(content_b64)
                
                # Create attachment part
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
        
        # Send email
        server_smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server_smtp.starttls()
        server_smtp.login(GMAIL_FROM, GMAIL_APP_PASSWORD)
        
        # Prepare all recipients
        all_recipients = to.copy()
        if cc:
            all_recipients.extend(cc)
        
        server_smtp.send_message(msg, GMAIL_FROM, all_recipients)
        server_smtp.quit()
        
        result_text = f"""✅ Email sent successfully!

To: {', '.join(to)}
{f'CC: {", ".join(cc)}' if cc else ''}
Subject: {subject}
Attachments: {len(attachments) if attachments else 0}
"""
        
        logger.info(f"Email sent to {len(all_recipients)} recipient(s)")
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        error_text = f"❌ Failed to send email: {str(e)}"
        logger.error(error_text)
        return [TextContent(type="text", text=error_text)]


async def send_simple_email(to: str, subject: str, body: str) -> list[TextContent]:
    """Send a simple text email."""
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = GMAIL_FROM
        msg['To'] = to
        msg['Subject'] = subject
        
        server_smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server_smtp.starttls()
        server_smtp.login(GMAIL_FROM, GMAIL_APP_PASSWORD)
        server_smtp.send_message(msg)
        server_smtp.quit()
        
        result_text = f"""✅ Simple email sent!

To: {to}
Subject: {subject}
"""
        
        logger.info(f"Simple email sent to {to}")
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        error_text = f"❌ Failed to send email: {str(e)}"
        logger.error(error_text)
        return [TextContent(type="text", text=error_text)]


async def main():
    """Run the MCP server."""
    logger.info("🚀 Starting Gmail MCP Server...")
    
    # Validate configuration
    if not GMAIL_FROM or not GMAIL_APP_PASSWORD:
        logger.error("❌ Gmail credentials not configured in .env")
        return
    
    logger.info(f"✅ Gmail configured for: {GMAIL_FROM}")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

