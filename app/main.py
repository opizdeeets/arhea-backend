from fastapi import FastAPI, HTTPException
import sqlalchemy as sa
from app.core.db import engine
from app.core.errors import *
from sqlalchemy.exc import IntegrityError
from app.core.errors import (DomainError, http_exception_handler, domain_exception_handler, integrity_exception_handler, generic_exception_handler)


app = FastAPI(
    title="ARHEA API",
    version="0.1.0",
    debug=False,
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/")
async def check():
    return {"status": "ok"}

@app.get("/db_check")
async def check_db_connection() -> None:
    async with engine.connect() as conn:
        await conn.execute(sa.text("SELECT 1"))

@app.get("/boom-domain")
async def boom_domain():
    raise DomainError("bad_request", "invalid input")

@app.get("/boom-500")
async def boom_500():
    raise RuntimeError("boom")

