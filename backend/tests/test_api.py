"""Integration tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

ASPIRIN = "CC(=O)OC1=CC=CC=C1C(=O)O"


class TestHealth:
    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestValidate:
    def test_valid_smiles(self):
        r = client.get("/validate", params={"smiles": ASPIRIN})
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is True
        assert data["molecular_weight"] == pytest.approx(180.16, abs=0.1)

    def test_invalid_smiles(self):
        r = client.get("/validate", params={"smiles": "not_valid"})
        assert r.status_code == 200
        assert r.json()["valid"] is False


class TestPredict:
    def test_predict_returns_501_until_implemented(self):
        r = client.post("/predict", json={"smiles": ASPIRIN})
        assert r.status_code == 501

    def test_empty_smiles_rejected(self):
        r = client.post("/predict", json={"smiles": ""})
        assert r.status_code == 422


class TestModelInfo:
    def test_returns_info(self):
        r = client.get("/models/info")
        assert r.status_code == 200
        data = r.json()
        assert "version" in data
        assert "properties" in data
