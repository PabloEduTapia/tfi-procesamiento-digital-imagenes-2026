from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from core.color_marker import ColorMarker
from core.daltonism_engine import DaltonismEngine
from core.image_codec import ImageCodec
from core.matrix_repository import MatrixRepository
from core.models import ProcessingOptions
from core.orchestrator import ProcessingOrchestrator, VALID_RESULTS


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX_FILE = ROOT_DIR / "data" / "matrices" / "machado.xlsx"
MATRIX_FILE = Path(os.getenv("MATRIX_FILE", DEFAULT_MATRIX_FILE))
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", 15 * 1024 * 1024))

matrix_repository = MatrixRepository(MATRIX_FILE)
engine = DaltonismEngine(matrix_repository)
orchestrator = ProcessingOrchestrator(engine, ColorMarker())

app = FastAPI(
    title="API de procesamiento de imágenes para daltonismo",
    version="2.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "matrix_file": MATRIX_FILE.name,
    }


@app.get("/v1/matrices")
def matrices():
    return matrix_repository.available()


@app.post("/v1/images/process")
async def process_image(
    file: UploadFile = File(...),
    result: str = Form("corrected_marked"),
    types: str = Form("protan"),
    severity: str = Form("10"),
    correction_intensity: float = Form(0.7),
    marker_spacing: int = Form(42),
    marker_size: int = Form(7),
    include_legend: bool = Form(True),
    output_format: str = Form("png"),
):
    if result not in VALID_RESULTS:
        raise HTTPException(status_code=400, detail="Tipo de resultado no válido.")

    content = await file.read(MAX_IMAGE_BYTES + 1)

    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el tamaño máximo permitido.")

    try:
        image = ImageCodec.decode(content)
        selected_types = [value.strip() for value in types.split(",") if value.strip()]
        options = ProcessingOptions(
            tipos=selected_types,
            severidad=severity,
            resultado=result,
            intensidad_correccion=correction_intensity,
            espacio_marcadores=marker_spacing,
            tamano_marcadores=marker_size,
            incluir_leyenda=include_legend,
        )
        context = orchestrator.process(image, options)
        output, media_type = ImageCodec.encode(context.current, output_format)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex

    filename = f"{Path(file.filename or 'imagen').stem}_{result}.{output_format}"

    return Response(
        content=output,
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "X-Processing-Result": result,
        },
    )
