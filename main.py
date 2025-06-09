# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import auth  # este archivo lo vamos a crear
from routers import divorcio_admin
from routers import divorcio_incausado
from routers import divorcio_voluntario
from routers import guarda_custodia
from routers import pension_alimenticia
from routers import reconocimiento
from routers import historial
from routers import resumen_admin
from routers import resumen_incausado
from routers import resumen_voluntario
from routers import resumen_alimentos
from routers import resumen_guarda
from routers import resumen_reconocimiento

app = FastAPI()
# Crear las tablas definidas en models.py
Base.metadata.create_all(bind=engine)

# Configurar CORS para permitir conexiones desde tu frontend
origins = [
    "http://localhost:5173",                     # para desarrollo local
    "https://famlez-front.vercel.app",          # tu dominio en producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de autenticación
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(divorcio_admin.router)
app.include_router(divorcio_incausado.router)
app.include_router(divorcio_voluntario.router)
app.include_router(guarda_custodia.router)
app.include_router(pension_alimenticia.router)
app.include_router(reconocimiento.router)
app.include_router(historial.router)
# Rutas de resumen por tipo de demanda
app.include_router(resumen_admin.router)
app.include_router(resumen_voluntario.router)
app.include_router(resumen_incausado.router)
app.include_router(resumen_alimentos.router)
app.include_router(resumen_reconocimiento.router)
app.include_router(resumen_guarda.router)