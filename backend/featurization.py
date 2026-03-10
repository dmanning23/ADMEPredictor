"""
Molecular featurization utilities.

Converts SMILES strings to:
  - PyTorch Geometric Data objects (for GNN)
  - RDKit descriptor vectors (for Random Forest)
"""

from __future__ import annotations

import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
import torch
from torch_geometric.data import Data


# ---------------------------------------------------------------------------
# Atom / bond feature helpers
# ---------------------------------------------------------------------------

ATOM_FEATURES = {
    "atomic_num": list(range(1, 119)),
    "degree": list(range(0, 11)),
    "formal_charge": [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
    "hybridization": [
        Chem.rdchem.HybridizationType.SP,
        Chem.rdchem.HybridizationType.SP2,
        Chem.rdchem.HybridizationType.SP3,
        Chem.rdchem.HybridizationType.SP3D,
        Chem.rdchem.HybridizationType.SP3D2,
    ],
    "num_hs": [0, 1, 2, 3, 4],
}

BOND_FEATURES = {
    "bond_type": [
        Chem.rdchem.BondType.SINGLE,
        Chem.rdchem.BondType.DOUBLE,
        Chem.rdchem.BondType.TRIPLE,
        Chem.rdchem.BondType.AROMATIC,
    ],
}


def _one_hot(value, choices: list) -> list[int]:
    """One-hot encode value against choices; last element = 'other'."""
    encoding = [0] * (len(choices) + 1)
    idx = choices.index(value) if value in choices else len(choices)
    encoding[idx] = 1
    return encoding


def _atom_features(atom) -> list[int]:
    features = (
        _one_hot(atom.GetAtomicNum(), ATOM_FEATURES["atomic_num"])
        + _one_hot(atom.GetDegree(), ATOM_FEATURES["degree"])
        + _one_hot(atom.GetFormalCharge(), ATOM_FEATURES["formal_charge"])
        + _one_hot(atom.GetHybridization(), ATOM_FEATURES["hybridization"])
        + _one_hot(atom.GetTotalNumHs(), ATOM_FEATURES["num_hs"])
        + [int(atom.GetIsAromatic())]
        + [int(atom.IsInRing())]
    )
    return features


def _bond_features(bond) -> list[int]:
    features = (
        _one_hot(bond.GetBondType(), BOND_FEATURES["bond_type"])
        + [int(bond.GetIsConjugated())]
        + [int(bond.IsInRing())]
    )
    return features


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_smiles(smiles: str) -> bool:
    """Return True if SMILES is valid and parseable by RDKit."""
    if not smiles or len(smiles) > 500:
        return False
    mol = Chem.MolFromSmiles(smiles)
    return mol is not None


def smiles_to_graph(smiles: str) -> Data:
    """
    Convert a SMILES string to a PyTorch Geometric Data object.

    Returns a Data object with:
        x          : Node feature matrix  [num_atoms, num_atom_features]
        edge_index : Edge connectivity    [2, num_bonds * 2]  (undirected)
        edge_attr  : Edge feature matrix  [num_bonds * 2, num_bond_features]
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    # Node features
    atom_feats = [_atom_features(atom) for atom in mol.GetAtoms()]
    x = torch.tensor(atom_feats, dtype=torch.float)

    # Edge index + edge features (both directions)
    edge_indices = []
    edge_attrs = []
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        feat = _bond_features(bond)
        edge_indices += [[i, j], [j, i]]
        edge_attrs += [feat, feat]

    # bond feature dim: 4 bond types + 1 "other" + is_conjugated + is_in_ring = 7
    BOND_FEATURE_DIM = len(BOND_FEATURES["bond_type"]) + 1 + 2

    if edge_indices:
        edge_index = torch.tensor(edge_indices, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor(edge_attrs, dtype=torch.float)
    else:
        edge_index = torch.zeros((2, 0), dtype=torch.long)
        edge_attr = torch.zeros((0, BOND_FEATURE_DIM), dtype=torch.float)

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)


def compute_descriptors(smiles: str) -> np.ndarray:
    """
    Compute a vector of RDKit molecular descriptors for classical ML.

    Returns a 1-D numpy array of floats (NaN-filled for invalid descriptors).
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    descriptor_fns = Descriptors.descList
    values = []
    for _, fn in descriptor_fns:
        try:
            values.append(float(fn(mol)))
        except Exception:
            values.append(float("nan"))

    arr = np.array(values, dtype=np.float64)
    arr = np.clip(arr, -1e9, 1e9)
    return arr.astype(np.float32)
