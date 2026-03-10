# ADME Predictor - Technical Implementation Guide

## Project Overview

This is a **free, open-source** portfolio project demonstrating end-to-end ML engineering skills applied to computational chemistry. It predicts ADME (Absorption, Distribution, Metabolism, Excretion) properties of drug-like molecules and is made available in three forms:

1. **Web Tool**: A hosted web application for interactive use (no account required)
2. **Public REST API**: An open API for programmatic access by developers and researchers
3. **MCP Server**: A Model Context Protocol server so LLM assistants (Claude, Cursor, etc.) can call ADME predictions as a tool during drug discovery workflows

The goal is to demonstrate proficiency in ML model training, API design, modern frontend development, and LLM tool integration — not to compete commercially with existing ADME platforms.

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI**: REST API framework
- **PyTorch**: Deep learning framework
- **PyTorch Geometric**: Graph neural networks for molecular graphs
- **RDKit**: Chemistry toolkit for molecule manipulation
- **scikit-learn**: Classical ML baselines
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Vite**: Build tool
- **Ketcher**: Molecular structure drawing (embedded via iframe or component)
- **RDKit.js**: Client-side molecule rendering and validation

### MCP Server
- **Model Context Protocol (MCP) SDK**: Python MCP server exposing prediction tools to LLM clients
- **Stdio transport**: Local use (Claude Desktop, Cursor, etc.)
- **HTTP/SSE transport**: Remote use via hosted endpoint

### Infrastructure
- **Railway.app** or **Render.com**: Backend + MCP server hosting
- **Vercel**: Frontend hosting
- **PostgreSQL**: Optional — prediction logging for demo/showcase purposes (later phase)
- **Redis**: Rate limiting for the public API (later phase)

## Core Components

### 1. Molecular Featurization (`backend/featurization.py`)

Converts SMILES strings to graph representations for GNN models.

**Key functions:**
```python
def smiles_to_graph(smiles: str) -> Data:
    """
    Convert SMILES to PyTorch Geometric Data object.
    
    Returns:
        Data object with:
        - x: Node features (atom properties)
        - edge_index: Connectivity
        - edge_attr: Bond features
    """
    
def validate_smiles(smiles: str) -> bool:
    """Validate SMILES string using RDKit"""
    
def compute_descriptors(smiles: str) -> np.ndarray:
    """Compute molecular descriptors for classical ML"""
```

**Atom features (per node):**
- Atomic number (one-hot or embedding)
- Degree
- Formal charge
- Hybridization (sp, sp2, sp3)
- Is aromatic
- Number of hydrogens
- Is in ring

**Bond features (per edge):**
- Bond type (single, double, triple, aromatic)
- Is conjugated
- Is in ring

### 2. ML Models (`backend/models/`)

#### Random Forest Baseline (`rf_model.py`)
- Uses molecular descriptors (RDKit)
- Fast inference
- Good interpretability
- Use as fallback if GNN fails

#### Graph Neural Network (`gnn_model.py`)
```python
class ADMEPredictor(nn.Module):
    """
    Multi-task GNN for ADME property prediction.
    
    Architecture:
    - 3-4 GCN/GAT layers for message passing
    - Global pooling (mean/max)
    - MLP heads for each property
    """
    def __init__(self, num_node_features, num_properties):
        self.conv1 = GCNConv(num_node_features, 128)
        self.conv2 = GCNConv(128, 128)
        self.conv3 = GCNConv(128, 64)
        # Property-specific heads
        self.heads = nn.ModuleDict({
            'solubility': MLP([64, 32, 1]),
            'permeability': MLP([64, 32, 1]),
            'cyp3a4': MLP([64, 32, 1]),  # Binary classification
            'herg': MLP([64, 32, 1]),     # Binary classification
        })
```

**Properties to predict:**

1. **Solubility (LogS)**: Regression, range typically -10 to 0
2. **Permeability (Caco-2)**: Regression, log scale
3. **CYP3A4 inhibition**: Binary classification (inhibitor/non-inhibitor)
4. **hERG blocking**: Binary classification (cardiotoxicity risk)
5. **Lipophilicity (LogP)**: Regression (optional, easy to add)

### 3. Training Pipeline (`backend/train.py`)

```python
def train_model(
    dataset_path: str,
    property_name: str,
    model_type: str = 'gnn',
    epochs: int = 100,
    batch_size: int = 32
):
    """
    Train model on ADME dataset.
    
    Steps:
    1. Load data (SMILES + property values)
    2. Split train/val/test (80/10/10)
    3. Featurize molecules
    4. Train with early stopping
    5. Evaluate on test set
    6. Save model checkpoint
    """
```

