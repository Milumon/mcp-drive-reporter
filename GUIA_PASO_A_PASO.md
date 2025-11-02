# 📚 Guía Paso a Paso - Agente de Reportes MCP

Esta guía te llevará desde cero hasta tener el agente funcionando completamente.

## 🎯 Índice

1. [Requisitos Previos](#1-requisitos-previos)
2. [Instalación](#2-instalación)
3. [Configuración de PostgreSQL](#3-configuración-de-postgresql)
4. [Configuración de Gmail](#4-configuración-de-gmail)
5. [Pruebas](#5-pruebas)
6. [Uso](#6-uso)
7. [Automatización](#7-automatización)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Requisitos Previos

### Software Necesario

- **Python 3.9+**
  ```bash
  python3 --version
  ```

- **PostgreSQL 12+**
  ```bash
  # macOS
  brew install postgresql@14
  brew services start postgresql@14
  
  # Ubuntu/Debian
  sudo apt update
  sudo apt install postgresql postgresql-contrib
  sudo systemctl start postgresql
  
  # Windows
  # Descargar desde: https://www.postgresql.org/download/windows/
  ```

- **Git** (opcional)
  ```bash
  git --version
  ```

### Cuentas Necesarias

- ✅ Cuenta de Gmail
- ✅ Acceso a PostgreSQL (local o remoto)
- ✅ (Opcional) Google Cloud Project para OAuth2

---

## 2. Instalación

### Paso 2.1: Clonar o Descargar el Proyecto

```bash
cd /ruta/donde/quieras/el/proyecto
# Si tienes el código, simplemente navega a la carpeta
cd mcp-reports-agent
```

### Paso 2.2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Paso 2.3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Deberías ver algo como:
```
Successfully installed psycopg2-binary-2.9.9 python-dotenv-1.0.0 ...
```

---

## 3. Configuración de PostgreSQL

### Paso 3.1: Crear Base de Datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Dentro de psql:
CREATE DATABASE reports_db;
\q
```

### Paso 3.2: Inicializar Datos de Ejemplo

```bash
psql -U postgres -d reports_db -f init_db.sql
```

Deberías ver:
```
CREATE TABLE
CREATE INDEX
INSERT 0 40
...
```

### Paso 3.3: Verificar Datos

```bash
psql -U postgres -d reports_db -c "SELECT COUNT(*) FROM ventas;"
```

Debería mostrar: `40` (o el número de filas insertadas)

### Paso 3.4: Configurar Credenciales

Crea el archivo `.env`:

```bash
cp env.example .env
```

Edita `.env` con tus credenciales:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=postgres
DB_PASS=tu_password_aqui
```

**⚠️ IMPORTANTE:** Reemplaza `tu_password_aqui` con tu contraseña real de PostgreSQL.

### Paso 3.5: Probar Conexión

```bash
python3 mcp_postgres.py
```

Deberías ver:
```
✅ Pool de conexiones PostgreSQL inicializado
=== Test de Conexión ===
{'status': 'success', 'message': 'Conexión exitosa', ...}
```

---

## 4. Configuración de Gmail

Tienes **dos opciones**: App Password (más fácil) u OAuth2 (más seguro).

### Opción A: App Password (Recomendado para Empezar)

#### Paso 4A.1: Habilitar Verificación en 2 Pasos

1. Ve a https://myaccount.google.com/security
2. Activa "Verificación en 2 pasos" si no la tienes

#### Paso 4A.2: Generar App Password

1. Ve a https://myaccount.google.com/apppasswords
2. Selecciona "Correo" y "Otro (nombre personalizado)"
3. Escribe "MCP Reports Agent"
4. Copia la contraseña de 16 caracteres (ej: `abcd efgh ijkl mnop`)

#### Paso 4A.3: Configurar en .env

Edita `.env` y agrega:

```env
GMAIL_FROM=tu_email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop  # Sin espacios
```

#### Paso 4A.4: Probar Conexión

```bash
python3 mcp_gmail.py
```

Deberías ver:
```
✅ MCP Gmail inicializado para: tu_email@gmail.com
=== Test de Conexión ===
{'status': 'success', 'message': 'Conexión exitosa a smtp.gmail.com'}
```

---

### Opción B: OAuth2 (Producción)

#### Paso 4B.1: Crear Proyecto en Google Cloud

1. Ve a https://console.cloud.google.com/
2. Crea un nuevo proyecto: "MCP Reports Agent"
3. Habilita la Gmail API:
   - Menú → APIs y servicios → Biblioteca
   - Busca "Gmail API" → Habilitar

#### Paso 4B.2: Crear Credenciales OAuth2

1. Menú → APIs y servicios → Credenciales
2. Crear credenciales → ID de cliente de OAuth
3. Tipo: "Aplicación de escritorio"
4. Nombre: "MCP Reports Desktop"
5. Descargar JSON → Guardar como `credentials.json`

#### Paso 4B.3: Ejecutar Setup

```bash
python3 setup_gmail_oauth.py
```

Sigue las instrucciones:
1. Ingresa la ruta a `credentials.json`
2. Se abrirá el navegador
3. Autoriza la aplicación
4. Las credenciales se guardarán automáticamente en `.env`

---

## 5. Pruebas

### Paso 5.1: Probar Conexiones

```bash
python3 agent.py --test
```

Deberías ver:
```
🔍 Probando conexiones...
✓ PostgreSQL: success
✓ Gmail: success
✅ Todas las conexiones funcionan correctamente
```

### Paso 5.2: Ejecutar Tests Automatizados

```bash
pytest test_agent.py -v
```

Deberías ver algo como:
```
test_agent.py::TestReportQueries::test_ventas_por_periodo PASSED
test_agent.py::TestReportGenerator::test_generate_report_with_data PASSED
...
==================== 20 passed in 2.34s ====================
```

### Paso 5.3: Generar Reporte de Prueba

```bash
python3 agent.py --from 2025-10-01 --to 2025-10-07 --recipients tu_email@gmail.com
```

**¡Revisa tu correo!** Deberías recibir un reporte con:
- ✅ HTML con KPIs y tablas
- ✅ Adjunto CSV con los datos

---

## 6. Uso

### Modo Interactivo

```bash
python3 agent.py
```

El agente te preguntará:
```
Fecha inicio (YYYY-MM-DD) [2025-10-25]: 2025-10-01
Fecha fin (YYYY-MM-DD) [2025-11-01]: 2025-10-31
Destinatarios (separados por coma): finanzas@empresa.com, gerencia@empresa.com
Asunto del correo (Enter para usar por defecto): 
```

### Modo Línea de Comandos

```bash
# Reporte de la última semana
python3 agent.py \
  --from 2025-10-25 \
  --to 2025-11-01 \
  --recipients "finanzas@empresa.com,gerencia@empresa.com" \
  --subject "Reporte Semanal"
```

### Modo Programático

Crea un script Python:

```python
from agent import ReportsAgent

agent = ReportsAgent()
result = agent.generate_and_send_report(
    date_from="2025-10-01",
    date_to="2025-10-31",
    recipients=["finanzas@empresa.com"],
    subject="Reporte Mensual"
)
print(result)
agent.close()
```

### Ejemplos de Uso

```bash
python3 example_usage.py
```

---

## 7. Automatización

### Opción A: CRON (Linux/macOS)

Edita el crontab:

```bash
crontab -e
```

Agrega una línea (ejemplo: todos los lunes a las 9 AM):

```cron
0 9 * * 1 cd /ruta/al/proyecto && /ruta/al/proyecto/venv/bin/python3 agent.py --auto --recipients "finanzas@empresa.com"
```

### Opción B: Task Scheduler (Windows)

1. Abre "Programador de tareas"
2. Crear tarea básica
3. Desencadenador: Semanal, Lunes, 9:00 AM
4. Acción: Iniciar programa
   - Programa: `C:\ruta\al\proyecto\venv\Scripts\python.exe`
   - Argumentos: `agent.py --auto --recipients "finanzas@empresa.com"`
   - Iniciar en: `C:\ruta\al\proyecto`

### Opción C: Script de Shell

Crea `run_weekly_report.sh`:

```bash
#!/bin/bash
cd /ruta/al/proyecto
source venv/bin/activate

# Calcular fechas de la semana pasada
python3 agent.py --auto \
  --recipients "finanzas@empresa.com,gerencia@empresa.com" \
  --subject "Reporte Semanal Automático"
```

Hazlo ejecutable:

```bash
chmod +x run_weekly_report.sh
```

---

## 8. Troubleshooting

### Error: "psycopg2.OperationalError: could not connect to server"

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
pg_isready -h localhost -p 5432

# Si no está corriendo, iniciarlo:
# macOS:
brew services start postgresql@14
# Linux:
sudo systemctl start postgresql
```

### Error: "SMTPAuthenticationError: Username and Password not accepted"

**Solución:**
1. Verifica que el email es correcto
2. Verifica que la App Password no tiene espacios
3. Asegúrate de tener verificación en 2 pasos habilitada
4. Regenera la App Password

### Error: "ModuleNotFoundError: No module named 'psycopg2'"

**Solución:**
```bash
# Asegúrate de que el entorno virtual está activado
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate  # Windows

# Reinstala dependencias
pip install -r requirements.txt
```

### El correo no llega

**Solución:**
1. Revisa la carpeta de SPAM
2. Verifica que `GMAIL_FROM` es correcto
3. Prueba con `python3 agent.py --test`
4. Revisa los logs en la terminal

### Error: "relation 'ventas' does not exist"

**Solución:**
```bash
# Reinicializa la base de datos
psql -U postgres -d reports_db -f init_db.sql
```

### Tests fallan

**Solución:**
```bash
# Asegúrate de que las variables de entorno están configuradas
cat .env

# Ejecuta tests con más detalle
pytest test_agent.py -v -s
```

---

## 🎉 ¡Felicidades!

Si llegaste hasta aquí, tu agente de reportes está completamente funcional.

### Próximos Pasos

1. **Personaliza las consultas SQL** en `mcp_postgres.py`
2. **Modifica el template HTML** en `report_generator.py`
3. **Agrega más KPIs** según tus necesidades
4. **Configura alertas** para valores específicos
5. **Integra con otros sistemas** (Slack, Telegram, etc.)

### Recursos Adicionales

- 📖 [README.md](README.md) - Documentación completa
- 🧪 [test_agent.py](test_agent.py) - Ejemplos de tests
- 💡 [example_usage.py](example_usage.py) - Ejemplos de uso
- 🐛 Issues: Abre un issue si encuentras problemas

---

**¿Necesitas ayuda?** Revisa la sección de Troubleshooting o abre un issue en el repositorio.

