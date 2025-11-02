# MCP Reports Agent - Reto 1

Agente de reportes que ejecuta consultas en PostgreSQL mediante un MCP, genera reportes (tabla y métricas) y los envía por correo usando un MCP de Gmail.

## 🎯 MCP SDK Implementation

This project uses the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to create proper MCP servers that can be used by LLMs like Claude.

**Key Features:**
- ✅ LLM-compatible (works with Claude Desktop)
- ✅ Follows MCP standard protocol
- ✅ Dynamic tool discovery
- ✅ Part of the MCP ecosystem
- 📚 See [MCP_SDK_GUIDE.md](MCP_SDK_GUIDE.md) for complete guide

## 📋 Arquitectura

```
[Claude/LLM/User] → [agent_mcp.py (MCP Client)]
                         ↓
                         ├─→ [mcp_server_postgres.py (MCP Server)] → PostgreSQL
                         └─→ [mcp_server_gmail.py (MCP Server)] → Gmail
```

**Components:**
- **agent_mcp.py** - MCP client that orchestrates the workflow
- **mcp_server_postgres.py** - MCP server exposing database tools
- **mcp_server_gmail.py** - MCP server exposing email tools
- **report_generator.py** - Shared report generation module

## 🛠️ Requisitos Previos

- Python 3.9+
- PostgreSQL 12+ (local o remoto)
- Cuenta de Gmail con OAuth2 configurado
- Google Cloud Project con Gmail API habilitada

## 📦 Instalación

### 1. Clonar e instalar dependencias

```bash
cd mcp-reports-agent
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=postgres
DB_PASS=tu_password

# Gmail OAuth2
GMAIL_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=tu_client_secret
GMAIL_REFRESH_TOKEN=tu_refresh_token

# O usar App Password (más simple)
GMAIL_APP_PASSWORD=tu_app_password_16_caracteres
GMAIL_FROM=tu_email@gmail.com
```

### 3. Inicializar la base de datos

```bash
psql -h localhost -U postgres -d reports_db -f init_db.sql
```

### 4. Configurar Gmail OAuth2

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

## 🚀 Uso

### Test MCP Servers

```bash
python3 agent_mcp.py --test
```

This will test both PostgreSQL and Gmail MCP servers and list available tools.

### Ejecutar el agente manualmente

```bash
python3 agent_mcp.py
```

El agente te pedirá los parámetros del reporte:
- Fecha desde (YYYY-MM-DD)
- Fecha hasta (YYYY-MM-DD)
- Destinatarios (emails separados por coma)

### Ejemplo de uso programático

```python
import asyncio
from agent_mcp import MCPReportsAgent

async def generate_report():
    agent = MCPReportsAgent()
    result = await agent.generate_and_send_report(
        date_from="2025-10-01",
        date_to="2025-10-31",
        recipients=["finanzas@empresa.com", "gerencia@empresa.com"],
        subject="Reporte Mensual de Ventas"
    )
    print(result)

asyncio.run(generate_report())
```

### Usar con Claude Desktop

Configura los servidores MCP en Claude Desktop. Ver [MCP_SDK_GUIDE.md](MCP_SDK_GUIDE.md) para detalles de configuración.

## 📊 Estructura del Proyecto

```
mcp-reports-agent/
├── README.md                   # Documentación principal
├── MCP_SDK_GUIDE.md           # Guía completa del MCP SDK
├── COMPARISON.md              # Comparación de implementaciones
├── QUICKSTART.md              # Inicio rápido
├── requirements.txt           # Dependencias (incluye MCP SDK)
├── env.example                # Template de configuración
├── init_db.sql                # Inicialización de BD
│
├── agent_mcp.py               # ⭐ MCP Client/Orchestrator
├── mcp_server_postgres.py     # MCP Server para PostgreSQL
├── mcp_server_gmail.py        # MCP Server para Gmail
├── report_generator.py        # Generador de reportes HTML/CSV
└── setup_gmail_oauth.py       # Helper para OAuth2
```

## 🔒 Seguridad

- ✅ Credenciales en variables de entorno (no en código)
- ✅ Conexiones TLS a PostgreSQL
- ✅ No se registran datos sensibles en logs
- ✅ Tokens OAuth2 almacenados de forma segura

## 📧 Formato del Reporte

El correo incluye:
- **Asunto**: Configurable
- **Cuerpo HTML**: 
  - 3+ KPIs principales (Total Ventas, Promedio, Variación %)
  - Tabla con los datos consultados
  - Top 5 productos/clientes
- **Adjunto CSV**: Datos completos en formato tabular

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL está corriendo
pg_isready -h localhost -p 5432

# Verificar credenciales
psql -h localhost -U postgres -d reports_db
```

### Error de autenticación Gmail
```bash
# Verificar que la API está habilitada
# Regenerar App Password o refresh token
```

### Consulta sin resultados
El agente envía un correo indicando "Sin resultados para el periodo especificado"

## 📝 Licencia

MIT

