-- Crear base de datos (ejecutar como superusuario)
-- CREATE DATABASE reports_db;

-- Conectar a la base de datos
\c reports_db;

-- Tabla de ventas de ejemplo
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    producto VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    cliente VARCHAR(100),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    importe DECIMAL(10, 2) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_producto ON ventas(producto);
CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente);

-- Insertar datos de ejemplo
INSERT INTO ventas (fecha, producto, categoria, cliente, cantidad, precio_unitario, importe, region) VALUES
-- Octubre 2025
('2025-10-01', 'Laptop Dell XPS', 'Electrónica', 'Empresa A', 5, 1200.00, 6000.00, 'Norte'),
('2025-10-01', 'Mouse Logitech', 'Accesorios', 'Empresa B', 20, 25.00, 500.00, 'Sur'),
('2025-10-02', 'Teclado Mecánico', 'Accesorios', 'Empresa A', 10, 80.00, 800.00, 'Norte'),
('2025-10-03', 'Monitor LG 27"', 'Electrónica', 'Empresa C', 8, 350.00, 2800.00, 'Centro'),
('2025-10-03', 'Webcam HD', 'Accesorios', 'Empresa D', 15, 60.00, 900.00, 'Este'),
('2025-10-04', 'Laptop HP Pavilion', 'Electrónica', 'Empresa B', 3, 900.00, 2700.00, 'Sur'),
('2025-10-05', 'Auriculares Sony', 'Accesorios', 'Empresa E', 25, 45.00, 1125.00, 'Oeste'),
('2025-10-05', 'SSD 1TB', 'Componentes', 'Empresa A', 12, 120.00, 1440.00, 'Norte'),
('2025-10-06', 'RAM 16GB', 'Componentes', 'Empresa C', 18, 80.00, 1440.00, 'Centro'),
('2025-10-07', 'Router WiFi', 'Redes', 'Empresa F', 7, 150.00, 1050.00, 'Norte'),
('2025-10-08', 'Laptop Dell XPS', 'Electrónica', 'Empresa G', 4, 1200.00, 4800.00, 'Sur'),
('2025-10-09', 'Impresora HP', 'Oficina', 'Empresa H', 2, 450.00, 900.00, 'Este'),
('2025-10-10', 'Tablet Samsung', 'Electrónica', 'Empresa I', 6, 400.00, 2400.00, 'Oeste'),
('2025-10-11', 'Mouse Logitech', 'Accesorios', 'Empresa J', 30, 25.00, 750.00, 'Centro'),
('2025-10-12', 'Monitor LG 27"', 'Electrónica', 'Empresa A', 5, 350.00, 1750.00, 'Norte'),
('2025-10-13', 'Teclado Mecánico', 'Accesorios', 'Empresa K', 8, 80.00, 640.00, 'Sur'),
('2025-10-14', 'Laptop HP Pavilion', 'Electrónica', 'Empresa L', 7, 900.00, 6300.00, 'Este'),
('2025-10-15', 'Webcam HD', 'Accesorios', 'Empresa M', 12, 60.00, 720.00, 'Oeste'),
('2025-10-16', 'SSD 1TB', 'Componentes', 'Empresa N', 15, 120.00, 1800.00, 'Norte'),
('2025-10-17', 'Auriculares Sony', 'Accesorios', 'Empresa O', 20, 45.00, 900.00, 'Centro'),
('2025-10-18', 'Router WiFi', 'Redes', 'Empresa P', 9, 150.00, 1350.00, 'Sur'),
('2025-10-19', 'RAM 16GB', 'Componentes', 'Empresa Q', 22, 80.00, 1760.00, 'Este'),
('2025-10-20', 'Laptop Dell XPS', 'Electrónica', 'Empresa R', 6, 1200.00, 7200.00, 'Oeste'),
('2025-10-21', 'Impresora HP', 'Oficina', 'Empresa S', 3, 450.00, 1350.00, 'Norte'),
('2025-10-22', 'Tablet Samsung', 'Electrónica', 'Empresa T', 8, 400.00, 3200.00, 'Centro'),
('2025-10-23', 'Mouse Logitech', 'Accesorios', 'Empresa U', 35, 25.00, 875.00, 'Sur'),
('2025-10-24', 'Monitor LG 27"', 'Electrónica', 'Empresa V', 10, 350.00, 3500.00, 'Este'),
('2025-10-25', 'Teclado Mecánico', 'Accesorios', 'Empresa W', 14, 80.00, 1120.00, 'Oeste'),
('2025-10-26', 'Laptop HP Pavilion', 'Electrónica', 'Empresa X', 5, 900.00, 4500.00, 'Norte'),
('2025-10-27', 'Webcam HD', 'Accesorios', 'Empresa Y', 18, 60.00, 1080.00, 'Centro'),
('2025-10-28', 'SSD 1TB', 'Componentes', 'Empresa Z', 20, 120.00, 2400.00, 'Sur'),
('2025-10-29', 'Auriculares Sony', 'Accesorios', 'Empresa A', 28, 45.00, 1260.00, 'Este'),
('2025-10-30', 'Router WiFi', 'Redes', 'Empresa B', 11, 150.00, 1650.00, 'Oeste'),
('2025-10-31', 'RAM 16GB', 'Componentes', 'Empresa C', 25, 80.00, 2000.00, 'Norte'),

