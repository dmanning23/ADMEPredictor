"""
Evaluate trained models on the held-out test set.

Usage (from project root):
    PYTHONPATH=backend .venv/bin/python backend/evaluate.py --data data/adme_merged.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score
from torch_geometric.loader import DataLoader

from featurization import smiles_to_graph, validate_smiles
from models.gnn_model import ADMEPredictor
from train import split_dataset

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

CHECKPOINTS_DIR = Path("checkpoints")
NUM_NODE_FEATURES = 157
PROPERTY_COLS = ["solubility", "permeability", "cyp3a4", "herg"]
REGRESSION_TASKS = ["solubility", "permeability"]
CLASSIFICATION_TASKS = ["cyp3a4", "herg"]


def build_graph_dataset(df: pd.DataFrame):
    graphs = []
    for _, row in df.iterrows():
        smiles = row["smiles"]
        if not validate_smiles(smiles):
            continue
        try:
            data = smiles_to_graph(smiles)
            y_vals = [float(row.get(col, float("nan"))) if pd.notna(row.get(col)) else float("nan")
                      for col in PROPERTY_COLS]
            data.y = torch.tensor(y_vals, dtype=torch.float).unsqueeze(0)
            graphs.append(data)
        except Exception:
            pass
    return graphs


@torch.no_grad()
def evaluate_gnn(model, loader, device):
    model.eval()
    all_preds = {col: [] for col in PROPERTY_COLS}
    all_true  = {col: [] for col in PROPERTY_COLS}

    for batch in loader:
        batch = batch.to(device)
        preds = model(batch.x, batch.edge_index, batch.batch)
        y = batch.y  # shape (batch_size, num_props)

        for i, col in enumerate(PROPERTY_COLS):
            col_y = y[:, i].cpu().numpy()
            col_pred = preds[col].cpu().numpy()
            valid = ~np.isnan(col_y)
            all_true[col].extend(col_y[valid].tolist())
            all_preds[col].extend(col_pred[valid].tolist())

    return all_preds, all_true


def r2_score(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0


def mae(y_true, y_pred):
    return np.mean(np.abs(np.array(y_true) - np.array(y_pred)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    _, _, test_df = split_dataset(df)

    log.info(f"Test set: {len(test_df)} molecules")
    log.info("Building graph dataset...")
    test_graphs = build_graph_dataset(test_df)
    test_loader = DataLoader(test_graphs, batch_size=64)

    checkpoint = CHECKPOINTS_DIR / "gnn_best.pt"
    if not checkpoint.exists():
        log.error(f"Checkpoint not found: {checkpoint}")
        return

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = ADMEPredictor(num_node_features=NUM_NODE_FEATURES).to(device)
    model.load_state_dict(torch.load(checkpoint, map_location=device))
    log.info(f"Loaded checkpoint from {checkpoint}\n")

    preds, true = evaluate_gnn(model, test_loader, device)

    log.info("=" * 50)
    log.info("GNN TEST SET PERFORMANCE")
    log.info("=" * 50)
    for col in PROPERTY_COLS:
        if not true[col]:
            log.info(f"  {col}: no test labels")
            continue
        if col in REGRESSION_TASKS:
            r2  = r2_score(true[col], preds[col])
            err = mae(true[col], preds[col])
            log.info(f"  {col:15s}  R²={r2:.3f}  MAE={err:.3f}")
        else:
            # sigmoid for classification logits
            probs = torch.sigmoid(torch.tensor(preds[col])).numpy()
            try:
                auc = roc_auc_score(true[col], probs)
                log.info(f"  {col:15s}  ROC-AUC={auc:.3f}")
            except Exception as e:
                log.info(f"  {col:15s}  ROC-AUC=N/A ({e})")
    log.info("=" * 50)


if __name__ == "__main__":
    main()
