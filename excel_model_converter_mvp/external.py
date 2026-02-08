from __future__ import annotations

from .formula import expression_to_string
from .models import (
    CanonicalModel,
    ExternalCalculation,
    ExternalField,
    ExternalModel,
    ExternalTable,
)


def to_external_model(canonical: CanonicalModel) -> ExternalModel:
    inputs = [
        ExternalField(name=factor.name, data_type=factor.data_type)
        for factor in canonical.factors
    ]
    tables = []
    for table in canonical.lookup_tables:
        columns = [
            ExternalField(name=column.name, data_type=column.data_type)
            for column in table.columns
        ]
        tables.append(ExternalTable(name=table.name, columns=columns, rows=table.rows))
    calculations = [
        ExternalCalculation(
            name=f"{calc.sheet}!{calc.cell}",
            expression=expression_to_string(calc.expression),
        )
        for calc in canonical.calculations
    ]
    return ExternalModel(
        name=canonical.model_name,
        inputs=inputs,
        tables=tables,
        calculations=calculations,
    )
