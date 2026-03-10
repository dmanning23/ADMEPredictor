"""
MCP tool definitions for ADME property prediction.
"""

from __future__ import annotations

from mcp.server import Server

from mcp_server import client as backend


def register_tools(server: Server) -> None:
    @server.tool()
    async def predict_adme(smiles: str) -> dict:
        """
        Predict ADME properties for a molecule given its SMILES string.
        Returns solubility (LogS), Caco-2 permeability, CYP3A4 inhibition,
        and hERG blocking probability.

        Args:
            smiles: SMILES string of the molecule (e.g. "CC(=O)OC1=CC=CC=C1C(=O)O" for aspirin)
        """
        return await backend.predict_adme(smiles)

    @server.tool()
    async def predict_adme_batch(smiles_list: list[str]) -> list[dict]:
        """
        Predict ADME properties for multiple molecules at once (up to 100).

        Args:
            smiles_list: List of SMILES strings
        """
        if len(smiles_list) > 100:
            raise ValueError("Maximum 100 molecules per batch request")
        return await backend.predict_adme_batch(smiles_list)

    @server.tool()
    async def validate_smiles(smiles: str) -> dict:
        """
        Validate a SMILES string and return basic molecular properties
        (molecular weight, atom count, canonical SMILES).
        Useful for checking a structure before running full ADME predictions.

        Args:
            smiles: SMILES string to validate
        """
        return await backend.validate_smiles(smiles)
