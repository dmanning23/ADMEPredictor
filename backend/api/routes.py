"""FastAPI route definitions."""

from __future__ import annotations

import torch
from fastapi import APIRouter, HTTPException
from rdkit import Chem
from rdkit.Chem import Descriptors
from torch_geometric.data import Batch

from api.schemas import (
    BatchPredictionRequest,
    ClassificationResult,
    ModelInfo,
    PredictionRequest,
    PredictionResponse,
    PropertyResults,
    RegressionResult,
    RuleOfFive,
    ValidationResponse,
)
from featurization import smiles_to_graph, validate_smiles
import model_registry

router = APIRouter()

BINARY_THRESHOLD = 0.5


def _rule_of_five(mol) -> RuleOfFive:
    violations = []
    mw   = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd  = Descriptors.NumHDonors(mol)
    hba  = Descriptors.NumHAcceptors(mol)
    if mw > 500:  violations.append(f"MW {mw:.0f} > 500")
    if logp > 5:  violations.append(f"LogP {logp:.1f} > 5")
    if hbd > 5:   violations.append(f"HBD {hbd} > 5")
    if hba > 10:  violations.append(f"HBA {hba} > 10")
    return RuleOfFive(passes=len(violations) == 0, violations=violations)


@torch.no_grad()
def _gnn_predict_single(smiles: str) -> dict:
    gnn = model_registry.get_gnn()
    if gnn is None:
        return {}
    device = next(gnn.parameters()).device
    graph = smiles_to_graph(smiles)
    batch = Batch.from_data_list([graph]).to(device)
    preds = gnn(batch.x, batch.edge_index, batch.batch)
    return {k: float(v.item()) for k, v in preds.items()}


def _predict_one(smiles: str) -> PredictionResponse:
    if not validate_smiles(smiles):
        raise HTTPException(status_code=422, detail=f"Invalid SMILES: {smiles}")

    mol = Chem.MolFromSmiles(smiles)
    canonical = Chem.MolToSmiles(mol)

    gnn_preds = _gnn_predict_single(canonical)

    # Convert classification logits → probabilities
    for task in ["cyp3a4", "herg"]:
        if task in gnn_preds:
            gnn_preds[task] = float(torch.sigmoid(torch.tensor(gnn_preds[task])))

    rf_model = model_registry.get_rf()
    rf_preds = rf_model.predict(canonical) if rf_model else {}

    def regression(task: str, unit: str) -> RegressionResult | None:
        val = gnn_preds.get(task) or rf_preds.get(task)
        if val is None:
            return None
        return RegressionResult(value=round(float(val), 3), unit=unit)

    def classification(task: str) -> ClassificationResult | None:
        prob = gnn_preds.get(task) if gnn_preds else rf_preds.get(task)
        if prob is None:
            prob = rf_preds.get(task)
        if prob is None:
            return None
        prob = float(prob)
        return ClassificationResult(probability=round(prob, 3), prediction=prob >= BINARY_THRESHOLD)

    properties = PropertyResults(
        solubility=regression("solubility", "log mol/L"),
        permeability=regression("permeability", "log cm/s"),
        logp=regression("logp", "log"),
        cyp3a4_inhibitor=classification("cyp3a4"),
        herg_blocker=classification("herg"),
    )

    warnings = []
    mw = Descriptors.MolWt(mol)
    if mw > 800:
        warnings.append("Very large molecule — predictions may be less reliable.")

    return PredictionResponse(
        smiles=canonical,
        properties=properties,
        warnings=warnings,
        molecular_weight=round(mw, 2),
        rule_of_five=_rule_of_five(mol),
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """Predict ADME properties for a single molecule."""
    return _predict_one(request.smiles)


@router.post("/predict/batch", response_model=list[PredictionResponse])
async def predict_batch(request: BatchPredictionRequest) -> list[PredictionResponse]:
    """Predict ADME properties for up to 100 molecules."""
    results = []
    for smiles in request.smiles_list:
        try:
            results.append(_predict_one(smiles))
        except HTTPException as e:
            results.append(PredictionResponse(
                smiles=smiles,
                properties=PropertyResults(),
                warnings=[e.detail],
            ))
    return results


@router.get("/validate", response_model=ValidationResponse)
async def validate(smiles: str) -> ValidationResponse:
    """Validate a SMILES string and return basic molecular properties."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ValidationResponse(smiles=smiles, valid=False, error="Invalid SMILES")

    return ValidationResponse(
        smiles=smiles,
        valid=True,
        canonical_smiles=Chem.MolToSmiles(mol),
        molecular_weight=round(Descriptors.MolWt(mol), 2),
        num_atoms=mol.GetNumAtoms(),
    )


@router.get("/models/info", response_model=ModelInfo)
async def model_info() -> ModelInfo:
    """Return information about the loaded models."""
    gnn_available = model_registry.GNN_CHECKPOINT.exists()
    rf_available  = (model_registry.RF_CHECKPOINT / "rf_models.pkl").exists()
    return ModelInfo(
        version="0.1.0",
        model_type="GNN (GCNConv) + RF baseline",
        training_date=None,
        properties=["solubility", "permeability", "logp", "cyp3a4", "herg"],
        gnn_available=gnn_available,
        rf_available=rf_available,
    )
