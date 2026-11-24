"""FastAPI microservice for Latinex Data Hub WTP Survey & Protected Admin Console."""

import csv
import io
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

import auth
import db
from config import settings

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
ASSETS_DIR = BASE_DIR.parent / "src" / "assets"

LOGIN_WINDOW_SECONDS = 300
LOGIN_MAX_ATTEMPTS = 10
_failed_login_attempts: dict[str, list[float]] = defaultdict(list)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_pool()
    try:
        yield
    finally:
        db.close_pool()


app = FastAPI(
    title="Latinex Data Hub: WTP Survey Microservice",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

if ASSETS_DIR.exists():
    app.mount("/src/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


class SurveySubmission(BaseModel):
    alias: str = Field(..., min_length=1, max_length=100)
    contact: str = Field(..., min_length=1, max_length=50)
    segment: str = Field(..., min_length=1, max_length=50)
    roleCategory: Optional[str] = Field(default="", max_length=100)
    manualHours: float = Field(..., ge=0, le=1000)
    intrinsicValueUsd: float = Field(..., ge=0, le=1000000)
    tooCheap: float = Field(..., gt=0)
    cheap: float = Field(..., gt=0)
    expensive: float = Field(..., gt=0)
    tooExpensive: float = Field(..., gt=0)
    nmsCheap: int = Field(..., ge=1, le=5)
    nmsExpensive: int = Field(..., ge=1, le=5)
    s3: bool = False
    tablero: bool = False
    sdk: bool = False
    selectedServiceIds: list[str] = Field(default_factory=list)
    priorityDatasets: list[str] = Field(default_factory=list)
    qualitativeNotes: Optional[str] = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def validate_van_westendorp_order(self) -> "SurveySubmission":
        if not (
            0 < self.tooCheap < self.cheap < self.expensive < self.tooExpensive
        ):
            raise ValueError(
                "Los umbrales deben cumplir orden estricto: "
                "0 < Sospechosamente Baja < Atractiva < Elevada < Prohibitiva."
            )
        return self


class AdminLoginRequest(BaseModel):
    password: str = Field(..., min_length=1)


class ComplementaryServicePayload(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    setupFeeUsd: float = Field(..., ge=0, le=1000000)
    monthlyFeeUsd: float = Field(..., ge=0, le=1000000)
    isActive: bool = True
    description: Optional[str] = Field(default="", max_length=1000)


@app.get("/", include_in_schema=False)
def serve_public_survey() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/admin", include_in_schema=False)
def serve_admin_console() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "admin.html"))


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    if not db.check_db_health():
        raise HTTPException(status_code=503, detail="Database unreachable")
    return {"status": "ok", "database": "connected"}


@app.get("/api/v1/services")
def get_public_services() -> dict[str, object]:
    services = db.list_complementary_services(active_only=True)
    return {"services": services}


@app.post("/api/v1/responses", status_code=status.HTTP_201_CREATED)
def submit_response(payload: SurveySubmission) -> dict[str, str]:
    saved = db.insert_survey_response(payload.model_dump())
    return {
        "status": "saved",
        "responseId": saved["response_id"],
        "submittedAt": saved["submitted_at"],
    }


@app.post("/api/v1/admin/login")
def admin_login(payload: AdminLoginRequest, request: Request, response: Response) -> dict[str, bool]:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    recent = [ts for ts in _failed_login_attempts[client_ip] if now - ts < LOGIN_WINDOW_SECONDS]
    _failed_login_attempts[client_ip] = recent
    if len(recent) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intente nuevamente en unos minutos.",
        )

    if not auth.verify_admin_password(payload.password):
        _failed_login_attempts[client_ip].append(now)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta.",
        )
    _failed_login_attempts.pop(client_ip, None)
    token = auth.create_session_token()
    response.set_cookie(
        key=auth.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True}


@app.post("/api/v1/admin/logout")
def admin_logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(key=auth.COOKIE_NAME, path="/")
    return {"authenticated": False}


@app.get("/api/v1/admin/me")
def admin_me(_: None = Depends(auth.require_admin_session)) -> dict[str, bool]:
    return {"authenticated": True}


@app.get("/api/v1/admin/responses")
def admin_get_responses(_: None = Depends(auth.require_admin_session)) -> dict[str, object]:
    rows = db.list_survey_responses()
    return {"count": len(rows), "responses": rows}


@app.get("/api/v1/admin/services")
def admin_list_services(_: None = Depends(auth.require_admin_session)) -> dict[str, object]:
    return {"services": db.list_complementary_services(active_only=False)}


@app.post("/api/v1/admin/services", status_code=status.HTTP_201_CREATED)
def admin_create_service(
    payload: ComplementaryServicePayload,
    _: None = Depends(auth.require_admin_session),
) -> dict[str, object]:
    try:
        created = db.create_complementary_service(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo crear el servicio: {exc}") from exc
    return {"service": created}


@app.put("/api/v1/admin/services/{service_id}")
def admin_update_service(
    service_id: str,
    payload: ComplementaryServicePayload,
    _: None = Depends(auth.require_admin_session),
) -> dict[str, object]:
    try:
        updated = db.update_complementary_service(service_id, payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo actualizar el servicio: {exc}") from exc
    if not updated:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")
    return {"service": updated}


@app.delete("/api/v1/admin/services/{service_id}")
def admin_delete_service(
    service_id: str,
    _: None = Depends(auth.require_admin_session),
) -> dict[str, bool]:
    deleted = db.delete_complementary_service(service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Servicio no encontrado.")
    return {"deleted": True}


@app.get("/api/v1/admin/export.csv")
def admin_export_csv(_: None = Depends(auth.require_admin_session)) -> StreamingResponse:
    rows = db.list_survey_responses()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "ID",
            "Alias",
            "Contacto",
            "Segmento",
            "Rol_Decision",
            "Horas_Mes",
            "Valor_Intrinseco_USD",
            "Sospechosamente_Baja",
            "Atractiva",
            "Elevada",
            "Prohibitiva",
            "Prob_Atractiva",
            "Prob_Elevada",
            "Conector_S3",
            "Tablero_Marca",
            "Kit_SDK",
            "Datasets_Prioritarios",
            "Notas_Cualitativas",
            "Fecha_Envio",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r["id"],
                r["alias"],
                r["contact"],
                r["segment"],
                r.get("roleCategory") or "",
                r["manualHours"],
                r["intrinsicValueUsd"],
                r["tooCheap"],
                r["cheap"],
                r["expensive"],
                r["tooExpensive"],
                r["nmsCheap"],
                r["nmsExpensive"],
                r["s3"],
                r["tablero"],
                r["sdk"],
                "; ".join(r.get("priorityDatasets") or []),
                r.get("qualitativeNotes") or "",
                r["submittedAt"],
            ]
        )
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="latinex_wtp_respuestas.csv"'},
    )