**Data augmentation techniques:**
- SMILES enumeration (different valid SMILES for same molecule)
- Molecular scaffolds for splitting (avoid data leakage)

### 4. API Endpoints (`backend/api/routes.py`)

```python
@app.post("/predict")
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Predict ADME properties for a molecule.
    
    Input: {"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}  # Aspirin
    Output: {
        "smiles": "...",
        "properties": {
            "solubility": {"value": -2.3, "unit": "log mol/L", "confidence": 0.85},
            "permeability": {"value": -5.1, "unit": "log cm/s", "confidence": 0.78},
            "cyp3a4_inhibitor": {"probability": 0.12, "prediction": false},
            "herg_blocker": {"probability": 0.05, "prediction": false}
        },
        "warnings": ["Molecule contains unusual functional group"],
        "molecular_weight": 180.16,
        "rule_of_five": {"passes": true, "violations": []}
    }
    """

@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest):
    """Batch prediction for multiple SMILES (up to 100)"""

@app.get("/health")
async def health_check():
    """Service health check"""

@app.get("/models/info")
async def model_info():
    """Return information about loaded models (version, training date, metrics)"""
```

### 5. MCP Server (`mcp_server/`)

Exposes the ADME predictor as a set of tools consumable by any MCP-compatible LLM client (Claude Desktop, Cursor, Continue, etc.).

**Project structure:**
```
mcp_server/
├── server.py           # MCP server entry point
├── tools.py            # Tool definitions
├── client.py           # Internal HTTP client calling the FastAPI backend
└── README.md           # Setup instructions for LLM clients
```

**Exposed MCP tools:**

```python
@mcp.tool()
async def predict_adme(smiles: str) -> dict:
    """
    Predict ADME properties for a molecule given its SMILES string.
    Returns solubility, permeability, CYP3A4 inhibition, and hERG blocking predictions.

    Args:
        smiles: SMILES string of the molecule (e.g. "CC(=O)OC1=CC=CC=C1C(=O)O" for aspirin)
    """

@mcp.tool()
async def predict_adme_batch(smiles_list: list[str]) -> list[dict]:
    """
    Predict ADME properties for multiple molecules at once (up to 100).

    Args:
        smiles_list: List of SMILES strings
    """

@mcp.tool()
async def validate_smiles(smiles: str) -> dict:
    """
    Validate a SMILES string and return basic molecular properties.
    Useful for checking a structure before running predictions.

    Args:
        smiles: SMILES string to validate
    """
```

**Transport modes:**
- **Stdio (local)**: Run as a subprocess for Claude Desktop / Cursor. User points their MCP config at the local binary.
- **HTTP/SSE (remote)**: Hosted endpoint at `https://api.admetool.dev/mcp` for remote clients.

**Claude Desktop config example:**
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

**Published as a PyPI package** (`adme-predictor-mcp`) so it's installable with `uvx` or `pip install`.

### 6. Frontend Components

**Overall repo structure:**
```
adme-predictor/
├── backend/            # FastAPI prediction service
├── frontend/           # React web tool
├── mcp_server/         # MCP server (PyPI package)
└── notebooks/          # Training experiments (published for transparency)
```

**Frontend app structure:**
```
frontend/src/
├── components/
│   ├── MoleculeInput.tsx       # SMILES input or drawing
│   ├── MoleculeViewer.tsx      # 2D structure display
│   ├── PredictionResults.tsx   # Display predictions
│   ├── PropertyCard.tsx        # Individual property display
│   ├── ExampleMolecules.tsx    # Pre-loaded examples
│   └── BatchUpload.tsx         # CSV upload for batch
├── services/
│   ├── api.ts                  # API client
│   └── validation.ts           # Client-side SMILES validation
├── hooks/
│   ├── usePrediction.ts        # Prediction state management
│   └── useMolecule.ts          # Molecule state
└── utils/
    ├── chemistry.ts            # Chemistry helper functions
    └── formatting.ts           # Display formatting
```

**Key UX features:**
- Real-time SMILES validation
- Molecule preview as user types
- Example molecules (aspirin, caffeine, ibuprofen, etc.)
- Clear error messages
- Loading states with estimated time
- Results visualization (gauges, color-coding)
- Export results as JSON/CSV

## Data Sources

### Training Data

**Primary dataset: ADMET-AI**
- URL: https://github.com/swansonk14/admet_ai
- ~40,000 compounds with ADME measurements
- Pre-split train/val/test sets
- Well-curated, validated data

**Alternative/Supplementary:**
- **ChEMBL**: Large bioactivity database (filter for ADME assays)
- **PubChem**: BioAssay data
- **ToxCast**: Toxicity predictions
- **ClinTox**: Clinical trial toxicity

