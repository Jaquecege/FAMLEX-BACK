# resumen_admin.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import obtener_usuario_actual
import requests  # 👈 Importante
import json

router = APIRouter()

OLLAMA_URL = "http://20.66.107.40:11434"  # 👈 IP pública de la VM

@router.post("/resumen/divorcio_admin")
async def resumen_divorcio_admin(
    promovente: str = Form(...),
    conyuge: str = Form(...),
    direccion: str = Form(...),
    fecha_matrimonio: str = Form(...),
    regimenadm: str = Form(...),
    usuario=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    contenido_legal = f"""
        Quienes suscribimos, {promovente} y {conyuge}, por nuestro propio derecho, señalando como domicilio el ubicado en {direccion},
        comparecemos respetuosamente para exponer:

        Que por medio del presente escrito, y con fundamento en el artículo 272 del Código Civil para la Ciudad de México,
        venimos a solicitar de manera conjunta y de común acuerdo el divorcio por la vía administrativa.

        1. Con fecha {fecha_matrimonio}, contrajimos matrimonio civil en la Ciudad de México.
        2. Ambos comparecientes somos mayores de edad.
        3. No procreamos hijos menores ni dependientes económicos.
        4. La compareciente no está embarazada.
        5. Ninguno requiere pensión alimenticia.
        6. El régimen matrimonial fue: {regimenadm}.
    """

    prompt = f"Resume jurídicamente en un solo párrafo, usando lenguaje técnico, el siguiente escrito legal:\n{contenido_legal}\nResumen:"

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "model": "gemma:2b-instruct",
                "prompt": prompt
            }),
            timeout=180
        )
        if response.status_code == 200:
            resumen_generado = response.json()["response"].strip()
        else:
            resumen_generado = f"No se pudo generar el resumen. Código: {response.status_code}"

    except Exception as e:
        resumen_generado = f"Error al conectarse con el modelo: {str(e)}"

    return JSONResponse({"resumen": resumen_generado})

