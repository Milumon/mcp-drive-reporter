-- Crear la base de datos
CREATE DATABASE CriptoTransacciones
GO

USE CriptoTransacciones
GO

-- Crear esquema para organizar los objetos
CREATE SCHEMA cripto
GO

-- Crear tabla principal de transacciones
CREATE TABLE cripto.transacciones_cripto (
    id_transaccion INT PRIMARY KEY IDENTITY(1,1),
    fecha DATETIME NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    tipo_transaccion VARCHAR(20) NOT NULL,
    criptomoneda VARCHAR(20) NOT NULL,
    monto DECIMAL(18,8) NOT NULL,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    CONSTRAINT chk_tipo_transaccion CHECK (tipo_transaccion IN ('Compra', 'Venta', 'Transferencia')),
    CONSTRAINT df_fecha_creacion DEFAULT GETDATE() FOR fecha_creacion
);

-- Crear índices para mejorar el rendimiento
CREATE NONCLUSTERED INDEX IX_transacciones_cripto_fecha
ON cripto.transacciones_cripto(fecha);

CREATE NONCLUSTERED INDEX IX_transacciones_cripto_usuario
ON cripto.transacciones_cripto(usuario);

CREATE NONCLUSTERED INDEX IX_transacciones_cripto_tipo
ON cripto.transacciones_cripto(tipo_transaccion);

CREATE NONCLUSTERED INDEX IX_transacciones_cripto_cripto
ON cripto.transacciones_cripto(criptomoneda);

-- Crear vista para el resumen diario de transacciones
CREATE VIEW cripto.vw_resumen_diario AS
SELECT 
    CAST(fecha AS DATE) as fecha,
    criptomoneda,
    tipo_transaccion,
    COUNT(*) as total_transacciones,
    SUM(monto) as monto_total
FROM cripto.transacciones_cripto
GROUP BY CAST(fecha AS DATE), criptomoneda, tipo_transaccion;
GO

-- Crear procedimiento almacenado para insertar transacciones
CREATE PROCEDURE cripto.sp_insertar_transaccion
    @fecha DATETIME,
    @usuario VARCHAR(50),
    @tipo_transaccion VARCHAR(20),
    @criptomoneda VARCHAR(20),
    @monto DECIMAL(18,8)
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO cripto.transacciones_cripto (fecha, usuario, tipo_transaccion, criptomoneda, monto)
    VALUES (@fecha, @usuario, @tipo_transaccion, @criptomoneda, @monto);
    
    SELECT SCOPE_IDENTITY() as id_transaccion;
END;
GO

-- Crear procedimiento para obtener el historial de un usuario
CREATE PROCEDURE cripto.sp_historial_usuario
    @usuario VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        fecha,
        tipo_transaccion,
        criptomoneda,
        monto
    FROM cripto.transacciones_cripto
    WHERE usuario = @usuario
    ORDER BY fecha DESC;
END;
GO

-- Habilitar configuraciones necesarias
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'Ad Hoc Distributed Queries', 1;
RECONFIGURE;

-- Insertar datos desde Excel
INSERT INTO transacciones_cripto (fecha, usuario, tipo_transaccion, criptomoneda, monto)
SELECT 
    CONVERT(DATETIME, [fecha]),
    [usuario],
    [tipo_transaccion],
    [criptomoneda],
    CONVERT(DECIMAL(18,8), [monto])
FROM OPENROWSET(
    'Microsoft.ACE.OLEDB.12.0',
    'Excel 12.0; Database=C:\Users\OBLIVIUS\Desktop\transacciones_cripto.xlsx',
    'SELECT * FROM [Sheet1$]'
);

-- Deshabilitar configuraciones
EXEC sp_configure 'Ad Hoc Distributed Queries', 0;
RECONFIGURE;
EXEC sp_configure 'show advanced options', 0;
RECONFIGURE;

-- Insertar algunos datos de ejemplo
INSERT INTO transacciones_cripto (fecha, usuario, tipo_transaccion, criptomoneda, monto)
VALUES 
    ('2025-08-02', 'fernando_1203', 'Compra', 'Bitcoin', 0.07);