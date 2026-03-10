"""
Random Forest baseline for ADME property prediction.

Uses RDKit molecular descriptors as features. Serves as:
  - Fallback if GNN inference fails
  - Baseline to compare GNN performance against
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from featurization import compute_descriptors


REGRESSION_TASKS = ["solubility", "permeability", "logp"]
CLASSIFICATION_TASKS = ["cyp3a4", "herg"]


class RFADMEPredictor:
    """Wrapper holding one RF model per ADME property."""

    def __init__(self, n_estimators: int = 200, random_state: int = 42):
        self.models: dict[str, RandomForestRegressor | RandomForestClassifier] = {}
        self._init_models(n_estimators, random_state)

    def _init_models(self, n_estimators: int, random_state: int) -> None:
        for task in REGRESSION_TASKS:
            self.models[task] = RandomForestRegressor(
                n_estimators=n_estimators, random_state=random_state, n_jobs=-1
            )
        for task in CLASSIFICATION_TASKS:
            self.models[task] = RandomForestClassifier(
                n_estimators=n_estimators, random_state=random_state, n_jobs=-1
            )

    def fit(self, smiles_list: list[str], labels: dict[str, np.ndarray]) -> None:
        """Train all property models, skipping NaN labels per task."""
        smiles_arr = np.array(smiles_list)
        X_all = np.vstack([compute_descriptors(s) for s in smiles_list])
        # Clip inf values then impute NaN descriptors with column means
        X_all = np.clip(X_all, -1e9, 1e9)
        col_means = np.nanmean(X_all, axis=0)
        col_means = np.nan_to_num(col_means, nan=0.0)
        nan_mask = np.isnan(X_all)
        X_all[nan_mask] = np.take(col_means, np.where(nan_mask)[1])

        for task, model in self.models.items():
            if task not in labels:
                continue
            y = labels[task]
            valid = ~np.isnan(y.astype(float))
            if valid.sum() == 0:
                continue
            model.fit(X_all[valid], y[valid])

    def predict(self, smiles: str) -> dict[str, float]:
        """Return predictions for all properties for a single molecule."""
        x = compute_descriptors(smiles).reshape(1, -1)
        x = np.clip(x, -1e9, 1e9)
        x = np.nan_to_num(x, nan=0.0)
        from sklearn.utils.validation import check_is_fitted
        from sklearn.exceptions import NotFittedError

        results = {}
        for task, model in self.models.items():
            try:
                check_is_fitted(model)
            except NotFittedError:
                continue
            if task in CLASSIFICATION_TASKS:
                results[task] = float(model.predict_proba(x)[0, 1])
            else:
                results[task] = float(model.predict(x)[0])
        return results

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "rf_models.pkl", "wb") as f:
            pickle.dump(self.models, f)

    @classmethod
    def load(cls, path: str | Path) -> "RFADMEPredictor":
        path = Path(path)
        instance = cls.__new__(cls)
        with open(path / "rf_models.pkl", "rb") as f:
            instance.models = pickle.load(f)
        return instance
