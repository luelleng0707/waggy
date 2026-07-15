"""Pydantic v2 models for PPIE agent state and API contracts."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DogProfileInput(BaseModel):
    name: str = Field(..., examples=["dolly"])
    primary_breed: str = Field(..., examples=["Golden Retriever"])
    secondary_breed: Optional[str] = Field(default=None, examples=["Labrador Retriever"])
    breed_split_pct: float = Field(default=50.0, ge=0.0, le=100.0)
    age_years: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    current_environment: str = Field(..., examples=["Shanghai Summer"])
    activity_level: str = Field(default="High", examples=["High"])
    sex: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = Field(default=None, examples=["2021-03-15"])
    height_cm: Optional[float] = None
    bcs: Optional[float] = None
    observed_conditions: List[str] = Field(default_factory=list)


class ProductFulfillment(BaseModel):
    product_id: str
    product_name: str
    standard_daily_feeding: str
    yielded_active_content: str
    supplemental_boost_required: bool
    therapeutic_shortfall: str
    purchase_url: Optional[str] = None
    unit_cost_per_bag: Optional[float] = None
    coverage_pct: float = 0.0


class ActiveIntervention(BaseModel):
    active_ingredient: str
    required_dosage: str
    commercial_fulfillment: Dict[str, ProductFulfillment] = Field(default_factory=dict)


class WellnessReportPayload(BaseModel):
    condition: str
    weighted_priority_score: float
    targeted_intervention: ActiveIntervention


class PipelineTraceEntry(BaseModel):
    stage: str
    message: str
    record_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentPipelineState(BaseModel):
    profile: DogProfileInput
    biology: Dict[str, Any] = Field(default_factory=dict)
    epidemiology: Dict[str, Any] = Field(default_factory=dict)
    management: Dict[str, Any] = Field(default_factory=dict)
    nutrition: Dict[str, Any] = Field(default_factory=dict)
    products: Dict[str, Any] = Field(default_factory=dict)
    feeding_plan: Dict[str, Any] = Field(default_factory=dict)
    trace: List[PipelineTraceEntry] = Field(default_factory=list)
