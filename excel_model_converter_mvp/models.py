from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    model_config = {"extra": "forbid"}


class ExpressionNode(BaseSchema):
    node_type: Literal["literal", "reference", "range", "binary", "function", "unary"]
    value: Any | None = None
    ref: str | None = None
    ref_type: Literal["cell", "name"] | None = None
    operator: str | None = None
    left: "ExpressionNode" | None = None
    right: "ExpressionNode" | None = None
    operand: "ExpressionNode" | None = None
    name: str | None = None
    args: list["ExpressionNode"] | None = None


class Factor(BaseSchema):
    name: str
    data_type: Literal["string", "integer", "number", "boolean", "date"]
    source: str = "excel"
    sample_value: Any | None = None


class LookupColumn(BaseSchema):
    name: str
    data_type: Literal["string", "integer", "number", "boolean", "date"]


class LookupTable(BaseSchema):
    name: str
    columns: list[LookupColumn]
    rows: list[list[Any]]


class CalculationNode(BaseSchema):
    id: str
    sheet: str
    cell: str
    raw_formula: str
    expression: ExpressionNode
    dependencies: list[str] = Field(default_factory=list)


class CanonicalModel(BaseSchema):
    model_name: str
    version: str = "0.1"
    factors: list[Factor] = Field(default_factory=list)
    lookup_tables: list[LookupTable] = Field(default_factory=list)
    calculations: list[CalculationNode] = Field(default_factory=list)


class ExternalField(BaseSchema):
    name: str
    data_type: str


class ExternalTable(BaseSchema):
    name: str
    columns: list[ExternalField]
    rows: list[list[Any]]


class ExternalCalculation(BaseSchema):
    name: str
    expression: str


class ExternalModel(BaseSchema):
    schema_version: str = "1.0"
    name: str
    inputs: list[ExternalField] = Field(default_factory=list)
    tables: list[ExternalTable] = Field(default_factory=list)
    calculations: list[ExternalCalculation] = Field(default_factory=list)


class PatchOperation(BaseSchema):
    op: Literal["add", "remove", "replace"]
    target: str
    value: CalculationNode | None = None
    previous_formula: str | None = None


class PatchResult(BaseSchema):
    model_name: str
    changes: list[PatchOperation] = Field(default_factory=list)
    summary: dict[str, int] = Field(default_factory=dict)


class ConversionResult(BaseSchema):
    canonical_model: CanonicalModel
    external_model: ExternalModel


class PatchResponse(BaseSchema):
    patch: PatchResult
    canonical_model: CanonicalModel


class ExtractedFactor(BaseSchema):
    name: str
    value: Any | None = None


class ExtractedLookupTable(BaseSchema):
    name: str
    headers: list[str]
    rows: list[list[Any]]


class ExtractedFormula(BaseSchema):
    sheet: str
    cell: str
    formula: str


class ExtractedModel(BaseSchema):
    workbook_name: str
    factors: list[ExtractedFactor] = Field(default_factory=list)
    lookup_tables: list[ExtractedLookupTable] = Field(default_factory=list)
    formulas: list[ExtractedFormula] = Field(default_factory=list)


class ModelBuilderOutput(BaseSchema):
    factors: list[Factor] = Field(default_factory=list)
    lookup_tables: list[LookupTable] = Field(default_factory=list)


class FormulaAgentOutput(BaseSchema):
    calculations: list[CalculationNode] = Field(default_factory=list)
