# resumen_reconocimiento.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import obtener_usuario_actual
import requests
import json

router = APIRouter()

OLLAMA_URL = "http://20.66.107.40:11434"  # Cambia esta IP si cambia tu VPS/Azure

@router.post("/resumen/reconocimiento_paternidad")
async def resumen_reconocimiento_paternidad(
    promovente: str = Form(...),
    menor: str = Form(...),
    edad_menor: str = Form(...),
    fecha_nacimiento: str = Form(...),
    demandado: str = Form(...),
    tipo_relacion: str = Form(...),
    periodo_relacion: str = Form(...),
    motivo: str = Form(...),
    conoce_trabajo: str = Form(...),
    trabajo: str = Form(None),
    direccion_trabajo: str = Form(None),
    ingreso: str = Form(None),
    domicilio: str = Form(...),
    solicita_pension: str = Form(...),
    porcentaje: str = Form(None),
    incumplimiento: str = Form(None),
    prueba_adn: str = Form(...),
    testigos: str = Form(None),
    usuario=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    resumen = (
        f"{promovente}, en representación de la menor {menor} de {edad_menor} años (nacida el {fecha_nacimiento}), "
        f"promueve demanda contra {demandado} para el reconocimiento judicial de paternidad.\n"
        f"Ambos sostuvieron una relación de tipo {tipo_relacion} durante el periodo {periodo_relacion}. "
        f"Se considera al demandado como padre debido a: {motivo}.\n"
    )

    if conoce_trabajo.lower() == "sí" and trabajo and direccion_trabajo and ingreso:
        resumen += (
            f"El demandado trabaja en {trabajo}, ubicado en {direccion_trabajo}, con ingresos aproximados de ${ingreso}.\n"
        )
    else:
        resumen += "Se desconoce el lugar de trabajo actual del demandado.\n"

    resumen += f"El demandado {domicilio.lower()} y no ha reconocido voluntariamente a la menor.\n"

    if solicita_pension.lower() == "sí" and porcentaje and incumplimiento:
        resumen += (
            f"Se solicita pensión alimenticia del {porcentaje}% debido a incumplimiento desde {incumplimiento}.\n"
        )
    
    if prueba_adn.lower() == "sí":
        resumen += "Se solicita la práctica de prueba pericial en genética molecular (ADN).\n"

    if testigos:
        resumen += f"Se cuenta con testigos: {testigos}.\n"

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

