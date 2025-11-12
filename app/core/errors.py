from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)

def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        status = exc.status_code
        detail = exc.detail
        return JSONResponse(status_code=status, content={
            "error" : {"type": "http_error", "message": str(detail)} 
        })    
    
def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
        status = exc.status
        return JSONResponse(status_code=status, content={
            "error" : {"type": exc.code, "message": exc.message} 
        })    
    
def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        status = 409
        orig = getattr(exc, "orig", None) 
        constraint = (getattr(getattr(orig, "diag", None), "constraint_name", None) or getattr(orig, "constraint_name", None))
        if constraint == "uq_contact_message_per_day":
            msg = "message already submitted today"
        else:
            msg = "constraint violated"
        return JSONResponse(status_code=status, content={"error": {"type": "conflict", "message": msg}})    
    
def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        status = 500
        return JSONResponse(status_code=status, content={
            "error" : {"type": "internal_error", "message": "unexpected server error"} 
        })