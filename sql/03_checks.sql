USE OpinionesDB;
GO

SELECT 'Clientes' AS Tabla, COUNT(*) AS Registros FROM dbo.Clientes
UNION ALL
SELECT 'Productos', COUNT(*) FROM dbo.Productos
UNION ALL
SELECT 'Fuentes',   COUNT(*) FROM dbo.Fuentes
UNION ALL
SELECT 'Encuestas', COUNT(*) FROM dbo.Encuestas
UNION ALL
SELECT 'ComentariosSociales', COUNT(*) FROM dbo.ComentariosSociales
UNION ALL
SELECT 'ResenasWeb', COUNT(*) FROM dbo.ResenasWeb;
GO

SELECT TOP 10 * FROM dbo.Clientes ORDER BY IdCliente;
SELECT TOP 10 * FROM dbo.Productos ORDER BY IdProducto;
SELECT TOP 10 * FROM dbo.Fuentes   ORDER BY IdFuente;
SELECT TOP 10 * FROM dbo.Encuestas ORDER BY IdOpinion;
SELECT TOP 10 * FROM dbo.ComentariosSociales ORDER BY IdComment;
SELECT TOP 10 * FROM dbo.ResenasWeb ORDER BY IdReview;
GO

-- Chequeo de FKs nulas (por datos incompletos)
SELECT COUNT(*) AS Nulos_Cliente_Encuestas  FROM dbo.Encuestas WHERE IdCliente IS NULL;
SELECT COUNT(*) AS Nulos_Producto_Encuestas FROM dbo.Encuestas WHERE IdProducto IS NULL;
SELECT COUNT(*) AS Nulos_Cliente_Social     FROM dbo.ComentariosSociales WHERE IdCliente IS NULL;
SELECT COUNT(*) AS Nulos_Producto_Social    FROM dbo.ComentariosSociales WHERE IdProducto IS NULL;
SELECT COUNT(*) AS Nulos_Cliente_Web        FROM dbo.ResenasWeb WHERE IdCliente IS NULL;
SELECT COUNT(*) AS Nulos_Producto_Web       FROM dbo.ResenasWeb WHERE IdProducto IS NULL;
GO
