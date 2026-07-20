from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class BreedNode(FormulaNode):
    id = "breed"
    formula_id = "BREED_RESOLVE_V1"
    dependencies = ["profile"]
    produces = ["breed_names", "breed_rows"]
    consumes = ["profile"]
    tables = ["breeds", "breed_aliases"]

    def execute(self, context: ExecutionContext) -> None:
        profile = context.profile
        names = [profile.primary_breed]
        if profile.secondary_breed:
            names.append(profile.secondary_breed)
        breeds_df = context.repository.breeds()
        self.emit_lookup(
            context,
            table="breeds",
            rows=len(breeds_df),
            selection_rule="normalize + match primary/secondary",
            columns=list(breeds_df.columns)[:12] if not breeds_df.empty else [],
        )
        rows = []
        if not breeds_df.empty and "breed" in breeds_df.columns:
            for name in names:
                key = context.repository.platform.normalize_breed_name(name) if hasattr(context.repository, "platform") else name
                hit = breeds_df[breeds_df["breed"].astype(str).str.lower() == str(key).lower()]
                if hit.empty:
                    hit = breeds_df[breeds_df["breed"].astype(str).str.lower().str.contains(str(key).lower(), na=False)]
                if not hit.empty:
                    rows.append(hit.iloc[0].to_dict())
        payload = {"breed_names": names, "breed_rows": rows, "resolved_count": len(rows)}
        context.set_output(self.id, payload)
        self.emit_step(context, name="resolve_breeds", inputs={"names": names}, result=len(rows))
