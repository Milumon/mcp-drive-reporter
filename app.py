#!/usr/bin/env python3
"""
Streamlit Web Interface for MCP Reports Agent
Provides a user-friendly interface to generate and send reports.
"""

import streamlit as st
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from agent_mcp import MCPReportsAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MCP - DB to Email",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def parse_recipients(recipients_text: str) -> list:
    """Parse recipients from text input."""
    if not recipients_text:
        return []
    
    # Split by comma or newline
    recipients = [email.strip() for email in recipients_text.replace('\n', ',').split(',')]
    # Filter out empty strings
    recipients = [email for email in recipients if email]
    return recipients


async def generate_report_async(date_from, date_to, recipients, subject):
    """Generate report asynchronously."""
    agent = MCPReportsAgent()
    result = await agent.generate_and_send_report(
        date_from=date_from,
        date_to=date_to,
        recipients=recipients,
        subject=subject
    )
    return result


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 MCP - DB to Email</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        **MCP Reports Agent** generates sales reports from PostgreSQL 
        and sends them via Gmail using the official MCP SDK.
        
        ### Features:
        - 📊 Dynamic date range selection
        - 📧 Multiple recipients support
        - 📈 Automated KPI calculation
        - 📎 CSV attachment included
        - 🔒 Secure MCP protocol
        
        ### Status:
        """)
        
        # Check database connection
        db_host = os.getenv('DB_HOST', 'localhost')
        db_name = os.getenv('DB_NAME', 'reports_db')
        st.info(f"**Database:** {db_host}/{db_name}")
        
        # Check Gmail configuration
        gmail_from = os.getenv('GMAIL_FROM', 'Not configured')
        st.info(f"**Gmail:** {gmail_from}")
        
        st.markdown("---")
        st.markdown("### 📚 Documentation")
        st.markdown("""
        - [MCP SDK Guide](MCP_SDK_GUIDE.md)
        - [Quick Start](QUICKSTART.md)
        - [README](README.md)
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📅 Report Configuration")
        
        # Date range selection
        st.subheader("1. Select Date Range")
        
        date_col1, date_col2 = st.columns(2)
        
        with date_col1:
            default_from = datetime.now() - timedelta(days=30)
            date_from = st.date_input(
                "Start Date",
                value=default_from,
                max_value=datetime.now(),
                help="Select the start date for the report"
            )
        
        with date_col2:
            default_to = datetime.now() - timedelta(days=1)
            date_to = st.date_input(
                "End Date",
                value=default_to,
                max_value=datetime.now(),
                help="Select the end date for the report"
            )
        
        # Validate date range
        if date_from > date_to:
            st.error("⚠️ Start date must be before end date!")
        
        # Recipients
        st.subheader("2. Email Recipients")
        recipients_text = st.text_area(
            "Recipients (one per line or comma-separated)",
            placeholder="user1@example.com\nuser2@example.com\nuser3@example.com",
            height=120,
            help="Enter email addresses separated by commas or new lines"
        )
        
        # Parse and validate recipients
        recipients = parse_recipients(recipients_text)
        
        if recipients:
            valid_recipients = [email for email in recipients if validate_email(email)]
            invalid_recipients = [email for email in recipients if not validate_email(email)]
            
            if valid_recipients:
                st.success(f"✅ {len(valid_recipients)} valid recipient(s)")
                with st.expander("View recipients"):
                    for email in valid_recipients:
                        st.text(f"• {email}")
            
            if invalid_recipients:
                st.error(f"❌ {len(invalid_recipients)} invalid email(s)")
                with st.expander("View invalid emails"):
                    for email in invalid_recipients:
                        st.text(f"• {email}")
        
        # Subject
        st.subheader("3. Email Subject")
        default_subject = f"Sales Report - {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}"
        subject = st.text_input(
            "Subject",
            value=default_subject,
            help="Customize the email subject line"
        )
    
    with col2:
        st.header("📊 Preview")
        
        # Report summary
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### Report Summary")
        st.markdown(f"""
        **Period:**  
        {date_from.strftime('%B %d, %Y')} to {date_to.strftime('%B %d, %Y')}
        
        **Duration:**  
        {(date_to - date_from).days + 1} days
        
        **Recipients:**  
        {len(recipients) if recipients else 0}
        
        **Subject:**  
        {subject[:50]}{'...' if len(subject) > 50 else ''}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Report contents
        st.markdown("### 📋 Report Contents")
        st.markdown("""
        The email will include:
        - 📊 **6 KPIs**: Total Sales, Average, Transactions, etc.
        - 🏆 **Top 5 Products** by sales
        - 📋 **Sales Details** table
        - 📎 **CSV Attachment** with full data
        """)
    
    # Generate button
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        generate_button = st.button(
            "🚀 Generate & Send Report",
            type="primary",
            use_container_width=True
        )
    
    # Generate report
    if generate_button:
        # Validation
        if date_from > date_to:
            st.error("❌ Invalid date range!")
            return
        
        if not recipients:
            st.error("❌ Please add at least one recipient!")
            return
        
        valid_recipients = [email for email in recipients if validate_email(email)]
        if not valid_recipients:
            st.error("❌ No valid email addresses found!")
            return
        
        if not subject:
            st.error("❌ Please enter an email subject!")
            return
        
        # Generate report
        with st.spinner("🔄 Generating report... This may take a few moments..."):
            try:
                # Convert dates to strings
                date_from_str = date_from.strftime('%Y-%m-%d')
                date_to_str = date_to.strftime('%Y-%m-%d')
                
                # Run async function
                result = asyncio.run(generate_report_async(
                    date_from_str,
                    date_to_str,
                    valid_recipients,
                    subject
                ))
                
                # Show result
                if result.get('status') == 'success':
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("## ✅ Report Sent Successfully!")
                    st.markdown(f"""
                    **Period:** {date_from_str} to {date_to_str}  
                    **Recipients:** {', '.join(valid_recipients[:3])}{'...' if len(valid_recipients) > 3 else ''}  
                    **Total Recipients:** {len(valid_recipients)}
                    
                    The report has been generated and sent via email. 
                    Recipients should receive it shortly.
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show balloons
                    st.balloons()
                    
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.markdown("## ❌ Error Generating Report")
                    st.markdown(f"""
                    **Error:** {result.get('message', 'Unknown error')}
                    
                    Please check:
                    - Database connection is working
                    - Gmail credentials are configured
                    - Date range has data
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with st.expander("View error details"):
                        st.json(result)
            
            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown("## ❌ Unexpected Error")
                st.markdown(f"**Error:** {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                with st.expander("View full error"):
                    st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>MCP Reports Agent | Powered by <a href='https://github.com/modelcontextprotocol/python-sdk'>MCP Python SDK</a></p>
        <p>© 2025 - Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

