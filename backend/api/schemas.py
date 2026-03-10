"""Pydantic request / response schemas for the ADME API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class PredictionRequest(BaseModel):
    smiles: str = Field(..., max_length=500, examples=["CC(=O)OC1=CC=CC=C1C(=O)O"])

    @field_validator("smiles")
    @classmethod
    def smiles_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("SMILES must not be empty")
        return v.strip()


class BatchPredictionRequest(BaseModel):
    smiles_list: list[str] = Field(..., max_length=100)

    @field_validator("smiles_list")
    @classmethod
    def non_empty_list(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("smiles_list must not be empty")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class RegressionResult(BaseModel):
    value: float
    unit: str
    confidence: float | None = None


class ClassificationResult(BaseModel):
    probability: float
    prediction: bool


class RuleOfFive(BaseModel):
    passes: bool
    violations: list[str]


class PropertyResults(BaseModel):
    solubility: RegressionResult | None = None
    permeability: RegressionResult | None = None
    logp: RegressionResult | None = None
    cyp3a4_inhibitor: ClassificationResult | None = None
    herg_blocker: ClassificationResult | None = None


class PredictionResponse(BaseModel):
    smiles: str
    properties: PropertyResults
    warnings: list[str] = Field(default_factory=list)
    molecular_weight: float | None = None
    rule_of_five: RuleOfFive | None = None


class ValidationResponse(BaseModel):
    smiles: str
    valid: bool
    canonical_smiles: str | None = None
    molecular_weight: float | None = None
    num_atoms: int | None = None
    error: str | None = None


class ModelInfo(BaseModel):
    version: str
    model_type: str
    training_date: str | None = None
    properties: list[str]
    gnn_available: bool = False
    rf_available: bool = False
