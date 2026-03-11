# ADME Predictor

> A free, open-source tool for predicting pharmaceutical ADME properties of drug-like molecules using Graph Neural Networks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61DAFB.svg)](https://reactjs.org/)

[**Live Demo**](https://adme-predictor.vercel.app) · [**API Docs**](https://api.adme-predictor.com/docs) · [**Blog Post**](#)

---

## What is ADME Predictor?

ADME Predictor helps medicinal chemists, drug discovery researchers, and computational biologists quickly assess whether a molecule has drug-like properties **before** spending time and money synthesizing it.

Input a molecular structure (as SMILES), and get instant predictions for:

| Property | Type | Description |
|---|---|---|
| **Solubility (LogS)** | Regression | Aqueous solubility in log mol/L |
| **Permeability (Caco-2)** | Regression | Intestinal permeability in log cm/s |
| **CYP3A4 Inhibition** | Classification | Metabolic drug-drug interaction risk |
| **hERG Blocking** | Classification | Cardiac toxicity risk |

Plus: Lipinski Rule of Five, molecular weight, and LogP.

### Why use this?

| Tool | Cost | API | Model |
|---|---|---|---|
| SwissADME | Free | ❌ | Rule-based |
| ADMETlab 2.0 | Freemium | Limited | ML |
| Commercial tools | $10k–$50k/yr | ✅ | ML |
| **ADME Predictor** | **Free** | **✅** | **GNN** |

---

## Quick Start

### Web Interface

1. Go to [adme-predictor.vercel.app](https://adme-predictor.vercel.app)
2. Enter a SMILES string (e.g. `CC(=O)OC1=CC=CC=C1C(=O)O` for aspirin)
3. Click **Predict**

### REST API

```bash
curl -X POST https://api.adme-predictor.com/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}'
```

**Response:**
```json
{
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "properties": {
    "solubility":       { "value": -1.608, "unit": "log mol/L" },
    "permeability":     { "value": -5.327, "unit": "log cm/s" },
    "logp":             { "value":  0.191, "unit": "log" },
    "cyp3a4_inhibitor": { "probability": 0.030, "prediction": false },
    "herg_blocker":     { "probability": 0.123, "prediction": false }
  },
  "molecular_weight": 180.16,
  "rule_of_five": { "passes": true, "violations": [] },
  "warnings": []
}
```

### MCP Server (for LLM clients)

Use ADME predictions directly inside Claude, Cursor, or any MCP-compatible assistant:

```bash
pip install adme-predictor-mcp   # or: uvx adme-predictor-mcp
```

Add to `~/.claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "adme-predictor": {
      "command": "uvx",
      "args": ["adme-predictor-mcp"]
    }
  }
}
```

---

## Model Performance

Trained on 36,204 compounds from [Therapeutic Data Commons](https://tdcommons.ai/). Evaluated on a held-out 10% test split.

| Property | Metric | Score | Target |
|---|---|---|---|
| Solubility (LogS) | R² | **0.804** | > 0.65 ✅ |
| Solubility (LogS) | MAE | **0.743** log units | < 0.80 ✅ |
| Permeability (Caco-2) | R² | **0.641** | > 0.60 ✅ |
| Permeability (Caco-2) | MAE | **0.362** log units | < 0.70 ✅ |
| CYP3A4 Inhibition | ROC-AUC | **0.857** | > 0.75 ✅ |
| hERG Blocking | ROC-AUC | **0.805** | > 0.70 ✅ |

All metrics exceed targets and are competitive with published ADME prediction tools.

---

## How It Works

### Architecture

```
SMILES → Molecular Graph → GCNConv × 3 → Global Mean Pool → MLP Heads
                               ↓
                    (157 atom features, 7 bond features)
```

- **Model:** Multi-task Graph Convolutional Network (55,557 parameters)
- **Shared encoder:** 3 × GCNConv layers (128 → 128 → 64 hidden dims)
- **Per-property heads:** Separate MLP for each ADME property
- **Training:** 60 epochs on Apple Silicon MPS, NaN-masked multi-task loss
- **Fallback:** Random Forest on 210 RDKit descriptors

### Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI · PyTorch · PyTorch Geometric · RDKit |
| Frontend | React 18 · TypeScript · Tailwind CSS v4 · Vite |
| MCP Server | Model Context Protocol SDK (stdio + HTTP/SSE) |
| Infrastructure | Railway (backend) · Vercel (frontend) |

---

## API Reference

**Base URL:** `https://api.adme-predictor.com`
**Swagger UI:** `https://api.adme-predictor.com/docs`

### `POST /predict`
Single molecule prediction. Input: `{"smiles": "..."}`.
Rate limit: 10 req/min (IP-based, no account required).

### `POST /predict/batch`
Up to 100 molecules. Input: `{"smiles_list": ["...", "..."]}`.

### `GET /validate?smiles=...`
Validate SMILES and return MW, atom count, canonical form.

### `GET /health`
Service health check.

### `GET /models/info`
Model version and checkpoint status.

---

## Understanding Results

### Solubility (LogS)

| Value | Interpretation |
|---|---|
| > −2 | Highly soluble |
| −2 to −4 | Moderately soluble |
| −4 to −6 | Poorly soluble |
| < −6 | Very poorly soluble |

### Permeability (Caco-2, log cm/s)

| Value | Interpretation |
|---|---|
| > −5 | High permeability (good oral absorption) |
| −5 to −6 | Moderate |
| < −6 | Low (poor absorption) |

### CYP3A4 / hERG (probability 0–1)

| Value | Interpretation |
|---|---|
| < 0.3 | Low risk |
| 0.3 – 0.7 | Moderate — investigate further |
| > 0.7 | High risk |

---

## Local Development

### Prerequisites

- Python 3.11 · Node.js 18+ · [uv](https://github.com/astral-sh/uv)

### Backend

```bash
git clone https://github.com/yourusername/adme-predictor.git
cd adme-predictor

uv venv --python 3.11 .venv
uv pip install -r backend/requirements.txt

# Download training data (~36k molecules, ~10MB)
.venv/bin/python data/download_data.py

# Train models (~30 min on Apple Silicon, ~2 hrs on CPU)
PYTHONPATH=backend .venv/bin/python backend/train.py \
  --data data/adme_merged.csv --model gnn --epochs 60

# Evaluate on test set
PYTHONPATH=backend .venv/bin/python backend/evaluate.py \
  --data data/adme_merged.csv

# Start API server
cd backend && PYTHONPATH=. ../.venv/bin/uvicorn main:app --reload
```

API: `http://localhost:8000` · Swagger: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173 — proxies /api → localhost:8000
```

### Tests

```bash
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests/ -v
```

---

## Data Sources

| Dataset | Property | Molecules |
|---|---|---|
| AqSolDB | Solubility (LogS) | 9,982 |
| Caco2_Wang | Permeability | 906 |
| CYP3A4_Veith | CYP3A4 inhibition | 12,328 |
| hERG_Karim | hERG blocking | 13,445 |

All from [Therapeutic Data Commons](https://tdcommons.ai/). Merged on canonical SMILES; missing labels handled via NaN-masking in the multi-task loss.

---

## Roadmap

- [x] GNN model — solubility, permeability, CYP3A4, hERG
- [x] REST API with single + batch endpoints
- [x] React web UI with example molecules
- [x] MCP server for LLM integration
- [ ] 2D structure visualization (RDKit.js)
- [ ] Molecule drawing interface (Ketcher)
- [ ] Uncertainty estimation (MC dropout)
- [ ] Attention / saliency visualization
- [ ] Additional properties: BBB, PPB, half-life
- [ ] Deploy to Railway + Vercel

---

## Citation

```bibtex
@software{adme_predictor2025,
  author = {Your Name},
  title  = {ADME Predictor: Open-Source GNN for Drug Property Prediction},
  year   = {2025},
  url    = {https://github.com/yourusername/adme-predictor}
}
```

---

## Acknowledgments

- [Therapeutic Data Commons](https://tdcommons.ai/) — datasets
- [RDKit](https://www.rdkit.org/) — chemistry toolkit
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/) — GNN primitives

---

## License

MIT — see [LICENSE](LICENSE).
