from __future__ import annotations

from typing import Any, Protocol

from .formula import extract_references, parse_formula_to_expression
from .models import CalculationNode, Factor, LookupColumn, LookupTable
from .utils import infer_column_type, infer_value_type


class LLMClient(Protocol):
    def generate(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockLLM:
    def generate(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        if task == "build_model":
            return self._build_model(payload)
        if task == "build_calculations":
            return self._build_calculations(payload)
        raise ValueError(f"Unsupported task: {task}")

    def _build_model(self, payload: dict[str, Any]) -> dict[str, Any]:
        factors_payload = payload.get("factors", [])
        tables_payload = payload.get("lookup_tables", [])

        factors = []
        for factor in factors_payload:
            data_type = infer_value_type(factor.get("value"))
            factors.append(
                Factor(
                    name=factor.get("name", "unknown"),
                    data_type=data_type,
                    sample_value=factor.get("value"),
                ).model_dump()
            )

        lookup_tables = []
        for table in tables_payload:
            rows = table.get("rows", [])
            headers = table.get("headers", [])
            columns = []
            for index, header in enumerate(headers):
                column_values = [row[index] for row in rows if len(row) > index]
                columns.append(
                    LookupColumn(
                        name=header or f"column_{index + 1}",
                        data_type=infer_column_type(column_values),
                    ).model_dump()
                )
            lookup_tables.append(
                LookupTable(
                    name=table.get("name", "lookup"),
                    columns=columns,
                    rows=rows,
                ).model_dump()
            )

        return {"factors": factors, "lookup_tables": lookup_tables}

    def _build_calculations(self, payload: dict[str, Any]) -> dict[str, Any]:
        calculations = []
        for formula_data in payload.get("formulas", []):
            formula = formula_data.get("formula", "")
            expression = parse_formula_to_expression(formula)
            dependencies = extract_references(formula)
            calculation = CalculationNode(
                id=_calculation_id(formula_data.get("sheet"), formula_data.get("cell")),
                sheet=formula_data.get("sheet", ""),
                cell=formula_data.get("cell", ""),
                raw_formula=formula,
                expression=expression,
                dependencies=dependencies,
            ).model_dump()
            calculations.append(calculation)
        return {"calculations": calculations}


def _calculation_id(sheet: str | None, cell: str | None) -> str:
    safe_sheet = (sheet or "sheet").replace(" ", "_")
    safe_cell = (cell or "cell").replace("$", "")
    return f"calc_{safe_sheet}_{safe_cell}"
