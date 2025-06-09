from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from database import SessionLocal, HistorialDocumento
import os

router = APIRouter()

RUTA_DOCUMENTOS = "./backend"  # Ajusta si los archivos están en otra carpeta

@router.get("/historial")
def obtener_historial(usuario: str = Query(...)):
    session = SessionLocal()
    documentos = session.query(HistorialDocumento).filter_by(usuario=usuario).all()
    session.close()
    
    if not documentos:
        return []

    return [
        {
            "tipo": d.tipo,
            "archivo": d.nombre_archivo,
            "fecha": d.fecha_generacion.strftime("%d/%m/%Y %H:%M")
        }
        for d in documentos
    ]

@router.get("/descargar/{nombre_archivo}")
def descargar_documento(nombre_archivo: str):
    ruta_completa = os.path.join(RUTA_DOCUMENTOS, nombre_archivo)

    if not os.path.exists(ruta_completa):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(path=ruta_completa, filename=nombre_archivo, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
