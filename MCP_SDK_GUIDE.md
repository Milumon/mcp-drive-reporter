# 🎯 MCP SDK Implementation Guide

This guide explains the refactored implementation using the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).

---

## 🏗️ New Architecture

### Before (Custom Implementation)
```
agent.py → mcp_postgres.py → PostgreSQL
         → mcp_gmail.py → Gmail
```

### After (MCP SDK)
```
agent_mcp.py (MCP Client)
    ↓
    ├─→ mcp_server_postgres.py (MCP Server) → PostgreSQL
    └─→ mcp_server_gmail.py (MCP Server) → Gmail
```

---

## 📦 New Files

| File | Description | Type |
|------|-------------|------|
| `mcp_server_postgres.py` | PostgreSQL MCP Server | Server |
| `mcp_server_gmail.py` | Gmail MCP Server | Server |
| `agent_mcp.py` | MCP Client/Orchestrator | Client |
| `MCP_SDK_GUIDE.md` | This guide | Docs |

---

## 🚀 Installation

### 1. Install New Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install MCP SDK and dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python3 -c "import mcp; print(f'MCP SDK version: {mcp.__version__}')"
```

---

## 🎯 Usage

### Test MCP Servers

```bash
# Test both MCP servers
python3 agent_mcp.py --test
```

Expected output:
```
Testing PostgreSQL MCP server...
✅ PostgreSQL MCP: 4 tools available
   - query_ventas: Query sales data...
   - get_kpis: Get aggregated KPIs...
   - get_top_productos: Get top N products...
   - execute_custom_query: Execute a custom SQL query...

Testing Gmail MCP server...
✅ Gmail MCP: 2 tools available
   - send_email: Send an email via Gmail...
   - send_simple_email: Send a simple text email...
```

### Generate and Send Report

```bash
# Interactive mode
python3 agent_mcp.py
```

### Run Individual MCP Servers

```bash
# Run PostgreSQL server standalone
python3 mcp_server_postgres.py

# Run Gmail server standalone
python3 mcp_server_gmail.py
```

---

## 🔧 MCP Server Details

### PostgreSQL MCP Server

**Tools Exposed:**

1. **`query_ventas`** - Query sales data
   ```json
   {
     "date_from": "2025-10-01",
     "date_to": "2025-10-31"
   }
   ```

2. **`get_kpis`** - Get aggregated KPIs
   ```json
   {
     "date_from": "2025-10-01",
     "date_to": "2025-10-31"
   }
   ```

3. **`get_top_productos`** - Get top products
   ```json
   {
     "date_from": "2025-10-01",
     "date_to": "2025-10-31",
     "limit": 5
   }
   ```

4. **`execute_custom_query`** - Execute custom SQL
   ```json
   {
     "sql": "SELECT * FROM ventas LIMIT 10"
   }
   ```

### Gmail MCP Server

**Tools Exposed:**

1. **`send_email`** - Send email with attachments
   ```json
   {
     "to": ["user@example.com"],
     "subject": "Report",
     "body_html": "<h1>Report</h1>",
     "attachments": [
       {
         "filename": "report.csv",
         "content_base64": "..."
       }
     ]
   }
   ```

2. **`send_simple_email`** - Send simple text email
   ```json
   {
     "to": "user@example.com",
     "subject": "Hello",
     "body": "This is a test"
   }
   ```

---

## 🤖 Using with Claude Desktop

### 1. Configure MCP Servers in Claude

Add to Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "postgres-reports": {
      "command": "python3",
      "args": ["/path/to/mcp-reports-agent/mcp_server_postgres.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "reports_db",
        "DB_USER": "jvegal",
        "DB_PASS": ""
      }
    },
    "gmail-reports": {
      "command": "python3",
      "args": ["/path/to/mcp-reports-agent/mcp_server_gmail.py"],
      "env": {
        "GMAIL_FROM": "your@gmail.com",
        "GMAIL_APP_PASSWORD": "your_app_password"
      }
    }
  }
}
```

### 2. Use in Claude

Now you can ask Claude:

> "Query our sales database for October 2025 and email the report to finance@company.com"

Claude will:
1. Call `query_ventas` tool from postgres-reports server
2. Call `get_kpis` tool for metrics
3. Call `send_email` tool from gmail-reports server

---

## 📊 Comparison: Old vs New

| Aspect | Custom (Old) | MCP SDK (New) |
|--------|-------------|---------------|
| **Architecture** | Direct calls | Client-Server |
| **Protocol** | Custom | MCP Standard |
| **LLM Integration** | ❌ No | ✅ Yes |
| **Tool Discovery** | Hardcoded | Dynamic |
| **Claude Desktop** | ❌ No | ✅ Yes |
| **Reusability** | Limited | High |
| **Complexity** | Simple | Moderate |

---

## 🎓 Key Concepts

### 1. MCP Servers

MCP servers expose **tools** (functions) that can be called by clients:

```python
from mcp.server import Server

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [Tool(name="my_tool", ...)]

@server.call_tool()
async def call_tool(name, arguments):
    # Execute tool
    return result
```

### 2. MCP Clients

MCP clients connect to servers and call tools:

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("my_tool", {...})
```

### 3. MCP Primitives

| Primitive | Description | Example |
|-----------|-------------|---------|
| **Tools** | Functions the LLM can call | `query_database`, `send_email` |
| **Resources** | Data the LLM can read | File contents, API responses |
| **Prompts** | Templates for interactions | Slash commands |

---

## 🔄 Migration Path

### Keep Both Implementations

You can use both:

**Old (Simple automation):**
```bash
python3 agent.py --from 2025-10-01 --to 2025-10-31 --recipients user@email.com
```

**New (MCP-based):**
```bash
python3 agent_mcp.py
```

**With Claude:**
- Configure MCP servers in Claude Desktop
- Ask Claude to generate reports conversationally

---

## 🐛 Troubleshooting

### MCP Server Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check MCP installation
pip show mcp

# Run with debug logging
python3 mcp_server_postgres.py
```

### Tool Calls Fail

```bash
# Test server independently
python3 agent_mcp.py --test

# Check .env configuration
cat .env
```

### Claude Desktop Can't Find Servers

1. Check config file path
2. Verify absolute paths in config
3. Restart Claude Desktop
4. Check Claude logs

---

## 📚 Resources

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Documentation](https://modelcontextprotocol.github.io/python-sdk/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Registry](https://github.com/modelcontextprotocol/servers)

---

## 🎯 Next Steps

1. ✅ Test MCP servers: `python3 agent_mcp.py --test`
2. ✅ Generate a report: `python3 agent_mcp.py`
3. ✅ Configure Claude Desktop (optional)
4. ✅ Explore adding more tools to servers
5. ✅ Create custom MCP servers for other services

---

**Questions?** Check the [official documentation](https://modelcontextprotocol.github.io/python-sdk/) or the examples in the SDK repository.

