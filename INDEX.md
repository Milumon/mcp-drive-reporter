# 📑 Índice General - Agente de Reportes MCP

## 🎯 Bienvenido

Este es el **Agente de Reportes MCP** - una solución completa para generar y enviar reportes automatizados desde PostgreSQL vía Gmail.

---

## 🚀 ¿Por Dónde Empezar?

### Si eres nuevo aquí:
1. 📄 **[QUICKSTART.md](QUICKSTART.md)** - Empieza aquí (5 minutos)
2. 📄 **[GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md)** - Tutorial completo

### Si quieres entender el proyecto:
1. 📄 **[RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)** - Resumen ejecutivo
2. 📄 **[PRESENTACION_RETO.md](../PRESENTACION_RETO.md)** - Presentación del reto

### Si quieres usar el agente:
1. 📄 **[README.md](README.md)** - Documentación técnica completa
2. 💡 **[example_usage.py](example_usage.py)** - Ejemplos de uso

---

## 📚 Documentación

### Documentos Principales

| Documento | Descripción | Audiencia | Tiempo |
|-----------|-------------|-----------|--------|
| **[QUICKSTART.md](QUICKSTART.md)** | Inicio rápido en 5 pasos | Todos | 5 min |
| **[GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md)** | Tutorial completo desde cero | Principiantes | 30 min |
| **[README.md](README.md)** | Documentación técnica | Desarrolladores | 15 min |
| **[RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)** | Resumen ejecutivo | Gerentes/Líderes | 10 min |
| **[PRESENTACION_RETO.md](../PRESENTACION_RETO.md)** | Presentación del reto | Evaluadores | 10 min |

---

## 🐍 Código Fuente

### Componentes Principales

| Archivo | Descripción | LOC | Complejidad |
|---------|-------------|-----|-------------|
| **[agent.py](agent.py)** | ⭐ Orquestador principal | ~400 | Media |
| **[mcp_postgres.py](mcp_postgres.py)** | MCP PostgreSQL | ~350 | Media |
| **[mcp_gmail.py](mcp_gmail.py)** | MCP Gmail | ~300 | Media |
| **[report_generator.py](report_generator.py)** | Generador de reportes | ~450 | Alta |

### Scripts de Soporte

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| **[test_agent.py](test_agent.py)** | Tests automatizados | `pytest test_agent.py` |
| **[example_usage.py](example_usage.py)** | Ejemplos de uso | `python3 example_usage.py` |
| **[setup_gmail_oauth.py](setup_gmail_oauth.py)** | Helper OAuth2 | `python3 setup_gmail_oauth.py` |
| **[cron_examples.sh](cron_examples.sh)** | Ejemplos CRON | Ver contenido |

### Configuración

| Archivo | Descripción | Acción Requerida |
|---------|-------------|------------------|
| **[requirements.txt](requirements.txt)** | Dependencias Python | `pip install -r requirements.txt` |
| **[env.example](env.example)** | Template de .env | Copiar a `.env` y editar |
| **[init_db.sql](init_db.sql)** | Script de BD | `psql -f init_db.sql` |

---

## 🎯 Flujos de Trabajo

### 1. Instalación Inicial

```
QUICKSTART.md (Paso 1-3)
    ↓
requirements.txt → pip install
    ↓
env.example → .env (editar)
    ↓
init_db.sql → PostgreSQL
```

### 2. Primer Uso

```
agent.py --test (verificar)
    ↓
agent.py (modo interactivo)
    ↓
¡Reporte enviado! 📧
```

### 3. Desarrollo/Personalización

```
README.md (entender arquitectura)
    ↓
example_usage.py (ver ejemplos)
    ↓
Modificar mcp_postgres.py (consultas)
    ↓
Modificar report_generator.py (diseño)
    ↓
test_agent.py (probar cambios)
```

### 4. Producción

```
GUIA_PASO_A_PASO.md (Sección 7)
    ↓
cron_examples.sh (configurar)
    ↓
Monitorear logs
```

---

## 🔍 Búsqueda Rápida

### ¿Cómo...?

| Pregunta | Respuesta |
|----------|-----------|
| **¿Cómo instalar?** | [QUICKSTART.md](QUICKSTART.md) - Paso 1 |
| **¿Cómo configurar PostgreSQL?** | [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) - Sección 3 |
| **¿Cómo configurar Gmail?** | [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) - Sección 4 |
| **¿Cómo ejecutar?** | [README.md](README.md) - Sección "Uso" |
| **¿Cómo automatizar?** | [cron_examples.sh](cron_examples.sh) |
| **¿Cómo personalizar consultas?** | [mcp_postgres.py](mcp_postgres.py) - Clase `ReportQueries` |
| **¿Cómo personalizar HTML?** | [report_generator.py](report_generator.py) - Método `_get_html_template` |
| **¿Cómo ejecutar tests?** | `pytest test_agent.py -v` |
| **¿Cómo resolver problemas?** | [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) - Sección 8 |

