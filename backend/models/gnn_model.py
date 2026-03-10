"""
Graph Neural Network for multi-task ADME property prediction.

Architecture:
  - 3 GCNConv layers for message passing
  - Global mean + max pooling
  - Per-property MLP heads
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_add_pool, global_mean_pool


class MLP(nn.Module):
    def __init__(self, layer_sizes: list[int], dropout: float = 0.2):
        super().__init__()
        layers = []
        for in_size, out_size in zip(layer_sizes[:-1], layer_sizes[1:]):
            layers.extend([nn.Linear(in_size, out_size), nn.ReLU(), nn.Dropout(dropout)])
        layers.pop()   # remove last dropout
        layers.pop()   # remove last ReLU (raw logits / regression values)
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ADMEPredictor(nn.Module):
    """
    Multi-task GNN predicting solubility, permeability, CYP3A4, and hERG.

    Regression tasks  : solubility, permeability, logp
    Classification tasks (binary): cyp3a4, herg
    """

    REGRESSION_TASKS = ["solubility", "permeability", "logp"]
    CLASSIFICATION_TASKS = ["cyp3a4", "herg"]
    ALL_TASKS = REGRESSION_TASKS + CLASSIFICATION_TASKS

    def __init__(
        self,
        num_node_features: int,
        hidden_dim: int = 128,
        dropout: float = 0.2,
    ):
        super().__init__()

        self.conv1 = GCNConv(num_node_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim // 2)
        self.dropout = dropout

        pool_out = hidden_dim // 2  # after global mean pool

        self.heads = nn.ModuleDict({
            # Regression
            "solubility":   MLP([pool_out, 32, 1]),
            "permeability": MLP([pool_out, 32, 1]),
            "logp":         MLP([pool_out, 32, 1]),
            # Binary classification (logit output — use BCEWithLogitsLoss)
            "cyp3a4":       MLP([pool_out, 32, 1]),
            "herg":         MLP([pool_out, 32, 1]),
        })

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, batch: torch.Tensor) -> dict[str, torch.Tensor]:
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=self.dropout, training=self.training)

        x = F.relu(self.conv2(x, edge_index))
        x = F.dropout(x, p=self.dropout, training=self.training)

        x = F.relu(self.conv3(x, edge_index))

        x = global_mean_pool(x, batch)   # [batch_size, hidden_dim // 2]

        return {task: head(x).squeeze(-1) for task, head in self.heads.items()}
