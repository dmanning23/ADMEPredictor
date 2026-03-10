"""
HTTP client that calls the FastAPI backend from the MCP server.
"""

from __future__ import annotations

import os

import httpx

BACKEND_URL = os.getenv("ADME_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30.0


async def predict_adme(smiles: str) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BACKEND_URL}/predict", json={"smiles": smiles})
        r.raise_for_status()
        return r.json()


async def predict_adme_batch(smiles_list: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(f"{BACKEND_URL}/predict/batch", json={"smiles_list": smiles_list})
        r.raise_for_status()
        return r.json()


async def validate_smiles(smiles: str) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{BACKEND_URL}/validate", params={"smiles": smiles})
        r.raise_for_status()
        return r.json()