---

## 🎓 Casos de Uso

### Por Tipo de Usuario

#### 👨‍💼 Gerente/Líder
- Leer: [RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)
- Entender qué hace el proyecto y sus beneficios

#### 👨‍💻 Desarrollador
- Leer: [README.md](README.md)
- Modificar: [mcp_postgres.py](mcp_postgres.py), [report_generator.py](report_generator.py)
- Probar: [test_agent.py](test_agent.py)

#### 🔧 DevOps/SysAdmin
- Leer: [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) - Sección 7
- Configurar: [cron_examples.sh](cron_examples.sh)
- Monitorear: Logs en terminal

#### 👤 Usuario Final
- Leer: [QUICKSTART.md](QUICKSTART.md)
- Ejecutar: `python3 agent.py` (modo interactivo)

---

## 📊 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  CAPA DE USUARIO                    │
│  • CLI (agent.py)                                   │
│  • Interactivo (agent.py)                           │
│  • Programático (import agent)                      │
│  • CRON (cron_examples.sh)                          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              CAPA DE ORQUESTACIÓN                   │
│  agent.py                                           │
│  • Coordina flujo completo                          │
│  • Manejo de errores                                │
│  • Logging                                          │
└────────┬───────────────────────────┬────────────────┘
         │                           │
┌────────▼──────────┐    ┌──────────▼────────────────┐
│   CAPA DE MCPs    │    │  CAPA DE GENERACIÓN       │
│                   │    │                           │
│ mcp_postgres.py   │    │ report_generator.py       │
│ • Consultas SQL   │    │ • HTML templates          │
│ • Pool conexión   │    │ • CSV generation          │
│ • Reintentos      │    │ • KPI extraction          │
│                   │    │                           │
│ mcp_gmail.py      │    │                           │
│ • SMTP/OAuth2     │    │                           │
│ • Adjuntos        │    │                           │
└───────────────────┘    └───────────────────────────┘
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest test_agent.py -v

# Tests específicos
pytest test_agent.py::TestReportGenerator -v

# Con cobertura
pytest test_agent.py --cov=. --cov-report=html
```

### Cobertura

| Componente | Cobertura | Tests |
|------------|-----------|-------|
| agent.py | ~85% | 5 tests |
| mcp_postgres.py | ~80% | 4 tests |
| mcp_gmail.py | ~75% | 3 tests |
| report_generator.py | ~90% | 8 tests |

---

## 🔧 Personalización

### Modificar Consultas SQL

Editar: [mcp_postgres.py](mcp_postgres.py)

```python
class ReportQueries:
    @staticmethod
    def tu_nueva_consulta(params):
        sql = "SELECT ..."
        return sql, params
```

### Modificar Template HTML

Editar: [report_generator.py](report_generator.py)

```python
def _get_html_template(self):
    return """
    <!DOCTYPE html>
    <html>
    ...
    """
```

### Agregar Nuevo MCP

1. Crear `mcp_nuevo.py`
2. Implementar clase `MCPNuevo`
3. Integrar en `agent.py`
4. Agregar tests en `test_agent.py`

---

## 📈 Roadmap

### Implementado ✅
- [x] MCP PostgreSQL
- [x] MCP Gmail
- [x] Generador de reportes HTML/CSV
- [x] Tests automatizados
- [x] Documentación completa
- [x] Ejemplos de uso
- [x] Automatización CRON

### Futuro 🚀
- [ ] Dashboard web (Flask/FastAPI)
- [ ] Gráficos embebidos (charts.js)
- [ ] MCP Slack
- [ ] MCP Telegram
- [ ] API REST
- [ ] Multi-tenant

---

## 📞 Soporte

### Recursos

| Recurso | Enlace |
|---------|--------|
| Documentación | Este repositorio |
| Issues | GitHub Issues |
| Ejemplos | [example_usage.py](example_usage.py) |
| Tests | [test_agent.py](test_agent.py) |

### Troubleshooting

Ver: [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) - Sección 8

---

## 📝 Licencia

MIT License - Ver archivo LICENSE (si existe)

---

## 🎉 ¡Empecemos!

**¿Listo para empezar?**

👉 **[QUICKSTART.md](QUICKSTART.md)** - ¡5 minutos para tu primer reporte!

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Producción

