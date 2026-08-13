# TRACE_CANONICAL_CONTRACT

## Typed trace composition
Recommended layered trace architecture:
- RuntimeTrace / StageTrace (`repository/models/trace.py`)
- MathematicalFormulaTrace (`repository/mathematics/models.py`)
- Debugger FormulaTrace + ExecutionTrace (`repository/math_debugger/models.py`)
- OptimizationTrace (`repository/optimization/models.py`)
- App narrative/debug traces (`app/agent/calculation_trace.py`, `app/agent/pipeline_trace.py`)

## Required provenance fields
Canonical trace system must preserve:
- stage
- execution run id
- formula id
- formula version
- equation
- substituted equation
- intermediate variables
- parameter values
- warehouse rows/fact ids
- evidence ids
- citations (paper name/link/quote)
- final output
- timing
- warnings/errors

## Core question support
Trace contracts must support deterministic reconstruction of:
input -> warehouse fact -> formula -> parameter -> substituted equation -> intermediate value -> final value.
