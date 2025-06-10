# resumen_voluntario.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import obtener_usuario_actual
import requests
import json

router = APIRouter()

OLLAMA_URL = "http://20.66.107.40:11434"  # IP del VPS que corre Ollama

@router.post("/resumen/divorcio_voluntario")
async def resumen_divorcio_voluntario(
    promovente1: str = Form(...),
    promovente2: str = Form(...),
    direccion_promovente: str = Form(...),
    fecha_matrimonio: str = Form(...),
    regimen_matrimonial: str = Form(...),
    tiene_hijos: str = Form(...),
    hijos_info: str = Form(None),
    quien_guarda: str = Form(None),
    domicilio_hijos: str = Form(None),
    frecuencia_visitas: str = Form(None),
    horario_visitas: str = Form(None),
    porcentaje_alimentos: str = Form(None),
    uso_domicilio: str = Form(None),
    manutencion_conyuge: str = Form(None),
    conyuge_manutencion: str = Form(None),
    monto_manutencion: str = Form(None),
    bienes_comunes: str = Form(None),
    lista_bienes: str = Form(None),
    usuario=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    resumen = f"{promovente1} y {promovente2} solicitan divorcio voluntario.\n"
    resumen += f"Contrajeron matrimonio el {fecha_matrimonio} bajo el régimen de {regimen_matrimonial}.\n"
    resumen += f"Domicilio para notificaciones: {direccion_promovente}.\n"

    if tiene_hijos.lower().strip() == "si" and hijos_info:
        hijos_list = hijos_info.split(";")
        hijos_detalle = "; ".join([f"{h.split(':')[0]} ({h.split(':')[1]} años)" for h in hijos_list])
        resumen += f"Hijos menores: {hijos_detalle}.\n"
        resumen += f"La guarda y custodia será ejercida por {quien_guarda} en {domicilio_hijos}.\n"
        resumen += f"Visitas cada {frecuencia_visitas}, horario: {horario_visitas}.\n"
        resumen += f"Pensión alimenticia del {porcentaje_alimentos}% para los menores.\n"
        resumen += f"Uso del domicilio conyugal quedará a cargo de {uso_domicilio}.\n"

    if manutencion_conyuge and manutencion_conyuge.lower().strip() == "si":
        resumen += f"Se acuerda pensión conyugal del {monto_manutencion}% a favor de {conyuge_manutencion}.\n"

    if bienes_comunes and bienes_comunes.lower().strip() == "si" and lista_bienes:
        bienes = lista_bienes.split(";")
        bienes_descripcion = "\n".join([
            f"- '{b.split(':')[0]}' será dividido {b.split(':')[1]}% para {promovente1} y {b.split(':')[2]}% para {promovente2}."
            for b in bienes
        ])
        resumen += f"Reparto de bienes comunes:\n{bienes_descripcion}\n"

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
