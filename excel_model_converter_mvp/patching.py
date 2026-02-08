from __future__ import annotations

from .models import CalculationNode, CanonicalModel, PatchOperation, PatchResult


def generate_patch(previous: CanonicalModel, current: CanonicalModel) -> PatchResult:
    previous_map = {calc.id: calc for calc in previous.calculations}
    current_map = {calc.id: calc for calc in current.calculations}

    changes: list[PatchOperation] = []

    for calc_id, current_calc in current_map.items():
        if calc_id not in previous_map:
            changes.append(
                PatchOperation(op="add", target=calc_id, value=current_calc)
            )
            continue
        previous_calc = previous_map[calc_id]
        if previous_calc.raw_formula != current_calc.raw_formula:
            changes.append(
                PatchOperation(
                    op="replace",
                    target=calc_id,
                    value=current_calc,
                    previous_formula=previous_calc.raw_formula,
                )
            )

    for calc_id, previous_calc in previous_map.items():
        if calc_id not in current_map:
            changes.append(
                PatchOperation(op="remove", target=calc_id, value=previous_calc)
            )

    summary = _summarize_changes(changes)
    return PatchResult(
        model_name=current.model_name,
        changes=changes,
        summary=summary,
    )


def _summarize_changes(changes: list[PatchOperation]) -> dict[str, int]:
    summary = {"add": 0, "remove": 0, "replace": 0}
    for change in changes:
        summary[change.op] = summary.get(change.op, 0) + 1
    return summary
