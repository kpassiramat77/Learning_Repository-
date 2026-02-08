from __future__ import annotations

from fastapi import FastAPI, File, Form, UploadFile

from .external import to_external_model
from .models import CanonicalModel, ConversionResult, PatchResponse
from .parser import parse_workbook
from .patching import generate_patch
from .service import create_default_orchestrator


app = FastAPI(title="Excel Model Converter MVP")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/models/upload", response_model=ConversionResult)
@app.post("/models/convert", response_model=ConversionResult)
async def convert_model(file: UploadFile = File(...)) -> ConversionResult:
    orchestrator = create_default_orchestrator()
    workbook_bytes = await file.read()
    extracted = parse_workbook(workbook_bytes, filename=file.filename)
    canonical = orchestrator.build_canonical(extracted)
    external = to_external_model(canonical)
    return ConversionResult(canonical_model=canonical, external_model=external)


@app.post("/models/patch", response_model=PatchResponse)
async def patch_model(
    file: UploadFile = File(...),
    previous_canonical: str = Form(...),
) -> PatchResponse:
    orchestrator = create_default_orchestrator()
    workbook_bytes = await file.read()
    extracted = parse_workbook(workbook_bytes, filename=file.filename)
    current = orchestrator.build_canonical(extracted)

    previous_model = CanonicalModel.model_validate_json(previous_canonical)
    patch = generate_patch(previous_model, current)
    return PatchResponse(patch=patch, canonical_model=current)
