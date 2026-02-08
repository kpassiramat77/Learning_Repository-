from __future__ import annotations

from .llm import LLMClient
from .models import ExtractedModel, FormulaAgentOutput, ModelBuilderOutput


class ModelBuilderAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def build(self, extracted: ExtractedModel) -> ModelBuilderOutput:
        payload = {
            "model_name": extracted.workbook_name,
            "factors": [factor.model_dump() for factor in extracted.factors],
            "lookup_tables": [table.model_dump() for table in extracted.lookup_tables],
        }
        response = self.llm.generate("build_model", payload)
        return ModelBuilderOutput.model_validate(response)


class FormulaCalculationAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def build(self, extracted: ExtractedModel) -> FormulaAgentOutput:
        payload = {
            "model_name": extracted.workbook_name,
            "formulas": [formula.model_dump() for formula in extracted.formulas],
        }
        response = self.llm.generate("build_calculations", payload)
        return FormulaAgentOutput.model_validate(response)
