# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base  # mejor práctica

# Base para modelos declarativos
Base = declarative_base()

# Define la URL de la base de datos SQLite (archivo local llamado 'usuarios.db')
DATABASE_URL = "sqlite:///./usuarios.db"

# Configura el engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crea la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Función que se usará como dependencia en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
