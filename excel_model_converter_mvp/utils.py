from __future__ import annotations

from datetime import date, datetime
from typing import Any


def infer_value_type(value: Any) -> str:
    if value is None:
        return "string"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, (datetime, date)):
        return "date"
    return "string"


def infer_column_type(values: list[Any]) -> str:
    for value in values:
        if value is None:
            continue
        return infer_value_type(value)
    return "string"
