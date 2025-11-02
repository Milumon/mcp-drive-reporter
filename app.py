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
from typing import List, Dict, Any
import json
import re
import time
import os
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MCP - Good Queries",
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
    st.markdown('<h1 class="main-header">📊 MCP - Good Queries</h1>', unsafe_allow_html=True)
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
    
    tabs = st.tabs(["Form", "Chat (LLM)"])

    # =====================
    # Tab 1: Form workflow
    # =====================
    with tabs[0]:
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
                use_container_width=True,
                key="btn_form_generate"
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
    
    # =====================
    # Tab 2: Chat workflow
    # =====================
    with tabs[1]:
        st.subheader("💬 Ask the assistant to generate and email the report")
        st.caption("Powered by OpenAI. Set OPENAI_API_KEY in your .env or Streamlit secrets.")

        if 'chat' not in st.session_state:
            st.session_state.chat = []  # list of dicts {role, content}

        api_key = os.getenv('OPENAI_API_KEY') or st.secrets.get('OPENAI_API_KEY') if hasattr(st, 'secrets') else None
        if not api_key:
            st.warning("OPENAI_API_KEY not configured. Add it to your .env or Streamlit secrets.")
        elif OpenAI is None:
            st.warning("openai package not available. Please pip install -r requirements.txt")
        else:
            client = OpenAI(api_key=api_key)

            # System prompt guiding structured extraction
            system_prompt = (
                "You are an assistant that helps collect parameters to generate a crypto transactions report and send by email. "
                "Always keep conversation brief. When you have all required parameters, return ONLY a JSON object (no extra text) with this shape: "
                "{\n  'action': 'send_report',\n  'params': { 'date_from': 'YYYY-MM-DD', 'date_to': 'YYYY-MM-DD', 'recipients': ['a@b.com'], 'subject': '...'}\n}. "
                "If any field is missing, ask a short follow-up question to get it. Dates must be ISO YYYY-MM-DD."
            )

            # Render chat history
            for msg in st.session_state.chat:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])

            user_input = st.text_input(
                "Your message",
                key="chat_user_input",
                placeholder="Ask for a report, e.g., 'Send report for March to finance@company.com'"
            )
            send_click = st.button("Send", key="chat_send_btn")
            if send_click and user_input:
                st.session_state.chat.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                # Build messages for the API
                messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            resp = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=messages,
                                temperature=0.2,
                            )
                            ai_text = resp.choices[0].message.content
                        except Exception:
                            ai_text = (
                                "Sorry, the LLM call failed (likely invalid OPENAI_API_KEY). "
                                "Set a valid key in your .env or Streamlit secrets and try again."
                            )
                    st.markdown(ai_text or "")
                st.session_state.chat.append({"role": "assistant", "content": ai_text or ""})

                # Try to parse a JSON action
                def extract_json(s: str) -> Dict[str, Any] | None:
                    if not s:
                        return None
                    # Look for fenced code block JSON
                    m = re.search(r"\{[\s\S]*\}", s)
                    if m:
                        try:
                            return json.loads(m.group(0).replace("'", '"'))
                        except Exception:
                            return None
                    return None

                action = extract_json(ai_text or "")
                if action and action.get('action') == 'send_report':
                    params = action.get('params', {})
                    date_from = params.get('date_from')
                    date_to = params.get('date_to')
                    recipients = params.get('recipients') or []
                    subject = params.get('subject') or f"Reporte Cripto - {date_from} al {date_to}"

                    # Basic validation
                    ok = True
                    try:
                        datetime.strptime(date_from, '%Y-%m-%d')
                        datetime.strptime(date_to, '%Y-%m-%d')
                    except Exception:
                        ok = False
                    if not isinstance(recipients, list) or not recipients:
                        ok = False

                    if ok:
                        with st.chat_message("assistant"):
                            with st.spinner("🔄 Generating and sending the report..."):
                                try:
                                    result = asyncio.run(generate_report_async(date_from, date_to, recipients, subject))
                                    if result.get('status') == 'success':
                                        st.success(f"✅ Report sent to: {', '.join(recipients)}")
                                    else:
                                        st.error(f"❌ Error: {result.get('message')}")
                                except Exception as e:
                                    st.error(f"❌ Unexpected error: {e}")

        st.caption("Note: The assistant collects parameters only. The actual data querying and email are performed by MCP servers.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>MCP Reports Agent | Powered by <a href='https://github.com/modelcontextprotocol/python-sdk'>MCP Python SDK</a> & OpenAI</p>
        <p>© 2025 - Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

