from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from typing import Any
import logging

logger = logging.getLogger(__name__)


class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, details: dict[str, Any] | None = None, cause: Exception | None = None):
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}
        self.cause = cause
        super().__init__(message)



def _request_id(request: Request) -> str | None:
    return getattr(getattr(request, "state", None), "request_id", None) or request.headers.get("X-Request-ID")



def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    rid = _request_id(request)
    payload = {"error": {"type": "http_error", "message": str(exc.detail)}, "request_id": rid}
    logger.warning("HTTPException %s %s", exc.status_code, payload)
    return JSONResponse(status_code=exc.status_code, content=payload)



def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
    rid = _request_id(request)
    body = {"error": {"type": exc.code, "message": exc.message, "details": exc.details}, "request_id": rid}
    level = logger.warning if 400 <= exc.status < 500 else logger.error
    level("DomainError %s %s", exc.status, body)
    return JSONResponse(status_code=exc.status, content=body)



def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    rid = _request_id(request)
    orig = getattr(exc, "orig", None)
    pgcode = getattr(orig, "pgcode", None)
    diag = getattr(orig, "diag", None)

    code_map = {
        "23505": ("unique_violation", 409, "unique constraint violated"),
        "23503": ("foreign_key_violation", 409, "foreign key constraint violated"),
        "23502": ("not_null_violation", 400, "null value in column violates not-null constraint"),
        "23514": ("check_violation", 400, "check constraint violated"),
    }
    err_code, status, msg = code_map.get(pgcode, ("integrity_error", 409, "integrity constraint violated"))

    details = {
        "pgcode": pgcode,
        "constraint": getattr(diag, "constraint_name", None) if diag else getattr(orig, "constraint_name", None),
        "schema": getattr(diag, "schema_name", None) if diag else None,
        "table": getattr(diag, "table_name", None) if diag else None,
    }

    body = {"error": {"type": err_code, "message": msg, "details": details}, "request_id": rid}
    logger.warning("IntegrityError %s %s", status, body)
    return JSONResponse(status_code=status, content=body)



def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    rid = _request_id(request)
    body = {"error": {"type": "internal_error", "message": "unexpected server error"}, "request_id": rid}
    logger.error("Unhandled exception %s %s", type(exc).__name__, {"request_id": rid}, exc_info=exc)
    return JSONResponse(status_code=500, content=body)