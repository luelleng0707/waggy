"""Developer-facing mathematical audit runtime."""

from __future__ import annotations

from repository.models.runtime import EvidenceGraph
from repository.optimization.models import OptimizedBundle
from repository.reasoning.models import ConditionAssessment

from .models import ExecutionTrace, ExecutionTree, ExecutionTreeNode, FormulaTrace
from .replay import DeterministicMathReplay


class MathDebuggerRuntime:
    def __init__(self):
        self.replay_engine = DeterministicMathReplay()

    def trace(
        self,
        evidence_graph: EvidenceGraph,
        condition_assessments: tuple[ConditionAssessment, ...] = (),
        formula_version_overrides: dict[str, str] | None = None,
    ):
        return self.replay_engine.replay(
            evidence_graph=evidence_graph,
            condition_assessments=condition_assessments,
            formula_version_overrides=formula_version_overrides,
        )

    def trace_optimization(self, optimized_bundle: OptimizedBundle) -> ExecutionTrace:
        formula_traces: list[FormulaTrace] = []
        formula_traces.append(
            FormulaTrace(
                trace_id="optimization:TGT-701",
                formula_id="TGT-701",
                formula_version="1.0.0",
                formula_name="Target Intake",
                status="ACTIVE",
                equation="required_amount = mean(source_natural_amount / max(source_bioavailability,0.01))",
                substituted_equation="see target_intake_plan targets",
                intermediate_calculations=tuple(
                    [f"{t.ingredient_id}: required={t.required_amount} {t.unit}" for t in optimized_bundle.target_intake_plan.targets]
                ),
                output_variable="target_count",
                output_value=len(optimized_bundle.target_intake_plan.targets),
                unit="count",
            )
        )
        formula_traces.append(
            FormulaTrace(
                trace_id="optimization:COV-703",
                formula_id="COV-703",
                formula_version="1.0.0",
                formula_name="Coverage",
                status="ACTIVE",
                equation="coverage_percent = (provided / required) * 100",
                substituted_equation="see coverage_report items",
                intermediate_calculations=tuple(
                    [
                        f"{item.ingredient_id}: provided={item.provided_amount} required={item.required_amount} coverage={item.coverage_percent}"
                        for item in optimized_bundle.coverage_report.items
                    ]
                ),
                output_variable="mean_coverage_percent",
                output_value=optimized_bundle.coverage_report.mean_coverage_percent,
                unit="percent",
            )
        )
        formula_traces.append(
            FormulaTrace(
                trace_id="optimization:HRM-711",
                formula_id="HRM-711",
                formula_version="1.0.0",
                formula_name="Harmony",
                status="ACTIVE",
                equation="0.30*coverage + 0.20*dose + 0.15*absorption + 0.10*synergy + 0.10*calories + 0.10*constraints - 0.05*conflict",
                substituted_equation=(
                    f"0.30*{optimized_bundle.harmony_report.coverage_percent} + "
                    f"0.20*{optimized_bundle.harmony_report.dose_accuracy_percent} + "
                    f"0.15*{optimized_bundle.harmony_report.absorption_percent} + "
                    f"0.10*{optimized_bundle.harmony_report.synergy_percent} + "
                    f"0.10*{optimized_bundle.harmony_report.calories_percent} + "
                    f"0.10*{optimized_bundle.harmony_report.constraint_satisfaction_percent} - "
                    f"0.05*{optimized_bundle.harmony_report.conflict_penalty_percent}"
                ),
                intermediate_calculations=(
                    f"coverage_contribution={0.30 * optimized_bundle.harmony_report.coverage_percent}",
                    f"dose_contribution={0.20 * optimized_bundle.harmony_report.dose_accuracy_percent}",
                    f"absorption_contribution={0.15 * optimized_bundle.harmony_report.absorption_percent}",
                    f"synergy_contribution={0.10 * optimized_bundle.harmony_report.synergy_percent}",
                    f"calories_contribution={0.10 * optimized_bundle.harmony_report.calories_percent}",
                    f"constraints_contribution={0.10 * optimized_bundle.harmony_report.constraint_satisfaction_percent}",
                    f"conflict_penalty={0.05 * optimized_bundle.harmony_report.conflict_penalty_percent}",
                ),
                output_variable="harmony_score",
                output_value=optimized_bundle.harmony_report.harmony_score,
                unit="score_percent",
            )
        )
        tree = ExecutionTree(
            root_node_id="root",
            nodes=(
                ExecutionTreeNode("root", "Optimization Execution", "FORMULA_PIPELINE", ("f1", "f2", "f3")),
                ExecutionTreeNode("f1", "TGT-701", "Target Intake", tuple()),
                ExecutionTreeNode("f2", "COV-703", "Coverage", tuple()),
                ExecutionTreeNode("f3", "HRM-711", "Harmony", tuple()),
            ),
        )
        return ExecutionTrace(
            run_id="optimization-trace",
            input_summary="OptimizedBundle",
            formula_traces=tuple(formula_traces),
            execution_tree=tree,
            warehouse_trace=tuple(),
            code_references=tuple(),
            final_outputs={"harmony_score": optimized_bundle.harmony_report.harmony_score},
            warnings=tuple(),
            errors=tuple(),
        )
