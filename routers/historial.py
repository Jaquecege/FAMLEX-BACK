from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Documento
from routers.auth import obtener_usuario_actual
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/documentos")
def obtener_documentos_usuario(db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    documentos = db.query(Documento).filter(Documento.usuario_id == usuario.id).order_by(Documento.fecha_creacion.desc()).all()
    return [{"id": doc.id,
            "nombre": doc.nombre, 
            "url": f"http://localhost:8000/descargar/{doc.id}", 
            "fecha_creacion": doc.fecha_creacion
            } for doc in documentos]

@router.get("/descargar/{doc_id}")
def descargar_documento(doc_id: int, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    documento = db.query(Documento).filter(Documento.id == doc_id, Documento.usuario_id == usuario.id).first()
    if not documento or not os.path.exists(documento.ruta):
        return {"error": "Documento no encontrado"}

    return FileResponse(documento.ruta,
                         filename=documento.nombre,
                           media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@router.delete("/documentos/{doc_id}")
def eliminar_documento(doc_id: int, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    documento = db.query(Documento).filter(Documento.id == doc_id, Documento.usuario_id == usuario.id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if os.path.exists(documento.ruta):
        os.remove(documento.ruta)

    db.delete(documento)
    db.commit()
    return {"mensaje": "Documento eliminado correctamente"}