**Data format:**
```csv
smiles,solubility,permeability,cyp3a4_inhibitor,herg_blocker
CC(=O)OC1=CC=CC=C1C(=O)O,-2.3,-5.1,0,0
CCO,-0.77,-4.5,0,0
...
```

### Molecular Descriptors (if using RF)
- Molecular weight
- LogP (lipophilicity)
- Number of H-bond donors/acceptors
- Topological polar surface area (TPSA)
- Number of rotatable bonds
- Aromatic rings count
- ~200 RDKit descriptors total

## Development Phases

### Phase 1: MVP (Weeks 1-4)

**Week 1: Data + Training**
- Download ADMET-AI dataset
- Implement featurization pipeline
- Train baseline Random Forest
- Train simple GNN (2-layer GCN)
- Validate on test set

**Week 2: API**
- Set up FastAPI project structure
- Implement `/predict` endpoint
- Add SMILES validation
- Model loading and inference
- Error handling

**Week 3: Frontend**
- Create React app with Vite
- SMILES input component
- Molecule viewer (RDKit.js)
- Results display
- Connect to API

**Week 4: Deploy**
- Dockerize backend
- Deploy to Railway/Render
- Deploy frontend to Vercel
- End-to-end testing
- Soft launch

### Phase 2: Improvements (Weeks 5-8)
- Better GNN architecture (GAT, message passing)
- Uncertainty estimation (ensemble or MC dropout)
- Batch predictions
- Molecule drawing interface (Ketcher)
- Example molecules library
- Performance optimization

### Phase 3: MCP Server + Polish (Weeks 9-12)
- Implement MCP server with stdio transport
- Publish `adme-predictor-mcp` to PyPI
- Add HTTP/SSE transport for hosted MCP endpoint
- Write setup guides for Claude Desktop, Cursor, Continue
- Add attention visualization (which atoms drive predictions)
- Finalize public API documentation (OpenAPI/Swagger)
- GitHub README polish, demo GIF, example notebooks

## Model Performance Targets

**For MVP to be viable:**
- Solubility: R² > 0.65, MAE < 0.8 log units
- Permeability: R² > 0.60, MAE < 0.7 log units
- CYP3A4: ROC-AUC > 0.75
- hERG: ROC-AUC > 0.70

**Comparison:**
- SwissADME: No published metrics, rule-based
- ADMETlab 2.0: R² ~0.60-0.70 for various properties
- Commercial tools (ADMET Predictor): R² ~0.70-0.80

**Note:** Performance targets are portfolio minimums. The goal is demonstrating end-to-end ML engineering competence, not state-of-the-art accuracy.

## Key Technical Decisions & Rationale

### Why GNN over traditional ML?
- **Better performance**: Learns molecular structure directly
- **Transfer learning**: Can fine-tune on small datasets
- **Modern approach**: Shows technical sophistication in graph ML
- **Portfolio value**: Demonstrates knowledge beyond tabular/regression ML

### Why multi-task learning?
- **Shared representations**: Properties are correlated
- **Better generalization**: Regularization effect
- **Efficiency**: One model vs. four models
- **Easier deployment**: Single model to serve

### Why FastAPI over Flask?
- **Async support**: Better performance under load
- **Auto documentation**: Swagger UI out of the box — important for a public API
- **Type hints**: Pydantic validation
- **Modern**: Industry standard for ML APIs

### Why not use pre-trained models?
- **Portfolio purpose**: Training from scratch demonstrates the full ML pipeline
- **Transparency**: Full control and understanding of every component
- **Documented process**: Training notebooks are published as part of the project

### Why an MCP server?
- **Differentiation**: Most ADME tools have no LLM integration — this is a genuine gap
- **Modern relevance**: MCP is becoming a standard interface for LLM tool use
- **Demonstrates breadth**: Shows ability to integrate ML systems into emerging AI workflows
- **Practical value**: Researchers using AI assistants can call ADME predictions mid-conversation

## Testing Strategy

### Unit Tests
```python
# test_featurization.py
def test_smiles_to_graph():
    """Test SMILES conversion to graph"""
    
def test_invalid_smiles():
    """Test handling of invalid SMILES"""

# test_models.py
def test_model_inference():
    """Test model forward pass"""
    
def test_prediction_range():
    """Test predictions are in valid ranges"""
```

### Integration Tests
```python
# test_api.py
def test_predict_endpoint():
    """Test end-to-end prediction"""
    
def test_batch_prediction():
    """Test batch processing"""
    
def test_error_handling():
    """Test API error responses"""
```

### Performance Tests
- Inference latency: <200ms for single molecule
- Batch throughput: >100 molecules/second
- Memory usage: <2GB for model + server

## Monitoring & Observability

