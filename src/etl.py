import os, re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text
from utils_db import make_engine, ensure_database, run_sql_file

# config inicial
load_dotenv()
SERVER   = os.getenv("MSSQL_SERVER", "localhost") # uso whindows auth para mas sencillo
DB       = os.getenv("MSSQL_DB", "OpinionesDB")
DRIVER   = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
DATA_DIR = os.path.abspath(os.getenv("DATA_DIR", "./data"))

# Helpers para limpieza
def parse_prefixed_int(x, prefix):
    if pd.isna(x): return pd.NA
    s = str(x).strip()
    if s == "": return pd.NA
    if s.isdigit(): return int(s)
    m = re.match(rf"^{prefix}\s*0*([0-9]+)$", s, flags=re.IGNORECASE)
    if m: return int(m.group(1))
    m2 = re.search(r"([0-9]+)$", s)
    return int(m2.group(1)) if m2 else pd.NA

def to_date(x):
    try:
        return pd.to_datetime(x, errors="coerce").date()
    except Exception:
        return pd.NaT

def clean_text(x):
    if pd.isna(x): return None
    s = str(x).strip()
    return s if s else None

def strip_accents_headers(df):
    # Renombra encabezados con tildes a sin tildes para mejorar compatibilidad
    ren = {}
    for col in df.columns:
        c = col
        c = c.replace("Categoría","Categoria")
        c = c.replace("Clasificación","Clasificacion")
        c = c.replace("PuntajeSatisfacción","PuntajeSatisfaccion")
        ren[col] = c
    return df.rename(columns=ren)

def read_csv(name):
    return pd.read_csv(os.path.join(DATA_DIR, name), dtype=str)