-- Septiembre 2025 (para comparación)
('2025-09-01', 'Laptop Dell XPS', 'Electrónica', 'Empresa D', 4, 1200.00, 4800.00, 'Norte'),
('2025-09-05', 'Mouse Logitech', 'Accesorios', 'Empresa E', 15, 25.00, 375.00, 'Sur'),
('2025-09-10', 'Monitor LG 27"', 'Electrónica', 'Empresa F', 6, 350.00, 2100.00, 'Centro'),
('2025-09-15', 'Teclado Mecánico', 'Accesorios', 'Empresa G', 8, 80.00, 640.00, 'Este'),
('2025-09-20', 'Laptop HP Pavilion', 'Electrónica', 'Empresa H', 5, 900.00, 4500.00, 'Oeste'),
('2025-09-25', 'SSD 1TB', 'Componentes', 'Empresa I', 10, 120.00, 1200.00, 'Norte'),
('2025-09-30', 'Auriculares Sony', 'Accesorios', 'Empresa J', 20, 45.00, 900.00, 'Sur');

-- Verificar datos insertados
SELECT 
    DATE_TRUNC('month', fecha) as mes,
    COUNT(*) as total_transacciones,
    SUM(importe) as total_ventas
FROM ventas
GROUP BY DATE_TRUNC('month', fecha)
ORDER BY mes DESC;

COMMIT;

-- =============================
-- Nueva tabla: fact_transacciones_cripto
-- Base para cargas desde Excel/CSV
-- =============================

-- Esquema de transacciones cripto
CREATE TABLE IF NOT EXISTS fact_transacciones_cripto (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    usuario TEXT NOT NULL,
    tipo_transaccion TEXT NOT NULL,      -- compra, venta, deposito, retiro, etc.
    criptomoneda TEXT NOT NULL,          -- BTC, ETH, USDT, etc.
    monto NUMERIC(38, 10) NOT NULL,      -- cantidad de cripto o importe según convención
    tc NUMERIC(18, 8),                   -- tipo de cambio aplicado (opcional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices sugeridos
CREATE INDEX IF NOT EXISTS idx_ftc_fecha ON fact_transacciones_cripto(fecha);
CREATE INDEX IF NOT EXISTS idx_ftc_usuario ON fact_transacciones_cripto(usuario);
CREATE INDEX IF NOT EXISTS idx_ftc_cripto ON fact_transacciones_cripto(criptomoneda);

