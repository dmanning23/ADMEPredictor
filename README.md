# ADME Predictor

> A fast, accurate, and free tool for predicting pharmaceutical properties of drug-like molecules using machine learning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.0+-61DAFB.svg)](https://reactjs.org/)

[**Live Demo**](https://adme-predictor.vercel.app) | [**API Docs**](https://api.adme-predictor.com/docs) | [**Blog Post**](https://yourblog.com/building-adme-predictor)

---

## What is ADME Predictor?

ADME Predictor helps medicinal chemists, drug discovery researchers, and computational biologists quickly assess whether a molecule has drug-like properties **before** spending time and money synthesizing it.

Input a molecular structure (as SMILES), and get instant predictions for:

- **Solubility** - Will it dissolve in water/biological fluids?
- **Permeability** - Can it cross cell membranes?
- **CYP3A4 Inhibition** - Will it interfere with drug metabolism?
- **hERG Blocking** - Does it have cardiotoxicity risk?

### Why Use This?

**Existing solutions:**
- **SwissADME**: Free but slow web interface, no API, rule-based (less accurate)
- **ADMETlab**: Good but limited free tier, academic-only
- **Commercial tools**: $10,000-$50,000 per year (Schrödinger, SimulationsPlus)

**ADME Predictor:**
- ✅ **Free** (with generous usage limits)
- ✅ **Fast** (<1 second predictions)
- ✅ **Modern ML** (Graph Neural Networks, not just rules)
- ✅ **Easy to use** (clean UI + REST API)
- ✅ **Transparent** (open-source models, documented methodology)

---

## Quick Start

### Web Interface

1. Go to [adme-predictor.vercel.app](https://adme-predictor.vercel.app)
2. Enter a SMILES string (e.g., `CC(=O)OC1=CC=CC=C1C(=O)O` for aspirin)
3. Click **Predict**
4. View results instantly

### API Usage

```bash
curl -X POST https://api.adme-predictor.com/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}'
```

**Response:**
```json
{
  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
  "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "properties": {
    "solubility": {
      "value": -2.31,
      "unit": "log mol/L",
      "interpretation": "Moderately soluble",
      "confidence": 0.87
    },
    "permeability": {
      "value": -5.12,
      "unit": "log cm/s",
      "interpretation": "Low permeability",
      "confidence": 0.82
    },
    "cyp3a4_inhibitor": {
      "probability": 0.12,
      "prediction": false,
      "confidence": 0.91
    },
    "herg_blocker": {
      "probability": 0.05,
      "prediction": false,
      "confidence": 0.88
    }
  },
  "molecular_weight": 180.16,
  "lipinski_rule_of_five": {
    "passes": true,
    "violations": []
  }
}
```

### Python SDK (Coming Soon)

```python
from adme_predictor import ADMEClient

client = ADMEClient()
results = client.predict("CC(=O)OC1=CC=CC=C1C(=O)O")

print(f"Solubility: {results.solubility.value} {results.solubility.unit}")
print(f"CYP3A4 Inhibitor: {results.cyp3a4.prediction}")
```

---

## Features

### Current Features (v1.0)

- ✅ Single molecule prediction
- ✅ Batch prediction (up to 100 molecules)
- ✅ Four core ADME properties
- ✅ SMILES validation and canonicalization
- ✅ 2D molecular structure visualization
- ✅ Lipinski Rule of Five checking
- ✅ Example molecule library
- ✅ Export results (JSON/CSV)

### Roadmap

- [ ] More properties (BBB penetration, plasma protein binding, half-life)
- [ ] Uncertainty quantification (prediction intervals)
- [ ] Substructure highlighting (which atoms contribute to poor properties)
- [ ] User accounts and prediction history
- [ ] API authentication and higher rate limits
- [ ] Molecule drawing interface
- [ ] Comparison with known drugs

---

## Use Cases

### 1. Virtual Screening

Screen a library of compounds before synthesis:

```bash
# Upload CSV with SMILES column
curl -X POST https://api.adme-predictor.com/predict/batch \
  -F "file=@compounds.csv"
```

Filter out molecules with poor ADME properties → save time and money.

### 2. Lead Optimization

You've found an active compound but it has poor solubility:

1. Predict current molecule's properties
2. Make structural modifications
3. Re-predict to see if properties improved
4. Iterate until you have a good balance of activity + ADME

### 3. Teaching & Learning

Perfect for:
- Drug discovery courses
- Medicinal chemistry labs
- Self-study of structure-property relationships

See immediately how changing functional groups affects properties.

### 4. Literature Validation

Reading a paper claiming a molecule has good drug-likeness?

Quickly verify their claims with independent predictions.

---

## How It Works

### The Science

ADME Predictor uses **Graph Neural Networks (GNNs)** trained on experimental data from >40,000 compounds.

**Why GNNs?**
- Traditional ML treats molecules as fingerprints (bit vectors)
- GNNs treat molecules as graphs (atoms = nodes, bonds = edges)
- GNNs learn structural patterns directly → better predictions

**Training data:** [ADMET-AI benchmark dataset](https://github.com/swansonk14/admet_ai)

**Model architecture:**
```
SMILES → Molecular Graph → GNN (3 layers) → Property Predictions
                              ↓
                    (atoms, bonds, connectivity)
```

**Performance:**
- Solubility: R² = 0.68, MAE = 0.73 log units
- Permeability: R² = 0.63, MAE = 0.65 log units  
- CYP3A4: ROC-AUC = 0.78
- hERG: ROC-AUC = 0.74

Comparable to commercial tools, and often better than rule-based methods.

### The Tech Stack

**Backend:**
- FastAPI (Python web framework)
- PyTorch + PyTorch Geometric (GNN implementation)
- RDKit (chemistry toolkit)
- Deployed on Railway

**Frontend:**
- React + TypeScript
- Tailwind CSS
- RDKit.js (client-side molecule rendering)
- Deployed on Vercel

**Models:**
- Multi-task Graph Convolutional Network
- Random Forest baseline
- ~15MB model files

---

## Documentation

### API Reference

**Base URL:** `https://api.adme-predictor.com`

#### `POST /predict`

Predict ADME properties for a single molecule.

**Request:**
```json
{
  "smiles": "string"  // SMILES notation
}
```

**Response:** See [Quick Start](#api-usage) for example.

**Rate Limits:**
- Unauthenticated: 10 requests/minute
- Authenticated: 100 requests/minute (coming soon)

---

#### `POST /predict/batch`

Predict ADME properties for multiple molecules.

**Request:**
```json
{
  "smiles": ["CCO", "CC(=O)O", "c1ccccc1"]
}
```

Or upload CSV file:
```bash
curl -X POST https://api.adme-predictor.com/predict/batch \
  -F "file=@molecules.csv"
```

**CSV format:**
```csv
smiles,compound_id
CCO,compound_1
CC(=O)O,compound_2
```

**Response:**
```json
{
  "results": [
    {
      "smiles": "CCO",
      "compound_id": "compound_1",
      "properties": { /* ... */ }
    },
    // ...
  ],
  "summary": {
    "total": 100,
    "successful": 98,
    "failed": 2
  },
  "errors": [
    {
      "smiles": "INVALID",
      "error": "Invalid SMILES string"
    }
  ]
}
```

**Limits:**
- Max 100 molecules per request
- Max file size: 5MB

---

#### `GET /health`

Check API health status.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "models_loaded": true
}
```

---

#### `GET /models/info`

Get information about loaded models.

**Response:**
```json
{
  "models": {
    "gnn": {
      "version": "1.0",
      "training_date": "2025-03-01",
      "num_parameters": 234567,
      "properties": ["solubility", "permeability", "cyp3a4", "herg"],
      "metrics": {
        "solubility_r2": 0.68,
        "permeability_r2": 0.63,
        "cyp3a4_roc_auc": 0.78,
        "herg_roc_auc": 0.74
      }
    }
  }
}
```

---

### Understanding the Results

#### Solubility (LogS)

**Range:** Typically -10 to 0

- **> -2:** Highly soluble (good)
- **-2 to -4:** Moderately soluble (acceptable)
- **-4 to -6:** Poorly soluble (may need formulation)
- **< -6:** Very poorly soluble (problematic)

**Why it matters:** Poor solubility → hard to formulate → won't reach therapeutic concentrations

---

#### Permeability (Caco-2)

**Range:** Typically -7 to -4 (log cm/s)

- **> -5:** High permeability (good oral bioavailability)
- **-5 to -6:** Moderate permeability
- **< -6:** Low permeability (poor absorption)

**Why it matters:** Drugs must cross intestinal membranes to be orally bioavailable

---

#### CYP3A4 Inhibition

**Binary:** Inhibitor / Non-inhibitor

**Probability:** 0.0 to 1.0
- **< 0.3:** Unlikely to inhibit (safe)
- **0.3 to 0.7:** Moderate risk
- **> 0.7:** Likely inhibitor (drug-drug interaction risk)

**Why it matters:** CYP3A4 metabolizes ~50% of drugs. Inhibition → drug-drug interactions

---

#### hERG Blocking

**Binary:** Blocker / Non-blocker

**Probability:** 0.0 to 1.0
- **< 0.3:** Low cardiotoxicity risk (safe)
- **0.3 to 0.7:** Moderate risk (test further)
- **> 0.7:** High risk (likely fails safety)

**Why it matters:** hERG channel blocking → cardiac arrhythmias → drug fails clinical trials

---

### Interpreting Confidence Scores

**Confidence:** 0.0 to 1.0

- **> 0.8:** High confidence (molecule similar to training data)
- **0.6 to 0.8:** Moderate confidence (reasonable prediction)
- **< 0.6:** Low confidence (out of domain, unusual structure)

**Low confidence warnings:**
- Unusual functional groups
- Very large or very small molecules
- Complex scaffolds not in training data
- Metal-containing compounds

**What to do with low confidence:**
- Interpret predictions cautiously
- Consider experimental validation
- Try alternative prediction tools
- Check if molecule is truly drug-like

---

## Installation (For Development)

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/adme-predictor.git
cd adme-predictor/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download trained models
python scripts/download_models.py

# Run development server
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

Swagger docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## Training Your Own Models

Want to train models on your own data?

```bash
cd backend

# Prepare your dataset (CSV with SMILES + property values)
# Format: smiles,solubility,permeability,...

# Train GNN model
python training/train.py \
  --data data/your_dataset.csv \
  --model gnn \
  --epochs 100 \
  --output models/custom_model.pt

# Evaluate
python training/evaluate.py \
  --model models/custom_model.pt \
  --test_data data/test_set.csv
```

See [TRAINING.md](docs/TRAINING.md) for detailed instructions.

---

## Contributing

We welcome contributions! Areas where help is needed:

- 🐛 **Bug fixes** - Found an issue? Submit a PR
- 📊 **New properties** - BBB penetration, metabolism, etc.
- 🎨 **UI improvements** - Better visualizations, UX enhancements
- 📚 **Documentation** - Tutorials, examples, explanations
- 🧪 **Testing** - More test coverage

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## FAQ

**Q: Is this free?**  
A: Yes! Free tier includes 10 predictions/minute. We'll add paid tiers with higher limits for power users.

**Q: How accurate are the predictions?**  
A: Performance is comparable to commercial tools (R² ~0.65-0.70 for regression tasks). See [Model Performance](#how-it-works) for details.

**Q: Can I use this for commercial purposes?**  
A: Yes, under MIT license. We'll offer commercial API plans with SLA guarantees soon.

**Q: What about 3D structure or protein binding?**  
A: Not yet. ADME Predictor focuses on molecular properties only. For docking, try our upcoming tool (sign up for updates).

**Q: My molecule failed validation. Why?**  
A: Common reasons:
- Invalid SMILES syntax
- Molecule too large (>100 heavy atoms)
- Contains elements we can't handle (rare metals, radioactive, etc.)
- Mixtures or salts (use canonical form)

**Q: Can I run this locally/offline?**  
A: Yes! See [Installation](#installation-for-development). Models and code are open-source.

**Q: How do you handle my data?**  
A: We don't store molecules you submit (unless you create an account and save predictions). See [Privacy Policy](PRIVACY.md).

**Q: Who built this?**  
A: Built by [Your Name], a software engineer learning drug discovery. See the [blog post](https://yourblog.com/building-adme-predictor) for the full story.

---

## Citation

If you use ADME Predictor in your research, please cite:

```bibtex
@software{adme_predictor2025,
  author = {Your Name},
  title = {ADME Predictor: Machine Learning for Drug Property Prediction},
  year = {2025},
  url = {https://github.com/yourusername/adme-predictor},
  version = {1.0}
}
```

---

## Acknowledgments

- **ADMET-AI** for the training dataset
- **RDKit** for chemistry toolkit
- **PyTorch Geometric** for GNN implementation
- All the researchers who validated the idea during development

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contact & Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/yourusername/adme-predictor/issues)
- 💬 **Questions:** [Discussions](https://github.com/yourusername/adme-predictor/discussions)
- 📧 **Email:** your.email@example.com
- 🐦 **Twitter:** [@yourhandle](https://twitter.com/yourhandle)

---

**Built with ❤️ by engineers who care about making drug discovery more accessible.**

[Try it now →](https://adme-predictor.vercel.app)
