README – Proyecto de Análisis de Opiniones de Clientes
=====================================================

📌 Descripción
--------------
Este proyecto implementa un pipeline ETL (Extract, Transform, Load) en Python para cargar datos de opiniones de clientes desde múltiples fuentes CSV en una base de datos SQL Server.

El objetivo es integrar información de clientes, productos, fuentes de datos, encuestas, comentarios en redes sociales y reseñas web en un esquema centralizado (OpinionesDB) para facilitar análisis posteriores.

⚙️ Tecnologías
--------------
- Python 3.11+
- pandas para transformación de datos
- SQLAlchemy + pyodbc para conexión con SQL Server
- dotenv para configuración
- SQL Server 2019/2022 (o Express)
- Windows Authentication (sin usuario/contraseña)

📂 Estructura del proyecto
--------------------------
opiniones/
├─ data/                   # CSV de entrada
│  ├─ clients.csv
│  ├─ fuente_datos.csv
│  ├─ products.csv
│  ├─ social_comments.csv
│  ├─ surveys_part1.csv
│  └─ web_reviews.csv
├─ sql/
│  ├─ 01_schema.sql        # Definición idempotente del esquema
│  └─ 03_checks.sql        # Consultas de verificación
├─ src/
│  ├─ etl.py               # Proceso ETL principal
│  └─ utils_db.py          # Conexión y utilidades SQL Server
├─ .env                    # Configuración (servidor, base, driver, rutas)
├─ requirements.txt        # Dependencias Python
└─ README.txt              # Documentación

⚡ Instalación
--------------
1. Clonar repositorio:
   git clone https://github.com/nilfredb/Proceso-de-ETL-Lectura-y-procesamiento-de-archivo-CSV.git
   cd opiniones

2. Instalar dependencias:
   pip install -r requirements.txt

3. Configuración .env:
   MSSQL_SERVER=localhost          # o NOMBREPC\SQLEXPRESS
   MSSQL_DB=OpinionesDB
   MSSQL_DRIVER=ODBC Driver 18 for SQL Server
   DATA_DIR=./data
   
🚀 Ejecución del ETL
--------------------
python .\src\etl.py

El proceso realiza:
1. Asegura la base de datos (OpinionesDB).
2. Crea el esquema de tablas (idempotente, sin borrar nada).
3. Carga CSVs desde la carpeta data/.
4. Limpieza y transformación (IDs, fechas, texto, duplicados).
5. Carga en SQL Server:
   - Inserta dimensiones (Clientes, Productos, Fuentes).
   - Inserta hechos (Encuestas, ComentariosSociales, ResenasWeb).
   - Si un IdCliente o IdProducto no existe en su dimensión, se inserta NULL.

📊 Verificación
---------------
1. Con SQL Server Management Studio (SSMS):
   USE OpinionesDB;
   SELECT TOP 20 * FROM dbo.Clientes;
   SELECT TOP 20 * FROM dbo.Productos;
   SELECT TOP 20 * FROM dbo.Encuestas;

2. Script de checks:
   :r sql\03_checks.sql

