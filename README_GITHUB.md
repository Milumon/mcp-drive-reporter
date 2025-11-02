# 📊 MCP Drive Reporter

> **Automated Sales Reports from PostgreSQL to Email using MCP SDK**

A powerful reporting agent that uses the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to generate sales reports from PostgreSQL and send them via Gmail. Includes a beautiful Streamlit web interface for easy report generation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-SDK-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🤖 **MCP SDK Integration** - Uses official Model Context Protocol SDK
- 🌐 **Streamlit Web UI** - Beautiful, user-friendly interface (Form + Chat)
- 🧠 **LLM Assistant (OpenAI)** - Optional chat to collect parameters and trigger the report
- 📊 **Automated KPIs** - Total sales, averages, top products, and more
- 📧 **Email Reports** - HTML reports with CSV attachments
- 🔒 **Secure** - OAuth2 support, environment variables, TLS connections
- 🎯 **LLM Compatible** - Works with Claude Desktop and other MCP clients
- 📈 **Dynamic Queries** - Flexible date ranges and custom SQL support

---

## 🎬 Demo

### Streamlit Web Interface

![Streamlit UI](/Users/jvegal/01_projects/02_sundaihack/20251102/mcp-reports-agent/screenshot_app.png)

### Email Report Example (Crypto)

The generated crypto reports include (based on Σ monto × tc):
- 📊 Totals purchased and sold in period
- 👤 Top 5 clients by purchases
- 👤 Top 5 clients by sales
- 💠 Top 5 coins purchased
- 💠 Top 5 coins sold
- 📎 CSV attachment (summary)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Gmail account with App Password

### Installation

```bash
# Clone the repository
git clone https://github.com/Milumon/mcp-drive-reporter.git
cd mcp-drive-reporter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb reports_db
psql -d reports_db -f init_db.sql

# Configure environment
cp env.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` file:

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=your_username
DB_PASS=your_password

# Gmail
GMAIL_FROM=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate password for "Mail"
3. Copy the 16-character password (no spaces)

**Optional (LLM Chat):**

Add your OpenAI key either in shell or `.env`/Streamlit secrets:

```bash
export OPENAI_API_KEY=sk-...yourkey...
```

---

## 💻 Usage

### Option 1: Streamlit Web Interface (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

Tabs:
- Form: choose date range, recipients, subject, and send the report.
- Chat (LLM): ask for a report in natural language; the assistant extracts the parameters and triggers the email.

### Option 2: Command Line

```bash
# Interactive mode
python3 agent_mcp.py

# Test MCP servers
python3 agent_mcp.py --test
```

### Option 3: Claude Desktop Integration

Configure in `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "postgres-reports": {
      "command": "python3",
      "args": ["/path/to/mcp_server_postgres.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_NAME": "reports_db",
        "DB_USER": "your_user"
      }
    },
    "gmail-reports": {
      "command": "python3",
      "args": ["/path/to/mcp_server_gmail.py"],
      "env": {
        "GMAIL_FROM": "your@gmail.com",
        "GMAIL_APP_PASSWORD": "your_password"
      }
    }
  }
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Streamlit Web UI (app.py)           │
│              or Claude Desktop              │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      MCP Client (agent_mcp.py)              │
└────────┬───────────────────────┬────────────┘
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────────┐
│ PostgreSQL MCP │      │   Gmail MCP        │
│    Server      │      │    Server          │
│                │      │                    │
│ • query_ventas │      │ • send_email       │
│ • get_kpis     │      │ • send_simple      │
│ • top_products │      │                    │
└────────┬───────┘      └──────────┬─────────┘
         │                         │
         ▼                         ▼
    PostgreSQL                  Gmail SMTP
```

---

## 📂 Project Structure

```
mcp-drive-reporter/
├── app.py                      # 🌐 Streamlit web interface (Form + Chat)
├── agent_mcp.py                # 🤖 MCP client/orchestrator
├── mcp_server_postgres.py      # 🗄️ PostgreSQL MCP server
├── mcp_server_gmail.py         # 📧 Gmail MCP server
├── report_generator.py         # 📊 Report generation
├── setup_gmail_oauth.py        # 🔐 OAuth2 helper
├── init_db.sql                 # 🗃️ Database initialization
├── requirements.txt            # 📦 Dependencies (MCP, Streamlit, OpenAI)
├── env.example                 # ⚙️ Configuration template
└── .streamlit/
    └── config.toml             # 🎨 Streamlit theme
```

---

## 📚 Documentation

- **[MCP SDK Guide](MCP_SDK_GUIDE.md)** - Complete MCP SDK documentation
- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Comparison](COMPARISON.md)** - Implementation details
- **[Step-by-Step Guide](GUIA_PASO_A_PASO.md)** - Detailed tutorial (Spanish)

---

## 🛠️ MCP Tools

### PostgreSQL Server Tools (Crypto)

| Tool | Description |
|------|-------------|
| `top_clientes_compra` | Top clients by purchases in date range (Σ monto × tc) |
| `top_clientes_venta` | Top clients by sales in date range (Σ monto × tc) |
| `top_monedas_compra` | Top coins purchased in date range (Σ monto × tc) |
| `top_monedas_venta` | Top coins sold in date range (Σ monto × tc) |
| `totales_compra_venta` | Totals purchased and sold (Σ monto × tc) |
| `execute_custom_query` | Execute custom SQL queries |

### Gmail Server Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send HTML email with attachments |
| `send_simple_email` | Send plain text email |

---

## 🧪 Testing

```bash
# Test MCP servers
python3 agent_mcp.py --test

# Run with sample data
python3 agent_mcp.py
```

---

## 🔒 Security

- ✅ Environment variables for credentials
- ✅ OAuth2 support for Gmail
- ✅ TLS/SSL for PostgreSQL
- ✅ Parameterized SQL queries
- ✅ No sensitive data in logs
- ✅ App Password support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Model Context Protocol SDK
- [Streamlit](https://streamlit.io/) - Beautiful web framework
- [PostgreSQL](https://www.postgresql.org/) - Powerful database
- [Gmail API](https://developers.google.com/gmail/api) - Email integration

---

## 📞 Support

- 📖 [Documentation](README.md)
- 🐛 [Issues](https://github.com/Milumon/mcp-drive-reporter/issues)
- 💬 [Discussions](https://github.com/Milumon/mcp-drive-reporter/discussions)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ using MCP SDK**

