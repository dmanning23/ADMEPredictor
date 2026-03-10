"""Unit tests for featurization.py"""

import pytest
from featurization import compute_descriptors, smiles_to_graph, validate_smiles


ASPIRIN = "CC(=O)OC1=CC=CC=C1C(=O)O"
CAFFEINE = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
INVALID = "not_a_smiles"


class TestValidateSmiles:
    def test_valid_aspirin(self):
        assert validate_smiles(ASPIRIN) is True

    def test_valid_caffeine(self):
        assert validate_smiles(CAFFEINE) is True

    def test_invalid_returns_false(self):
        assert validate_smiles(INVALID) is False

    def test_empty_string(self):
        assert validate_smiles("") is False

    def test_too_long(self):
        assert validate_smiles("C" * 501) is False


class TestSmilesToGraph:
    def test_returns_data_object(self):
        from torch_geometric.data import Data
        data = smiles_to_graph(ASPIRIN)
        assert isinstance(data, Data)

    def test_node_features_shape(self):
        data = smiles_to_graph(ASPIRIN)
        assert data.x.ndim == 2
        assert data.x.shape[0] == 13  # Aspirin has 13 heavy atoms

    def test_edge_index_shape(self):
        data = smiles_to_graph(ASPIRIN)
        assert data.edge_index.shape[0] == 2

    def test_invalid_smiles_raises(self):
        with pytest.raises(ValueError):
            smiles_to_graph(INVALID)


class TestComputeDescriptors:
    def test_returns_array(self):
        import numpy as np
        desc = compute_descriptors(ASPIRIN)
        assert isinstance(desc, np.ndarray)

    def test_consistent_length(self):
        d1 = compute_descriptors(ASPIRIN)
        d2 = compute_descriptors(CAFFEINE)
        assert len(d1) == len(d2)

    def test_invalid_smiles_raises(self):
        with pytest.raises(ValueError):
            compute_descriptors(INVALID)
