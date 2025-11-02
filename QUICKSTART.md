# ⚡ Quick Start - Agente de Reportes

**¿Quieres empezar rápido?** Sigue estos 5 pasos.

## 🚀 Inicio Rápido (5 minutos)

### 1️⃣ Instalar Dependencias

```bash
cd mcp-reports-agent
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Configurar PostgreSQL

```bash
# Crear base de datos
psql -U postgres -c "CREATE DATABASE reports_db;"

# Inicializar datos de ejemplo
psql -U postgres -d reports_db -f init_db.sql
```

### 3️⃣ Configurar Variables de Entorno

```bash
# Copiar template
cp env.example .env

# Editar .env con tus credenciales
nano .env  # o usa tu editor favorito
```

Configura al menos:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=postgres
DB_PASS=tu_password

GMAIL_FROM=tu_email@gmail.com
GMAIL_APP_PASSWORD=uhhg cqwx qqgh ksmg 
```

**Obtener App Password de Gmail:**
1. Ve a https://myaccount.google.com/apppasswords
2. Genera una contraseña para "Correo"
3. Copia los 16 caracteres (sin espacios)

### 4️⃣ Probar Conexiones

```bash
python3 agent.py --test
```

Deberías ver:
```
✅ PostgreSQL: success
✅ Gmail: success
```

### 5️⃣ Generar Tu Primer Reporte

```bash
python3 agent.py \
  --from 2025-10-01 \
  --to 2025-10-31 \
  --recipients tu_email@gmail.com
```

**¡Revisa tu correo!** 📧

---

## 📚 Documentación Completa

- **Tutorial Completo**: [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md)
- **Documentación Técnica**: [README.md](README.md)
- **Resumen del Proyecto**: [RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)

---

## 🆘 Problemas Comunes

### Error de conexión a PostgreSQL
```bash
# Verificar que está corriendo
pg_isready -h localhost -p 5432

# Iniciar PostgreSQL
# macOS: brew services start postgresql@14
# Linux: sudo systemctl start postgresql
```

### Error de autenticación Gmail
- Verifica que tienes verificación en 2 pasos habilitada
- Regenera la App Password
- Asegúrate de copiar los 16 caracteres sin espacios

### No llega el correo
- Revisa la carpeta de SPAM
- Verifica que `GMAIL_FROM` es correcto
- Ejecuta `python3 agent.py --test`

---

## 🎯 Próximos Pasos

1. ✅ Personaliza las consultas SQL en `mcp_postgres.py`
2. ✅ Modifica el template HTML en `report_generator.py`
3. ✅ Automatiza con CRON (ver `cron_examples.sh`)
4. ✅ Revisa ejemplos en `example_usage.py`

---

**¿Necesitas ayuda?** Consulta [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) para instrucciones detalladas.

