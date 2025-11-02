# MCP Good Queries

Generate crypto transaction summaries from PostgreSQL via MCP and email them with Gmail. Includes a Streamlit web UI and an optional OpenAI-powered chat to collect parameters and trigger the report.

## 🎯 MCP SDK Implementation

This project uses the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to expose proper MCP servers, and a Streamlit UI (with optional OpenAI chat) to run reports.

**Key Features:**
- ✅ LLM-compatible (works with Claude Desktop)
- ✅ Follows the MCP standard protocol
- ✅ Dynamic tool discovery
- ✅ Part of the MCP ecosystem
- 📚 See [MCP_SDK_GUIDE.md](MCP_SDK_GUIDE.md) for a complete guide
- 🌐 Streamlit web app to configure and send reports
- 🧠 Optional LLM chat (OpenAI) to collect parameters interactively

## 📋 Architecture

```
[Claude/LLM/User] → [agent_mcp.py (MCP Client)]
                         ↓
                         ├─→ [mcp_server_postgres.py (MCP Server)] → PostgreSQL
                         └─→ [mcp_server_gmail.py (MCP Server)] → Gmail
```

**Components:**
- **agent_mcp.py** – MCP client/orchestrator
- **mcp_server_postgres.py** – MCP server exposing DB tools
- **mcp_server_gmail.py** – MCP server exposing email tools
- **report_generator.py** – HTML/CSV generator (legacy helper)

## 🛠️ Prerequisites

- Python 3.9+
- PostgreSQL 12+ (local or remote)
- Gmail account (App Password recommended for dev)
- Optional: OpenAI API key for chat

## 📦 Installation

### 1) Install dependencies

```bash
cd mcp-reports-agent
pip install -r requirements.txt
```

### 2) Environment variables

Copy the example and edit your values:

```bash
cp .env.example .env
```

Example `.env` (OAuth2 fields optional if using App Password):

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=postgres
DB_PASS=your_password

# Gmail OAuth2
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# O usar App Password (más simple)
GMAIL_APP_PASSWORD=your_16_char_app_password
GMAIL_FROM=your_email@gmail.com

# Optional LLM (Streamlit chat)
# OPENAI_API_KEY=sk-your_api_key
```

### 3) Initialize the database

```bash
psql -h localhost -U postgres -d reports_db -f init_db.sql
```

### 4) (Optional) Load data from Excel

Place your file and run:

```bash
python3 load_crypto_transactions.py --file /path/to/transacciones_cripto.xlsx
```

Expected columns (case/accents tolerant): `fecha, usuario, tipo_transaccion, criptomoneda, monto, tc`.


#### Opción A: App Password (Recomendado para desarrollo)

1. Ve a https://myaccount.google.com/apppasswords
2. Genera una contraseña de aplicación para "Mail"
3. Usa esa contraseña en `GMAIL_APP_PASSWORD`

#### Opción B: OAuth2 (Producción)

1. Ve a Google Cloud Console
2. Crea un proyecto y habilita Gmail API
3. Crea credenciales OAuth2 (Desktop app)
4. Descarga el JSON y ejecuta:

```bash
python setup_gmail_oauth.py
```

## 🚀 Usage

### Streamlit Web UI

```bash
streamlit run app.py
```

Tabs:
- Form: pick dates, recipients, subject, and send the report.
- Chat (LLM): ask for a report in natural language; the assistant extracts parameters and triggers the email. Set `OPENAI_API_KEY` in `.env` or Streamlit secrets.

### Test MCP Servers

```bash
python3 agent_mcp.py --test
```

This will test both PostgreSQL and Gmail MCP servers and list available tools.

### Run the agent (CLI)

```bash
python3 agent_mcp.py
```

You will be asked for:
- Start date (YYYY-MM-DD)
- End date (YYYY-MM-DD)
- Recipients (comma-separated)

### Programmatic example

```python
import asyncio
from agent_mcp import MCPReportsAgent

async def generate_report():
    agent = MCPReportsAgent()
    result = await agent.generate_and_send_report(
        date_from="2025-10-01",
        date_to="2025-10-31",
        recipients=["finance@company.com", "management@company.com"],
        subject="Monthly Crypto Report"
    )
    print(result)

asyncio.run(generate_report())
```

### Use with Claude Desktop

Configure MCP servers in Claude Desktop. See [MCP_SDK_GUIDE.md](MCP_SDK_GUIDE.md).

## 📊 Project Structure

```
mcp-reports-agent/
├── README.md                   # Main documentation (this)
├── MCP_SDK_GUIDE.md            # MCP SDK guide
├── COMPARISON.md               # Implementation comparison
├── QUICKSTART.md               # Quick start
├── requirements.txt            # Dependencies (MCP, Streamlit, OpenAI)
├── env.example                 # Env template
├── init_db.sql                 # DB initialization
│
├── app.py                      # 🌐 Streamlit UI (Form + Chat)
├── .streamlit/
│   └── config.toml             # Streamlit theme/config
├── load_crypto_transactions.py # Excel loader → fact_transacciones_cripto
│
├── agent_mcp.py                # ⭐ MCP client/orchestrator
├── mcp_server_postgres.py      # MCP Server (PostgreSQL)
├── mcp_server_gmail.py         # MCP Server (Gmail)
├── report_generator.py         # HTML/CSV generator (legacy helper)
└── setup_gmail_oauth.py        # OAuth2 helper
```

## 🔒 Security

- ✅ Environment variables for credentials
- ✅ TLS connections to PostgreSQL (if enabled)
- ✅ No sensitive data in logs
- ✅ App Password (dev) or OAuth2 for Gmail (prod)

## 📧 Email Report (Crypto)

Body includes:
- Totals in period: purchased and sold (Σ amount × exchange_rate i.e., monto × tc)
- Top 5 clients by purchases (Σ amount × exchange_rate)
- Top 5 clients by sales (Σ amount × exchange_rate)
- Top 5 coins purchased (Σ amount × exchange_rate)
- Top 5 coins sold (Σ amount × exchange_rate)
- CSV attachment: period summary

Base table: `fact_transacciones_cripto(fecha, usuario, tipo_transaccion, criptomoneda, monto, tc)`

## 🐛 Troubleshooting

### PostgreSQL connection
```bash
# Ensure PostgreSQL is running
pg_isready -h localhost -p 5432

# Check credentials
psql -h localhost -U postgres -d reports_db
```

### Gmail authentication
```bash
# Ensure API enabled / App Password valid or OAuth2 tokens configured
```

### No results
The email explicitly states “No results for the selected period” when applicable.

## 📝 License

MIT

