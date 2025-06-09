# resumen_incausado.py
from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import obtener_usuario_actual
import subprocess

router = APIRouter()

@router.post("/resumen/divorcio_incausado")
async def resumen_divorcio_incausado(
    promovente: str = Form(...),
    demandado: str = Form(...),
    direccion_promovente: str = Form(...),
    fecha_matrimonio: str = Form(...),
    regimen: str = Form(...),
    ultimo_domicilio: str = Form(...),
    fecha_separacion: str = Form(...),
    conoce_domicilio: str = Form(...),
    domicilio_demandado_si: str = Form(None),
    domicilio_demandado_no: str = Form(None),
    hijos: str = Form(...),
    hijos_info: str = Form(None),
    incluir_guardia: str = Form(None),
    guarda_titular: str = Form(None),
    guarda_domicilio: str = Form(None),
    visitas_frecuencia: str = Form(None),
    visitas_horario: str = Form(None),
    incluir_alimentos: str = Form(None),
    porcentaje_alimentos: str = Form(None),
    forma_pago_alimentos: str = Form(None),
    bienes: str = Form(None),
    lista_bienes: str = Form(None),
    proteccion: str = Form(None),
    usuario=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    resumen_base = f"""
La parte promovente, {promovente}, solicita divorcio incausado contra {demandado}, con domicilio en {domicilio_demandado_si or domicilio_demandado_no}.
Contrajeron matrimonio el {fecha_matrimonio} bajo el régimen de {regimen}. Su último domicilio conyugal fue en {ultimo_domicilio} y están separados desde {fecha_separacion}.

"""

    resumen_hijos = ""
    if hijos.lower().strip() == "si" and hijos_info:
        hijos_lista = hijos_info.split(";")
        hijos_descripcion = "; ".join([f"{h.strip().split(':')[0]} ({h.strip().split(':')[1]} años)" for h in hijos_lista])
        resumen_hijos = f"Tienen hijos menores: {hijos_descripcion}.\n"

    resumen_guardia = ""
    if incluir_guardia and incluir_guardia.lower().strip() == "si":
        resumen_guardia = f"La guarda y custodia será ejercida por {guarda_titular} en el domicilio {guarda_domicilio}.\n"

    resumen_visitas = ""
    if visitas_frecuencia and visitas_horario:
        resumen_visitas = f"El régimen de visitas será cada {visitas_frecuencia}, en horario de {visitas_horario}.\n"

    resumen_alimentos = ""
    if incluir_alimentos and incluir_alimentos.lower().strip() == "si":
        resumen_alimentos = f"Se solicita pensión alimenticia del {porcentaje_alimentos}% pagada de forma {forma_pago_alimentos}.\n"

    resumen_bienes = ""
    if bienes and bienes.lower().strip() == "si" and lista_bienes:
        bienes_list = lista_bienes.split(";")
        partes = "\n".join([
            f"'{b.split(':')[0]}' será dividido {b.split(':')[1]}% para {promovente} y {b.split(':')[2]}% para {demandado}."
            for b in bienes_list
        ])
        resumen_bienes = f"Se repartirá(n) los siguientes bien(es):\n{partes}\n"

    resumen_proteccion = ""
    if proteccion and proteccion.lower().strip() == "si":
        resumen_proteccion = (
            "Se solicita orden de protección: prohibición de acercamiento, contacto e intimidación por parte del demandado.\n"
        )

    contenido_legal = (
        resumen_base +
        resumen_hijos +
        resumen_guardia +
        resumen_visitas +
        resumen_alimentos +
        resumen_bienes +
        resumen_proteccion
    )

    prompt = (
        f"Resume jurídicamente en un solo párrafo, usando lenguaje técnico, el siguiente escrito legal:\n"
        f"{contenido_legal}\nResumen:"
    )

    comando = ["ollama", "run", "gemma:2b-instruct"]
    resultado = subprocess.run(comando, input=prompt, capture_output=True, text=True)

    resumen_generado = resultado.stdout.strip() if resultado.returncode == 0 else "No se pudo generar el resumen."
    subprocess.run(["ollama", "stop", "gemma:2b-instruct"])
    return JSONResponse({"resumen": resumen_generado})

