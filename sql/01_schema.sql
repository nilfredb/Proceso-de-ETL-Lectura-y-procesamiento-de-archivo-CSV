USE OpinionesDB;
GO

-- CLIENTES
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Clientes' AND schema_id=SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Clientes(
      IdCliente INT NOT NULL PRIMARY KEY,
      Nombre NVARCHAR(120) NOT NULL,
      Email NVARCHAR(190) NULL UNIQUE
    );
END
GO

-- PRODUCTOS
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Productos' AND schema_id=SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Productos(
      IdProducto INT NOT NULL PRIMARY KEY,
      Nombre NVARCHAR(160) NOT NULL,
      Categoria NVARCHAR(80) NULL
    );
END
GO

-- FUENTES
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Fuentes' AND schema_id=SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Fuentes(
      IdFuente VARCHAR(10) NOT NULL PRIMARY KEY,
      TipoFuente NVARCHAR(60) NOT NULL,
      FechaCarga DATE NULL
    );
END
GO

-- ENCUESTAS
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Encuestas' AND schema_id=SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Encuestas(
      IdOpinion INT NOT NULL PRIMARY KEY,
      IdCliente INT NULL,
      IdProducto INT NULL,
      Fecha DATE NULL,
      Comentario NVARCHAR(MAX) NULL,
      Clasificacion NVARCHAR(20) NULL,
      PuntajeSatisfaccion TINYINT NULL,
      FuenteTexto NVARCHAR(80) NULL
    );
END
GO

-- COMENTARIOS SOCIALES
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='ComentariosSociales' AND schema_id=SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.ComentariosSociales(
      IdComment VARCHAR(20) NOT NULL PRIMARY KEY,
      IdCliente INT NULL,
      IdProducto INT NULL,
      FuenteTexto NVARCHAR(80) NULL,
      Fecha DATE NULL,
      Comentario NVARCHAR(MAX) NULL
    );
END
GO

-- RESEÑAS WEB
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='ResenasWeb' AND schema_id=SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.ResenasWeb(
      IdReview VARCHAR(20) NOT NULL PRIMARY KEY,
      IdCliente INT NULL,
      IdProducto INT NULL,
      Fecha DATE NULL,
      Comentario NVARCHAR(MAX) NULL,
      Rating TINYINT NULL
    );
END
GO

/* ===== FKs (solo si faltan) ===== */
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Encuestas_Cliente')
    ALTER TABLE dbo.Encuestas ADD CONSTRAINT FK_Encuestas_Cliente
    FOREIGN KEY (IdCliente) REFERENCES dbo.Clientes(IdCliente);
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Encuestas_Producto')
    ALTER TABLE dbo.Encuestas ADD CONSTRAINT FK_Encuestas_Producto
    FOREIGN KEY (IdProducto) REFERENCES dbo.Productos(IdProducto);
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Social_Cliente')
    ALTER TABLE dbo.ComentariosSociales ADD CONSTRAINT FK_Social_Cliente
    FOREIGN KEY (IdCliente) REFERENCES dbo.Clientes(IdCliente);
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Social_Producto')
    ALTER TABLE dbo.ComentariosSociales ADD CONSTRAINT FK_Social_Producto
    FOREIGN KEY (IdProducto) REFERENCES dbo.Productos(IdProducto);
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Resenas_Cliente')
    ALTER TABLE dbo.ResenasWeb ADD CONSTRAINT FK_Resenas_Cliente
    FOREIGN KEY (IdCliente) REFERENCES dbo.Clientes(IdCliente);
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Resenas_Producto')
    ALTER TABLE dbo.ResenasWeb ADD CONSTRAINT FK_Resenas_Producto
    FOREIGN KEY (IdProducto) REFERENCES dbo.Productos(IdProducto);
GO

/* ===== Índices (solo si faltan) ===== */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Encuestas_IdCliente' AND object_id=OBJECT_ID('dbo.Encuestas'))
    CREATE INDEX IX_Encuestas_IdCliente  ON dbo.Encuestas(IdCliente);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Encuestas_IdProducto' AND object_id=OBJECT_ID('dbo.Encuestas'))
    CREATE INDEX IX_Encuestas_IdProducto ON dbo.Encuestas(IdProducto);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Social_IdCliente' AND object_id=OBJECT_ID('dbo.ComentariosSociales'))
    CREATE INDEX IX_Social_IdCliente     ON dbo.ComentariosSociales(IdCliente);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Social_IdProducto' AND object_id=OBJECT_ID('dbo.ComentariosSociales'))
    CREATE INDEX IX_Social_IdProducto    ON dbo.ComentariosSociales(IdProducto);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Web_IdCliente' AND object_id=OBJECT_ID('dbo.ResenasWeb'))
    CREATE INDEX IX_Web_IdCliente        ON dbo.ResenasWeb(IdCliente);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_Web_IdProducto' AND object_id=OBJECT_ID('dbo.ResenasWeb'))
    CREATE INDEX IX_Web_IdProducto       ON dbo.ResenasWeb(IdProducto);
GO
