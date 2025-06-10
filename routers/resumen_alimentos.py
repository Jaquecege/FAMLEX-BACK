# resumen_alimentos.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import obtener_usuario_actual
import requests
import json

router = APIRouter()

OLLAMA_URL = "http://20.66.107.40:11434"  # Reemplaza con la IP pública real si cambia

@router.post("/resumen/pension_alimenticia")
async def resumen_pension_alimenticia(
    promovente: str = Form(...),
    parentesco: str = Form(...),
    direccion: str = Form(...),
    demandado: str = Form(...),
    menores: str = Form(...),
    ingresos: str = Form(...),
    incumplimiento: str = Form(...),
    retroactivos: str = Form(...),
    medidas: str = Form(...),
    usuario=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    menores_list = [m.strip().replace(":", " de ") + " años" for m in menores.split(";") if m.strip()]
    menores_texto = "; ".join(menores_list)

    resumen = (
        f"{promovente}, en calidad de {parentesco}, promueve demanda en representación de {menores_texto} contra {demandado}, "
        f"para el pago de pensión alimenticia en la Ciudad de México.\n"
        f"Los menores dependen económicamente del promovente. Se estima que el demandado percibe ingresos mensuales de ${ingresos}.\n"
    )

    if incumplimiento.lower().strip() == "sí":
        resumen += "El promovente manifiesta que el demandado ha incumplido reiteradamente con su obligación alimentaria.\n"
    else:
        resumen += "El promovente señala que el demandado no ha contribuido voluntariamente a la manutención.\n"

    if retroactivos.lower().strip() == "sí":
        resumen += "Se solicita el pago retroactivo de la pensión desde la presentación de la demanda.\n"
    if medidas.lower().strip() == "sí":
        resumen += "Se solicita embargo precautorio u otra medida para garantizar el cumplimiento de la pensión.\n"

    prompt = (
        f"Resume jurídicamente en un solo párrafo, usando lenguaje técnico, el siguiente escrito legal:\n"
        f"{resumen}\nResumen:"
    )

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "model": "gemma:2b-instruct",
                "prompt": prompt
            }),
            timeout=60
        )

        if response.status_code == 200:
            resumen_generado = response.json()["response"].strip()
        else:
            resumen_generado = f"No se pudo generar el resumen. Código: {response.status_code}"

    except Exception as e:
        resumen_generado = f"Error al conectarse con el modelo: {str(e)}"

    return JSONResponse({"resumen": resumen_generado})