**Metrics to track:**
- Request count (by endpoint)
- Latency (p50, p95, p99)
- Error rate
- Model predictions distribution (detect drift)
- Popular molecules (cache candidates)

**Tools:**
- Logging: Python `logging` module
- Metrics: Prometheus (later)
- Errors: Sentry (later)
- Analytics: PostHog or Plausible

## Security Considerations

**MVP:**
- Rate limiting (10 requests/minute for unauthenticated)
- Input validation (SMILES length < 500 chars)
- CORS configuration
- HTTPS only

**Public API (no auth, so abuse prevention matters):**
- IP-based rate limiting (no API keys needed — keep it frictionless)
- Input validation (SMILES length < 500 chars, batch size < 100)
- DDoS protection via Cloudflare (free tier)
- No user data stored — stateless by design

## Deployment Configuration

### Backend (Railway.app)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for RDKit
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download trained models
RUN python download_models.py

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Vercel)
- Automatic deployment on git push
- Environment variables for API URL
- Edge caching for static assets

## Cost Estimates

This is a free project — cost minimization matters.

**Development (one-time):**
- GPU training: $50-100 (Google Colab Pro or Lambda Labs)
- Domain: $12/year
- Total: ~$100

**Monthly operating costs:**
- Railway backend: $5-20/month (scale to zero when idle if possible)
- Vercel frontend: $0 (free tier sufficient)
- Total: $5-20/month

The public API has no auth or paid tiers. Rate limiting (IP-based) is sufficient to prevent abuse without requiring accounts.

## Future Enhancements

**Technical:**
- Conformal prediction for uncertainty
- Attention visualization (which atoms matter)
- 3D conformer generation
- Retrosynthesis integration
- Protein-ligand docking

**Features:**
- Batch CSV upload
- Attention/saliency visualization (highlight atoms driving each prediction)
- Molecule library management
- Additional MCP tools (scaffold analysis, Lipinski violations, etc.)
- Cursor / Continue / other IDE MCP client setup guides

**Properties:**
- Blood-brain barrier penetration
- Plasma protein binding
- Half-life prediction
- More CYP isoforms
- Toxicity endpoints

## Resources & References

**Code Examples:**
- DeepChem tutorials: https://github.com/deepchem/deepchem
- PyTorch Geometric examples: https://github.com/pyg-team/pytorch_geometric
- Chemprop: https://github.com/chemprop/chemprop (reference implementation)

**Papers:**
- "Analyzing Learned Molecular Representations for Property Prediction" (Chemprop paper)
- "Pushing the Boundaries of Molecular Representation for Drug Discovery"
- "ADMET-AI: A machine learning ADMET platform"

**Datasets:**
- ADMET-AI: https://github.com/swansonk14/admet_ai
- MoleculeNet: http://moleculenet.ai/
- Therapeutic Data Commons: https://tdcommons.ai/

## Common Pitfalls to Avoid

1. **Data leakage**: Use scaffold splitting, not random splitting
2. **Overfitting**: Small datasets overfit easily, use regularization
3. **Invalid SMILES**: Always validate before processing
4. **Inference speed**: Profile and optimize bottlenecks
5. **Model versioning**: Track which model version made predictions
6. **Hard-coding**: Make thresholds configurable
7. **Poor error messages**: Users need to understand what went wrong
8. **Ignoring edge cases**: Test with drug-like AND non-drug-like molecules

## Success Metrics

**Technical:**
- ✅ Model performance meets targets
- ✅ API latency <200ms
- ✅ MCP server installable and functional in Claude Desktop
- ✅ Public API documented and accessible without auth

**Portfolio:**
- ✅ GitHub repo demonstrates full ML pipeline (data → training → serving)
- ✅ Training notebooks are readable and published
- ✅ GitHub repo gets >50 stars (signals community value)
- ✅ MCP package published to PyPI and installable via `uvx`

**Visibility:**
- ✅ Blog post / write-up about building this (especially the MCP angle)
- ✅ Listed on mcp.so or similar MCP server directories
- ✅ Referenced by at least one "awesome-mcp" style list

## Getting Help

**When stuck:**
1. Check RDKit documentation: https://www.rdkit.org/docs/
2. PyTorch Geometric docs: https://pytorch-geometric.readthedocs.io/
3. Ask on r/cheminformatics (friendly community)
4. RDKit mailing list
5. DeepChem Gitter chat

**Code review:**
- Post on relevant subreddits
- Ask in PyTorch forums
- Find mentors on Twitter/LinkedIn

This document should give you everything needed to build the ADME predictor from scratch. Update it as you learn and make decisions.

The three deliverables — web tool, public API, and MCP server — are the core of the portfolio story. All three should be live and linked from the GitHub README.