def main():
    # Asegurar BD y engine
    ensure_database(server=SERVER, driver=DRIVER, db=DB)
    engine = make_engine(server=SERVER, db=DB, driver=DRIVER)

    # DDL
    run_sql_file(engine, os.path.join(os.path.dirname(__file__), "..", "sql", "01_schema.sql"))

    # Leer CSV como texto
    clientes  = read_csv("clients.csv")
    fuentes   = read_csv("fuente_datos.csv")
    productos = read_csv("products.csv")
    social    = read_csv("social_comments.csv")
    encuestas = read_csv("surveys_part1.csv")
    web       = read_csv("web_reviews.csv")

    # Normalizar encabezados con tildes 
    productos = strip_accents_headers(productos)
    encuestas = strip_accents_headers(encuestas)

    # Limpieza 

    # Clientes
    clientes["IdCliente"] = clientes["IdCliente"].apply(lambda v: parse_prefixed_int(v, "C")).astype("Int64")
    clientes["Nombre"] = clientes["Nombre"].map(clean_text)
    clientes["Email"]  = clientes["Email"].map(clean_text)
    clientes = clientes.drop_duplicates(subset=["IdCliente"]).dropna(subset=["IdCliente"])

    # Productos
    productos["IdProducto"] = productos["IdProducto"].apply(lambda v: parse_prefixed_int(v, "P")).astype("Int64")
    productos["Nombre"]     = productos["Nombre"].map(clean_text)
    productos["Categoria"]  = productos["Categoria"].map(clean_text)
    productos = productos.drop_duplicates(subset=["IdProducto"]).dropna(subset=["IdProducto"])

    # Fuentes
    fuentes["IdFuente"]   = fuentes["IdFuente"].str.strip()
    fuentes["TipoFuente"] = fuentes["TipoFuente"].map(clean_text)
    fuentes["FechaCarga"] = fuentes["FechaCarga"].map(to_date)
    fuentes = fuentes.drop_duplicates(subset=["IdFuente"]).dropna(subset=["IdFuente"])

    # Social
    social["IdComment"]  = social["IdComment"].str.strip()
    social["IdCliente"]  = social["IdCliente"].apply(lambda v: parse_prefixed_int(v, "C")).astype("Int64")
    social["IdProducto"] = social["IdProducto"].apply(lambda v: parse_prefixed_int(v, "P")).astype("Int64")
    social["FuenteTexto"]= social.get("Fuente", pd.Series([None]*len(social))).map(clean_text)
    social["Fecha"]      = social["Fecha"].map(to_date)
    social["Comentario"] = social["Comentario"].map(clean_text)
    social = social.drop_duplicates(subset=["IdComment"]).dropna(subset=["IdComment"])
    if "Fuente" in social.columns:
        social = social.drop(columns=["Fuente"], errors="ignore")

    # Encuestas
    encuestas["IdOpinion"] = pd.to_numeric(encuestas["IdOpinion"], errors="coerce").astype("Int64")
    encuestas["IdCliente"] = encuestas["IdCliente"].apply(lambda v: parse_prefixed_int(v, "C")).astype("Int64")
    encuestas["IdProducto"]= encuestas["IdProducto"].apply(lambda v: parse_prefixed_int(v, "P")).astype("Int64")
    encuestas["Fecha"]     = encuestas["Fecha"].map(to_date)
    encuestas["Comentario"]= encuestas["Comentario"].map(clean_text)
    encuestas["Clasificacion"] = encuestas["Clasificacion"].map(clean_text)
    encuestas["PuntajeSatisfaccion"] = pd.to_numeric(encuestas["PuntajeSatisfaccion"], errors="coerce").astype("Int64")
    encuestas["FuenteTexto"]= encuestas.get("Fuente", pd.Series([None]*len(encuestas))).map(clean_text)
    encuestas = encuestas.drop_duplicates(subset=["IdOpinion"]).dropna(subset=["IdOpinion"])
    if "Fuente" in encuestas.columns:
        encuestas = encuestas.drop(columns=["Fuente"], errors="ignore")

    # Web
    web["IdReview"]  = web["IdReview"].str.strip()
    web["IdCliente"] = web["IdCliente"].apply(lambda v: parse_prefixed_int(v, "C")).astype("Int64")
    web["IdProducto"]= web["IdProducto"].apply(lambda v: parse_prefixed_int(v, "P")).astype("Int64")
    web["Fecha"]     = web["Fecha"].map(to_date)
    web["Comentario"]= web["Comentario"].map(clean_text)
    web["Rating"]    = pd.to_numeric(web["Rating"], errors="coerce").astype("Int64")
    web = web.drop_duplicates(subset=["IdReview"]).dropna(subset=["IdReview"])

    # 6) Carga 
    with engine.begin() as conn:
        # Dimensiones
        for _, r in clientes.iterrows():
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Clientes WHERE IdCliente = :id)
                INSERT INTO dbo.Clientes(IdCliente,Nombre,Email)
                VALUES(:id,:nombre,:email);
            """), {"id": int(r["IdCliente"]), "nombre": r["Nombre"], "email": r["Email"]})

        for _, r in productos.iterrows():
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Productos WHERE IdProducto = :id)
                INSERT INTO dbo.Productos(IdProducto,Nombre,Categoria)
                VALUES(:id,:nombre,:cat);
            """), {"id": int(r["IdProducto"]), "nombre": r["Nombre"], "cat": r["Categoria"]})

        for _, r in fuentes.iterrows():
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Fuentes WHERE IdFuente = :id)
                INSERT INTO dbo.Fuentes(IdFuente,TipoFuente,FechaCarga)
                VALUES(:id,:tipo,:fecha);
            """), {"id": r["IdFuente"], "tipo": r["TipoFuente"], "fecha": r["FechaCarga"]})

        # Conjuntos validos en dimensiones
        clientes_validos = set(x[0] for x in conn.execute(text("SELECT IdCliente FROM dbo.Clientes")).all())
        productos_validos = set(x[0] for x in conn.execute(text("SELECT IdProducto FROM dbo.Productos")).all())

        # Hechos: Encuestas
        for _, r in encuestas.iterrows():
            idc = int(r["IdCliente"])  if pd.notna(r["IdCliente"])  and int(r["IdCliente"])  in clientes_validos else None
            idp = int(r["IdProducto"]) if pd.notna(r["IdProducto"]) and int(r["IdProducto"]) in productos_validos else None
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Encuestas WHERE IdOpinion = :idop)
                INSERT INTO dbo.Encuestas(IdOpinion,IdCliente,IdProducto,Fecha,Comentario,Clasificacion,PuntajeSatisfaccion,FuenteTexto)
                VALUES(:idop,:idc,:idp,:fecha,:coment,:clas,:punt,:fuente);
            """), {
                "idop": int(r["IdOpinion"]),
                "idc":  idc,
                "idp":  idp,
                "fecha": r["Fecha"],
                "coment": r["Comentario"],
                "clas":  r["Clasificacion"],
                "punt":  int(r["PuntajeSatisfaccion"]) if pd.notna(r["PuntajeSatisfaccion"]) else None,
                "fuente": r["FuenteTexto"]
            })

        # Hechos: Comentarios Sociales
        for _, r in social.iterrows():
            idc = int(r["IdCliente"])  if pd.notna(r["IdCliente"])  and int(r["IdCliente"])  in clientes_validos else None
            idp = int(r["IdProducto"]) if pd.notna(r["IdProducto"]) and int(r["IdProducto"]) in productos_validos else None
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.ComentariosSociales WHERE IdComment = :idcmt)
                INSERT INTO dbo.ComentariosSociales(IdComment,IdCliente,IdProducto,FuenteTexto,Fecha,Comentario)
                VALUES(:idcmt,:idc,:idp,:fuente,:fecha,:coment);
            """), {
                "idcmt": r["IdComment"],
                "idc":  idc,
                "idp":  idp,
                "fuente": r["FuenteTexto"],
                "fecha": r["Fecha"],
                "coment": r["Comentario"]
            })

        # Hechos: Reseñas Web
        for _, r in web.iterrows():
            idc = int(r["IdCliente"])  if pd.notna(r["IdCliente"])  and int(r["IdCliente"])  in clientes_validos else None
            idp = int(r["IdProducto"]) if pd.notna(r["IdProducto"]) and int(r["IdProducto"]) in productos_validos else None
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.ResenasWeb WHERE IdReview = :idr)
                INSERT INTO dbo.ResenasWeb(IdReview,IdCliente,IdProducto,Fecha,Comentario,Rating)
                VALUES(:idr,:idc,:idp,:fecha,:coment,:rating);
            """), {
                "idr": r["IdReview"],
                "idc":  idc,
                "idp":  idp,
                "fecha": r["Fecha"],
                "coment": r["Comentario"],
                "rating": int(r["Rating"]) if pd.notna(r["Rating"]) else None
            })

    print("ETL completado correctamente con Windows Authentication y FKs seguras.")

if __name__ == "__main__":
    main()
