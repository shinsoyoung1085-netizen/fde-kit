from contextlib import asynccontextmanager
from typing import Any

from fastapi import Body, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import engine
from .entities import ENTITIES


@asynccontextmanager
async def lifespan(app):
    engine.initialize()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(engine.EngineError)
async def engine_error(request: Request, exc: engine.EngineError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def request_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "요청 형식이 올바르지 않습니다. JSON 본문과 항목 ID를 확인하세요."})


@app.get("/api/meta")
def meta():
    return ENTITIES


@app.get("/api/{entity}")
def list_records(entity: str):
    return engine.list_records(entity)


@app.post("/api/{entity}", status_code=201)
def create_record(entity: str, payload: Any = Body(...)):
    return engine.create_record(entity, payload)


@app.get("/api/{entity}/{id}")
def get_record(entity: str, id: int):
    return engine.get_record(entity, id)


@app.put("/api/{entity}/{id}")
def update_record(entity: str, id: int, payload: Any = Body(...)):
    return engine.update_record(entity, id, payload)


@app.delete("/api/{entity}/{id}", status_code=204)
def delete_record(entity: str, id: int):
    engine.delete_record(entity, id)
    return Response(status_code=204)
