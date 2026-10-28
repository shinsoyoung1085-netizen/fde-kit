"""엔티티 설정을 사용하는 SQLite CRUD 엔진."""

from contextlib import contextmanager
from datetime import date, datetime, timezone
import math
from pathlib import Path
import re
import sqlite3

from .entities import ENTITIES

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
SQL_TYPES = {"str": "TEXT", "int": "INTEGER", "float": "REAL", "bool": "INTEGER",
             "date": "TEXT", "datetime": "TEXT"}


class EngineError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def identifier(name):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"잘못된 식별자: {name}")
    return f'"{name}"'


def definition(entity):
    if entity not in ENTITIES:
        raise EngineError(404, "존재하지 않는 엔티티입니다.")
    return ENTITIES[entity]


@contextmanager
def connection():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connection() as db:
        for entity, config in ENTITIES.items():
            columns = ['id INTEGER PRIMARY KEY AUTOINCREMENT',
                       'created_at TEXT NOT NULL', 'updated_at TEXT NOT NULL']
            names = {"id", "created_at", "updated_at"}
            for field in config["fields"]:
                name = field["name"]
                if name in names or field["type"] not in SQL_TYPES:
                    raise ValueError(f"잘못된 필드 정의: {name}")
                names.add(name)
                columns.append(f'{identifier(name)} {SQL_TYPES[field["type"]]}'
                               + (' NOT NULL' if field.get("required") else ''))
            db.execute(f'CREATE TABLE IF NOT EXISTS {identifier(entity)} ({", ".join(columns)})')


def validate(entity, payload, partial=False):
    fields = definition(entity)["fields"]
    if not isinstance(payload, dict):
        raise EngineError(422, "입력은 JSON 객체여야 합니다.")
    unknown = payload.keys() - {field["name"] for field in fields}
    if unknown:
        raise EngineError(422, f"정의되지 않은 필드입니다: {', '.join(sorted(unknown))}")
    values = {}
    for field in fields:
        name, kind = field["name"], field["type"]
        label = field.get("label", name)
        if name not in payload and partial:
            continue
        value = payload.get(name, field.get("default"))
        if field.get("required") and (value is None or isinstance(value, str) and not value.strip()):
            raise EngineError(422, f"{label}: 필수 입력 항목입니다.")
        if value is None:
            values[name] = None
            continue
        valid = False
        if kind == "str":
            valid = isinstance(value, str)
        elif kind == "int":
            valid = type(value) is int and -(2**63) <= value < 2**63
        elif kind == "float":
            try:
                valid = type(value) in (int, float) and math.isfinite(value)
            except OverflowError:
                valid = False
        elif kind == "bool":
            valid = type(value) is bool
        elif kind in ("date", "datetime") and isinstance(value, str):
            try:
                if kind == "date":
                    valid = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
                    date.fromisoformat(value)
                else:
                    valid = "T" in value
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                valid = False
        if not valid:
            raise EngineError(422, f"{label}: {kind} 형식이어야 합니다.")
        values[name] = value
    return values


def serialize(entity, row):
    result = dict(row)
    for field in definition(entity)["fields"]:
        if field["type"] == "bool" and result[field["name"]] is not None:
            result[field["name"]] = bool(result[field["name"]])
    return result


def list_records(entity):
    definition(entity)
    with connection() as db:
        rows = db.execute(f'SELECT * FROM {identifier(entity)} ORDER BY id').fetchall()
    return [serialize(entity, row) for row in rows]


def get_record(entity, record_id):
    definition(entity)
    with connection() as db:
        row = db.execute(f'SELECT * FROM {identifier(entity)} WHERE id = ?', (record_id,)).fetchone()
    if row is None:
        raise EngineError(404, "존재하지 않는 항목입니다.")
    return serialize(entity, row)


def create_record(entity, payload):
    values = validate(entity, payload)
    now = datetime.now(timezone.utc).isoformat()
    values.update(created_at=now, updated_at=now)
    with connection() as db:
        cursor = db.execute(
            f'INSERT INTO {identifier(entity)} ({", ".join(map(identifier, values))}) '
            f'VALUES ({", ".join("?" for _ in values)})', tuple(values.values()))
        record_id = cursor.lastrowid
    return get_record(entity, record_id)


def update_record(entity, record_id, payload):
    get_record(entity, record_id)
    values = validate(entity, payload, partial=True)
    values["updated_at"] = datetime.now(timezone.utc).isoformat()
    with connection() as db:
        cursor = db.execute(
            f'UPDATE {identifier(entity)} SET {", ".join(identifier(key) + " = ?" for key in values)} WHERE id = ?',
            (*values.values(), record_id))
        if cursor.rowcount == 0:
            raise EngineError(404, "존재하지 않는 항목입니다.")
    return get_record(entity, record_id)


def delete_record(entity, record_id):
    definition(entity)
    with connection() as db:
        cursor = db.execute(f'DELETE FROM {identifier(entity)} WHERE id = ?', (record_id,))
        if cursor.rowcount == 0:
            raise EngineError(404, "존재하지 않는 항목입니다.")
