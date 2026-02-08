from __future__ import annotations

from .agents import FormulaCalculationAgent, ModelBuilderAgent
from .llm import MockLLM
from .models import CanonicalModel, ExtractedModel


class ModelOrchestrator:
    def __init__(
        self, model_builder: ModelBuilderAgent, formula_agent: FormulaCalculationAgent
    ) -> None:
        self.model_builder = model_builder
        self.formula_agent = formula_agent

    def build_canonical(self, extracted: ExtractedModel) -> CanonicalModel:
        model_parts = self.model_builder.build(extracted)
        formula_parts = self.formula_agent.build(extracted)
        return CanonicalModel(
            model_name=extracted.workbook_name,
            factors=model_parts.factors,
            lookup_tables=model_parts.lookup_tables,
            calculations=formula_parts.calculations,
        )


def create_default_orchestrator() -> ModelOrchestrator:
    llm = MockLLM()
    return ModelOrchestrator(
        model_builder=ModelBuilderAgent(llm=llm),
        formula_agent=FormulaCalculationAgent(llm=llm),
    )
