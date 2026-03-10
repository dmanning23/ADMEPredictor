"""
Training pipeline for ADME property prediction models.

Usage:
    python train.py --property solubility --model gnn --epochs 100
    python train.py --property all --model rf
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch_geometric.loader import DataLoader

from featurization import smiles_to_graph, validate_smiles
from models.gnn_model import ADMEPredictor
from models.rf_model import RFADMEPredictor

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

CHECKPOINTS_DIR = Path("checkpoints")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load CSV dataset. Expected columns: smiles + one or more property columns."""
    df = pd.read_csv(path)
    log.info(f"Loaded {len(df)} rows from {path}")
    return df


def split_dataset(df: pd.DataFrame, val_frac: float = 0.1, test_frac: float = 0.1, seed: int = 42):
    """Simple random split. TODO: replace with scaffold split to avoid data leakage."""
    train_val, test = train_test_split(df, test_size=test_frac, random_state=seed)
    val_size = val_frac / (1 - test_frac)
    train, val = train_test_split(train_val, test_size=val_size, random_state=seed)
    log.info(f"Split: train={len(train)}, val={len(val)}, test={len(test)}")
    return train, val, test


# ---------------------------------------------------------------------------
# GNN training
# ---------------------------------------------------------------------------

def build_graph_dataset(df: pd.DataFrame, property_cols: list[str]):
    """Convert dataframe rows to PyG Data objects with y labels."""
    graphs = []
    for _, row in df.iterrows():
        smiles = row["smiles"]
        if not validate_smiles(smiles):
            continue
        try:
            data = smiles_to_graph(smiles)
            y_vals = []
            for col in property_cols:
                val = row.get(col, float("nan"))
                y_vals.append(float(val) if pd.notna(val) else float("nan"))
            # Shape (1, num_props) so PyG batches to (batch_size, num_props)
            data.y = torch.tensor(y_vals, dtype=torch.float).unsqueeze(0)
            graphs.append(data)
        except Exception as e:
            log.warning(f"Skipping {smiles}: {e}")
    return graphs


def train_gnn(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    property_cols: list[str],
    epochs: int = 100,
    batch_size: int = 32,
    lr: float = 1e-3,
    patience: int = 10,
) -> ADMEPredictor:
    """Train the GNN model with early stopping."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    log.info(f"Training on {device}")

    train_graphs = build_graph_dataset(train_df, property_cols)
    val_graphs = build_graph_dataset(val_df, property_cols)

    train_loader = DataLoader(train_graphs, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_graphs, batch_size=batch_size)

    num_node_features = train_graphs[0].x.shape[1]
    model = ADMEPredictor(num_node_features=num_node_features).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)

    best_val_loss = float("inf")
    epochs_without_improvement = 0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            preds = model(batch.x, batch.edge_index, batch.batch)
            loss = _compute_loss(preds, batch.y, property_cols)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        val_loss = _evaluate(model, val_loader, property_cols, device)
        log.info(f"Epoch {epoch:3d} | train_loss={total_loss/len(train_loader):.4f} | val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0
            _save_gnn(model, CHECKPOINTS_DIR / "gnn_best.pt")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                log.info(f"Early stopping at epoch {epoch}")
                break

    return model


def _compute_loss(preds: dict[str, torch.Tensor], y: torch.Tensor, property_cols: list[str]) -> torch.Tensor:
    """MSE for regression, BCE for classification. Skip NaN labels."""
    from models.gnn_model import ADMEPredictor
    loss = torch.tensor(0.0, requires_grad=True)
    for i, col in enumerate(property_cols):
        col_y = y[:, i]
        valid = ~torch.isnan(col_y)
        if valid.sum() == 0:
            continue
        col_pred = preds.get(col)
        if col_pred is None:
            continue
        if col in ADMEPredictor.CLASSIFICATION_TASKS:
            loss = loss + torch.nn.functional.binary_cross_entropy_with_logits(col_pred[valid], col_y[valid])
        else:
            loss = loss + torch.nn.functional.mse_loss(col_pred[valid], col_y[valid])
    return loss


@torch.no_grad()
def _evaluate(model, loader, property_cols, device) -> float:
    model.eval()
    total = 0.0
    for batch in loader:
        batch = batch.to(device)
        preds = model(batch.x, batch.edge_index, batch.batch)
        total += _compute_loss(preds, batch.y, property_cols).item()
    return total / len(loader)


def _save_gnn(model: ADMEPredictor, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)
    log.info(f"Saved GNN checkpoint to {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Train ADME prediction models")
    parser.add_argument("--data", required=True, help="Path to training CSV")
    parser.add_argument("--model", choices=["gnn", "rf"], default="gnn")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    df = load_dataset(args.data)
    property_cols = [c for c in df.columns if c != "smiles"]
    train_df, val_df, test_df = split_dataset(df)

    if args.model == "gnn":
        train_gnn(train_df, val_df, property_cols, epochs=args.epochs, batch_size=args.batch_size)
    else:
        labels = {col: train_df[col].values for col in property_cols}
        rf = RFADMEPredictor()
        rf.fit(train_df["smiles"].tolist(), labels)
        rf.save(CHECKPOINTS_DIR / "rf")
        log.info("RF model saved.")


if __name__ == "__main__":
    main()
