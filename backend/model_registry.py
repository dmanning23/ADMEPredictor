"""
Singleton model registry — loads GNN + RF at startup, used by API routes.

Checkpoint layout expected (relative to CWD when uvicorn is started):
  checkpoints/gnn_best.pt   — GNN state dict
  checkpoints/rf/rf_models.pkl — RF sklearn models
"""

from __future__ import annotations

import logging
from pathlib import Path

import torch

log = logging.getLogger(__name__)

# ---- runtime constants ----
NUM_NODE_FEATURES = 157  # matches featurization._atom_features output
GNN_CHECKPOINT = Path("checkpoints/gnn_best.pt")
RF_CHECKPOINT  = Path("checkpoints/rf")

# ---- lazy singletons ----
_gnn_model = None
_rf_model  = None
_device    = None


def _get_device() -> torch.device:
    global _device
    if _device is None:
        if torch.cuda.is_available():
            _device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            _device = torch.device("mps")
        else:
            _device = torch.device("cpu")
    return _device


def get_gnn():
    global _gnn_model
    if _gnn_model is None:
        if not GNN_CHECKPOINT.exists():
            log.warning("GNN checkpoint not found at %s", GNN_CHECKPOINT)
            return None
        from models.gnn_model import ADMEPredictor
        device = _get_device()
        model = ADMEPredictor(num_node_features=NUM_NODE_FEATURES)
        model.load_state_dict(torch.load(GNN_CHECKPOINT, map_location=device))
        model.to(device)
        model.eval()
        _gnn_model = model
        log.info("GNN loaded from %s on %s", GNN_CHECKPOINT, device)
    return _gnn_model


def get_rf():
    global _rf_model
    if _rf_model is None:
        if not (RF_CHECKPOINT / "rf_models.pkl").exists():
            log.warning("RF checkpoint not found at %s", RF_CHECKPOINT)
            return None
        from models.rf_model import RFADMEPredictor
        _rf_model = RFADMEPredictor.load(RF_CHECKPOINT)
        log.info("RF models loaded from %s", RF_CHECKPOINT)
    return _rf_model
