"""
Report Generator - Generador de reportes HTML y CSV
Transforma datos de consultas SQL en reportes visuales y archivos adjuntos.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Template

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generador de reportes en formato HTML y CSV.
    Incluye KPIs, tablas y gráficos.
    """
    
    def __init__(self):
        """Inicializa el generador de reportes."""
        self.html_template = self._get_html_template()
    
    def generate_report(
        self,
        ventas_data: Dict[str, Any],
        kpis_data: Dict[str, Any],
        top_productos_data: Dict[str, Any],
        comparacion_data: Optional[Dict[str, Any]] = None,
        date_from: str = "",
        date_to: str = ""
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo con HTML y CSV.
        
        Args:
            ventas_data: Datos de ventas del periodo
            kpis_data: KPIs agregados
            top_productos_data: Top productos
            comparacion_data: Comparación con periodo anterior
            date_from: Fecha inicio
            date_to: Fecha fin
        
        Returns:
            Dict con 'html' y 'csv'
        """
        try:
            # Extraer KPIs
            kpis = self._extract_kpis(kpis_data, comparacion_data)
            
            # Generar HTML
            html = self._generate_html(
                ventas_data=ventas_data,
                kpis=kpis,
                top_productos_data=top_productos_data,
                date_from=date_from,
                date_to=date_to
            )
            
            # Generar CSV
            csv = self._generate_csv(ventas_data)
            
            logger.info("✅ Reporte generado exitosamente")
            return {
                "html": html,
                "csv": csv,
                "kpis": kpis
            }
            
        except Exception as e:
            logger.error(f"❌ Error al generar reporte: {e}")
            raise
    
    def _extract_kpis(
        self,
        kpis_data: Dict[str, Any],
        comparacion_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extrae y formatea los KPIs.
        
        Args:
            kpis_data: Datos de KPIs de la consulta
            comparacion_data: Datos de comparación
        
        Returns:
            Dict con KPIs formateados
        """
        if not kpis_data.get('rows') or len(kpis_data['rows']) == 0:
            return {
                "total_ventas": 0,
                "promedio_venta": 0,
                "total_transacciones": 0,
                "total_productos_vendidos": 0,
                "clientes_unicos": 0,
                "productos_unicos": 0,
                "variacion_porcentual": 0,
                "tiene_datos": False
            }
        
        # Primera fila de KPIs
        row = kpis_data['rows'][0]
        columns = kpis_data['columns']
        
        # Crear diccionario de KPIs
        kpis_dict = dict(zip(columns, row))
        
        # Formatear KPIs
        kpis = {
            "total_ventas": float(kpis_dict.get('total_ventas', 0) or 0),
            "promedio_venta": float(kpis_dict.get('promedio_venta', 0) or 0),
            "total_transacciones": int(kpis_dict.get('total_transacciones', 0) or 0),
            "total_productos_vendidos": int(kpis_dict.get('total_productos_vendidos', 0) or 0),
            "clientes_unicos": int(kpis_dict.get('clientes_unicos', 0) or 0),
            "productos_unicos": int(kpis_dict.get('productos_unicos', 0) or 0),
            "variacion_porcentual": 0,
            "tiene_datos": True
        }
        
        # Agregar variación si está disponible
        if comparacion_data and comparacion_data.get('rows'):
            comp_row = comparacion_data['rows'][0]
            comp_columns = comparacion_data['columns']
            comp_dict = dict(zip(comp_columns, comp_row))
            kpis["variacion_porcentual"] = float(comp_dict.get('variacion_porcentual', 0) or 0)
        
        return kpis
    
    def _generate_html(
        self,
        ventas_data: Dict[str, Any],
        kpis: Dict[str, Any],
        top_productos_data: Dict[str, Any],
        date_from: str,
        date_to: str
    ) -> str:
        """
        Genera el HTML del reporte.
        
        Args:
            ventas_data: Datos de ventas
            kpis: KPIs calculados
            top_productos_data: Top productos
            date_from: Fecha inicio
            date_to: Fecha fin
        
        Returns:
            HTML como string
        """
        # Preparar datos para la plantilla
        context = {
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodo_desde": date_from,
            "periodo_hasta": date_to,
            "kpis": kpis,
            "tiene_datos": kpis.get("tiene_datos", False),
            "ventas": self._format_table_data(ventas_data),
            "top_productos": self._format_table_data(top_productos_data),
        }
        
        # Renderizar plantilla
        template = Template(self.html_template)
        html = template.render(**context)
        
        return html
    
    def _format_table_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Formatea datos de tabla para la plantilla.
        
        Args:
            data: Datos con columns y rows
        
        Returns:
            Lista de diccionarios
        """
        if not data.get('rows'):
            return []
        
        columns = data['columns']
        rows = data['rows']
        
        result = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Formatear valores numéricos
                if isinstance(value, (int, float)):
                    if col in ['importe', 'ventas_totales', 'precio_unitario', 'total_ventas', 'promedio_venta']:
                        row_dict[col] = f"${value:,.2f}"
                    elif col in ['cantidad', 'cantidad_total', 'num_transacciones']:
                        row_dict[col] = f"{int(value):,}"
                    else:
                        row_dict[col] = value
                else:
                    row_dict[col] = value
            result.append(row_dict)
        
        return result
    
    def _generate_csv(self, ventas_data: Dict[str, Any]) -> str:
        """
        Genera CSV con los datos de ventas.
        
        Args:
            ventas_data: Datos de ventas
        
        Returns:
            CSV como string
        """
        if not ventas_data.get('rows'):
            return "Sin datos para el periodo especificado"
        
        columns = ventas_data['columns']
        rows = ventas_data['rows']
        
        # Header
        csv_lines = [','.join(columns)]
        
        # Rows
        for row in rows:
            # Escapar valores con comas
            escaped_row = []
            for value in row:
                if value is None:
                    escaped_row.append('')
                elif isinstance(value, str) and (',' in value or '"' in value):
                    escaped_row.append(f'"{value.replace(chr(34), chr(34)+chr(34))}"')
                else:
                    escaped_row.append(str(value))
            csv_lines.append(','.join(escaped_row))
        
        return '\n'.join(csv_lines)
    
    def _get_html_template(self) -> str:
        """
        Retorna la plantilla HTML del reporte.
        
        Returns:
            Template HTML
        """
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Ventas</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            color: #2c3e50;
            margin: 0 0 10px 0;
        }
        .meta {
            color: #7f8c8d;
            font-size: 14px;
        }
        .kpis {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .kpi-card.green {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .kpi-card.blue {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .kpi-card.orange {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        .kpi-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
        }
        .kpi-change {
            font-size: 14px;
            margin-top: 5px;
        }
        .kpi-change.positive {
            color: #a8ff78;
        }
        .kpi-change.negative {
            color: #ff6b6b;
        }
        .section {
            margin-bottom: 30px;
        }
        h2 {
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background-color: white;
        }
        th {
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .no-data {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-style: italic;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Reporte de Ventas</h1>
            <div class="meta">
                <strong>Periodo:</strong> {{ periodo_desde }} al {{ periodo_hasta }}<br>
                <strong>Generado:</strong> {{ fecha_generacion }}
            </div>
        </div>

        {% if tiene_datos %}
        <!-- KPIs -->
        <div class="kpis">
            <div class="kpi-card green">
                <div class="kpi-label">Total Ventas</div>
                <div class="kpi-value">${{ "%.2f"|format(kpis.total_ventas)|replace(',', 'X')|replace('.', ',')|replace('X', '.') }}</div>
                {% if kpis.variacion_porcentual != 0 %}
                <div class="kpi-change {{ 'positive' if kpis.variacion_porcentual > 0 else 'negative' }}">
                    {{ "%.1f"|format(kpis.variacion_porcentual) }}% vs periodo anterior
                </div>
                {% endif %}
            </div>
            
            <div class="kpi-card blue">
                <div class="kpi-label">Promedio por Venta</div>
                <div class="kpi-value">${{ "%.2f"|format(kpis.promedio_venta) }}</div>
            </div>
            
            <div class="kpi-card orange">
                <div class="kpi-label">Total Transacciones</div>
                <div class="kpi-value">{{ kpis.total_transacciones }}</div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">Productos Vendidos</div>
                <div class="kpi-value">{{ kpis.total_productos_vendidos }}</div>
            </div>
            
            <div class="kpi-card green">
                <div class="kpi-label">Clientes Únicos</div>
                <div class="kpi-value">{{ kpis.clientes_unicos }}</div>
            </div>
            
            <div class="kpi-card blue">
                <div class="kpi-label">Productos Únicos</div>
                <div class="kpi-value">{{ kpis.productos_unicos }}</div>
            </div>
        </div>

        <!-- Top Productos -->
        {% if top_productos|length > 0 %}
        <div class="section">
            <h2>🏆 Top Productos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Categoría</th>
                        <th>Cantidad</th>
                        <th>Ventas Totales</th>
                        <th>Transacciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for producto in top_productos %}
                    <tr>
                        <td><strong>{{ producto.producto }}</strong></td>
                        <td>{{ producto.categoria }}</td>
                        <td>{{ producto.cantidad_total }}</td>
                        <td>{{ producto.ventas_totales }}</td>
                        <td>{{ producto.num_transacciones }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- Detalle de Ventas (primeras 20 filas) -->
        {% if ventas|length > 0 %}
        <div class="section">
            <h2>📋 Detalle de Ventas {% if ventas|length > 20 %}(Primeras 20){% endif %}</h2>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Producto</th>
                        <th>Cliente</th>
                        <th>Cantidad</th>
                        <th>Importe</th>
                        <th>Región</th>
                    </tr>
                </thead>
                <tbody>
                    {% for venta in ventas[:20] %}
                    <tr>
                        <td>{{ venta.fecha }}</td>
                        <td>{{ venta.producto }}</td>
                        <td>{{ venta.cliente }}</td>
                        <td>{{ venta.cantidad }}</td>
                        <td>{{ venta.importe }}</td>
                        <td>{{ venta.region }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% if ventas|length > 20 %}
            <p style="text-align: center; color: #7f8c8d; font-style: italic;">
                Mostrando 20 de {{ ventas|length }} transacciones. Ver archivo CSV adjunto para datos completos.
            </p>
            {% endif %}
        </div>
        {% endif %}

        {% else %}
        <!-- Sin datos -->
        <div class="no-data">
            <h2>⚠️ Sin Resultados</h2>
            <p>No se encontraron datos para el periodo especificado.</p>
            <p><strong>Periodo:</strong> {{ periodo_desde }} al {{ periodo_hasta }}</p>
        </div>
        {% endif %}

        <div class="footer">
            Reporte generado automáticamente por MCP Reports Agent<br>
            © 2025 - Todos los derechos reservados
        </div>
    </div>
</body>
</html>
        """


# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo
    ventas_data = {
        "columns": ["fecha", "producto", "categoria", "cliente", "cantidad", "precio_unitario", "importe", "region"],
        "rows": [
            ["2025-10-01", "Laptop Dell", "Electrónica", "Empresa A", 5, 1200.00, 6000.00, "Norte"],
            ["2025-10-02", "Mouse", "Accesorios", "Empresa B", 20, 25.00, 500.00, "Sur"]
        ]
    }
    
    kpis_data = {
        "columns": ["total_transacciones", "total_ventas", "promedio_venta", "total_productos_vendidos", "clientes_unicos", "productos_unicos"],
        "rows": [[34, 73215.00, 2153.38, 495, 26, 14]]
    }
    
    top_productos_data = {
        "columns": ["producto", "categoria", "cantidad_total", "ventas_totales", "num_transacciones"],
        "rows": [
            ["Laptop Dell XPS", "Electrónica", 15, 18000.00, 3],
            ["Monitor LG 27\"", "Electrónica", 23, 8050.00, 3]
        ]
    }
    
    comparacion_data = {
        "columns": ["periodo_actual", "periodo_anterior", "variacion_porcentual"],
        "rows": [[73215.00, 14515.00, 404.38]]
    }
    
    # Generar reporte
    generator = ReportGenerator()
    report = generator.generate_report(
        ventas_data=ventas_data,
        kpis_data=kpis_data,
        top_productos_data=top_productos_data,
        comparacion_data=comparacion_data,
        date_from="2025-10-01",
        date_to="2025-10-31"
    )
    
    print("✅ HTML generado:", len(report['html']), "caracteres")
    print("✅ CSV generado:", len(report['csv']), "caracteres")
    print("\nKPIs:", report['kpis'])

