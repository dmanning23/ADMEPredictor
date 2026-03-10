# ADME Predictor - Architecture & Implementation Plan

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Molecule     │  │  Results     │  │  History     │     │
│  │ Input/Draw   │  │  Display     │  │  (future)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                         │
│                     React + TypeScript                       │
│  - Input validation                                          │
│  - Molecule rendering (RDKit.js)                             │
│  - Results visualization                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend API (Railway/Render)                 │
│                      FastAPI + Python                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐       │
│  │   Routes    │→ │ Validation   │→ │ Prediction  │       │
│  │  /predict   │  │  (RDKit)     │  │  Service    │       │
│  │  /batch     │  │              │  │             │       │
│  └─────────────┘  └──────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      ML Pipeline                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐       │
│  │Featurize    │→ │   GNN Model  │→ │   Output    │       │
│  │SMILES→Graph │  │  (PyTorch)   │  │  Transform  │       │
│  └─────────────┘  └──────────────┘  └─────────────┘       │
│                                                              │
│  Models stored in: /models/                                  │
│  - adme_gnn_v1.pt (GNN multi-task)                          │
│  - adme_rf_v1.pkl (Random Forest baseline)                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Single Prediction Flow
```
1. User enters SMILES or draws molecule
   │
   ▼
2. Frontend validates (basic syntax check via RDKit.js)
   │
   ▼
3. POST /predict with SMILES string
   │
   ▼
4. Backend validates (RDKit server-side)
   │
   ▼
5. Convert SMILES → molecular graph
   │
   ▼
6. Run inference on GNN model
   │
   ▼
7. Post-process predictions (scale, format)
   │
   ▼
8. Return JSON response
   │
   ▼
9. Frontend displays results with visualizations
```

### Batch Prediction Flow
```
1. User uploads CSV with SMILES column
   │
   ▼
2. Frontend parses and validates (max 100 molecules for MVP)
   │
   ▼
3. POST /predict/batch with array of SMILES
   │
   ▼
4. Backend processes in batches of 32
   │
   ▼
5. Return aggregated results
   │
   ▼
6. Frontend shows table + download CSV
```

## Directory Structure

```
adme-predictor/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Configuration (model paths, thresholds)
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Container definition
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # API endpoints
│   │   ├── schemas.py               # Pydantic models (request/response)
│   │   └── middleware.py            # Rate limiting, CORS, logging
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── gnn_model.py             # GNN architecture definition
│   │   ├── rf_model.py              # Random Forest wrapper
│   │   └── ensemble.py              # Model ensemble (future)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── prediction.py            # Prediction orchestration
│   │   ├── featurization.py         # SMILES → graph conversion
│   │   └── validation.py            # SMILES validation, drug-likeness
│   │
│   ├── training/
│   │   ├── train.py                 # Training script
│   │   ├── dataset.py               # Dataset loading and preprocessing
│   │   ├── evaluate.py              # Model evaluation
│   │   └── utils.py                 # Training utilities
│   │
│   ├── data/
│   │   ├── raw/                     # Raw downloaded datasets
│   │   ├── processed/               # Featurized datasets
│   │   └── splits/                  # Train/val/test splits
│   │
│   ├── saved_models/
│   │   ├── gnn_v1/
│   │   │   ├── model.pt
│   │   │   ├── config.json
│   │   │   └── metrics.json
│   │   └── rf_v1/
│   │       └── model.pkl
│   │
│   └── tests/
│       ├── test_api.py
│       ├── test_featurization.py
│       ├── test_models.py
│       └── test_validation.py
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   │
│   ├── src/
│   │   ├── main.tsx                 # App entry point
│   │   ├── App.tsx                  # Root component
│   │   │
│   │   ├── components/
│   │   │   ├── MoleculeInput.tsx    # SMILES input + drawing
│   │   │   ├── MoleculeViewer.tsx   # 2D structure display
│   │   │   ├── PredictionResults.tsx # Results display
│   │   │   ├── PropertyCard.tsx     # Individual property card
│   │   │   ├── ExampleMolecules.tsx # Example library
│   │   │   ├── BatchUpload.tsx      # CSV batch upload
│   │   │   └── LoadingState.tsx     # Loading indicator
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts               # API client (fetch wrapper)
│   │   │   └── chemistry.ts         # Client-side chem utils
│   │   │
│   │   ├── hooks/
│   │   │   ├── usePrediction.ts     # Prediction state logic
│   │   │   └── useMolecule.ts       # Molecule state
│   │   │
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript interfaces
│   │   │
│   │   └── utils/
│   │       ├── validation.ts        # Input validation
│   │       └── formatting.ts        # Display formatting
│   │
│   └── public/
│       └── examples/                # Example molecule files
│
├── docs/
│   ├── README.md                    # Project overview
│   ├── architecture.md              # This file
│   ├── claude.md                    # Claude Code reference
│   ├── biology-concepts.md          # Biology/chemistry background
│   └── walkthrough.md               # Usage scenario
│
├── scripts/
│   ├── download_data.py             # Download training data
│   ├── prepare_dataset.py           # Data preprocessing
│   └── benchmark.py                 # Performance benchmarking
│
└── docker-compose.yml               # Local development setup
```

## Step-by-Step Implementation Plan

### Week 1: Data & Model Training

#### Day 1-2: Environment Setup & Data Acquisition
**Tasks:**
- [ ] Set up Python environment (venv or conda)
- [ ] Install dependencies: PyTorch, PyG, RDKit, scikit-learn
- [ ] Download ADMET-AI dataset from GitHub
- [ ] Explore dataset (EDA notebook)
- [ ] Verify data quality and distributions

**Scripts to create:**
```bash
scripts/download_data.py
```

**Outputs:**
- `backend/data/raw/admet_ai.csv`
- `notebooks/01_data_exploration.ipynb`

**Decision points:**
- ❓ Which ADME properties to include? (Start with 4: solubility, permeability, CYP3A4, hERG)
- ❓ Minimum dataset size per property? (At least 1000 samples, preferably 5000+)

---

#### Day 3-4: Featurization Pipeline
**Tasks:**
- [ ] Implement `smiles_to_graph()` function
- [ ] Define atom and bond features
- [ ] Test on example molecules
- [ ] Handle edge cases (salts, mixtures, invalid SMILES)
- [ ] Create molecular descriptor computation for RF baseline

**Files to create:**
```python
backend/services/featurization.py
backend/tests/test_featurization.py
```

**Test molecules:**
- Aspirin: `CC(=O)OC1=CC=CC=C1C(=O)O`
- Caffeine: `CN1C=NC2=C1C(=O)N(C(=O)N2C)C`
- Invalid: `INVALID_SMILES_123`

**Decision points:**
- ❓ One-hot encoding vs learned embeddings for atom types?
  - **Recommendation:** One-hot for MVP (simpler, interpretable)
- ❓ Include 3D coordinates? 
  - **Recommendation:** No for MVP (2D graph is sufficient, faster)

---

#### Day 5-6: Model Training - Baseline
**Tasks:**
- [ ] Implement dataset loading
- [ ] Create train/val/test splits (scaffold-based)
- [ ] Train Random Forest models (one per property)
- [ ] Evaluate on test set
- [ ] Save models

**Files to create:**
```python
backend/training/dataset.py
backend/training/train.py
backend/training/evaluate.py
```

**Expected performance (baseline):**
- Solubility: R² ≈ 0.50-0.60
- Permeability: R² ≈ 0.45-0.55
- CYP3A4: ROC-AUC ≈ 0.70-0.75
- hERG: ROC-AUC ≈ 0.65-0.70

**Decision points:**
- ❓ Train separate models or multi-output?
  - **Recommendation:** Separate for RF (simpler), multi-task for GNN
- ❓ Handle missing values?
  - **Recommendation:** Skip molecules with missing target values for now

---

#### Day 6-7: Model Training - GNN
**Tasks:**
- [ ] Implement GNN architecture (start with GCNConv)
- [ ] Multi-task learning setup
- [ ] Training loop with early stopping
- [ ] Hyperparameter tuning (learning rate, layers, hidden dim)
- [ ] Compare to baseline

**Files to create:**
```python
backend/models/gnn_model.py
```

**Architecture decisions:**
- Number of layers: 3-4 (more = overfitting risk)
- Hidden dimensions: 128 → 128 → 64
- Pooling: Global mean pooling
- Dropout: 0.1-0.2

**Expected performance (GNN):**
- Solubility: R² ≈ 0.60-0.70
- Permeability: R² ≈ 0.55-0.65
- CYP3A4: ROC-AUC ≈ 0.75-0.80
- hERG: ROC-AUC ≈ 0.70-0.75

**Decision points:**
- ❓ GCN vs GAT vs other message passing?
  - **Recommendation:** Start with GCN (simplest), try GAT if time permits
- ❓ How to handle class imbalance (for binary tasks)?
  - **Recommendation:** Weighted loss or oversampling minority class

**⚠️ BLIND SPOTS:**
- GPU availability for training (may need Google Colab or cloud GPU)
- Training time estimate: 2-4 hours on single GPU for full dataset
- Model file size: ~10-50MB (should be fine for deployment)

---

### Week 2: Backend API Development

#### Day 1-2: FastAPI Setup & Basic Routes
**Tasks:**
- [ ] Initialize FastAPI project
- [ ] Create Pydantic schemas for requests/responses
- [ ] Implement `/health` endpoint
- [ ] Implement `/models/info` endpoint
- [ ] Set up logging

**Files to create:**
```python
backend/main.py
backend/api/routes.py
backend/api/schemas.py
backend/config.py
```

**API schema example:**
```python
class PredictionRequest(BaseModel):
    smiles: str
    
class PropertyPrediction(BaseModel):
    value: float
    unit: str
    confidence: Optional[float]
    
class PredictionResponse(BaseModel):
    smiles: str
    canonical_smiles: str  # RDKit canonical form
    properties: Dict[str, PropertyPrediction]
    molecular_weight: float
    warnings: List[str]
```

**Decision points:**
- ❓ Sync vs async endpoints?
  - **Recommendation:** Async for future scalability, but sync is fine for MVP
- ❓ Include confidence intervals?
  - **Recommendation:** Yes, even if simple (model variance or fixed values)

---

#### Day 3-4: Prediction Service
**Tasks:**
- [ ] Implement model loading (lazy loading vs eager)
- [ ] Create prediction service
- [ ] Implement `/predict` endpoint
- [ ] Add SMILES validation
- [ ] Error handling for invalid inputs

**Files to create:**
```python
backend/services/prediction.py
backend/services/validation.py
```

**Prediction flow:**
```python
async def predict(smiles: str):
    # 1. Validate SMILES
    if not validate_smiles(smiles):
        raise InvalidSMILESError
    
    # 2. Canonicalize
    canonical = canonicalize_smiles(smiles)
    
    # 3. Featurize
    graph = smiles_to_graph(canonical)
    
    # 4. Inference
    predictions = model(graph)
    
    # 5. Post-process
    results = format_predictions(predictions)
    
    return results
```

**Decision points:**
- ❓ Model loading strategy?
  - **Recommendation:** Load on startup (faster inference, uses more memory)
  - Alternative: Load on first request (slower first request, saves memory)
- ❓ Batch processing internally?
  - **Recommendation:** No for single predictions, yes for batch endpoint

**⚠️ BLIND SPOTS:**
- Memory usage with model loaded (estimate: 500MB-1GB)
- Cold start time if using serverless (may need to keep instance warm)

---

#### Day 5: Batch Prediction Endpoint
**Tasks:**
- [ ] Implement `/predict/batch` endpoint
- [ ] Handle CSV parsing
- [ ] Process in batches of 32
- [ ] Return results with error handling per molecule

**File updates:**
```python
backend/api/routes.py  # Add batch endpoint
```

**Design:**
```python
@app.post("/predict/batch")
async def predict_batch(file: UploadFile):
    # Parse CSV
    smiles_list = parse_csv(file)
    
    # Validate all
    valid_smiles, errors = validate_batch(smiles_list)
    
    # Predict in batches
    results = []
    for batch in chunks(valid_smiles, batch_size=32):
        batch_predictions = model.predict_batch(batch)
        results.extend(batch_predictions)
    
    return {"results": results, "errors": errors}
```

**Decision points:**
- ❓ Maximum batch size?
  - **Recommendation:** 100 for MVP (prevent abuse, keep response time reasonable)
- ❓ Async processing for large batches?
  - **Recommendation:** No for MVP, but add task queue (Celery) in future

---

#### Day 6-7: Testing & Middleware
**Tasks:**
- [ ] Write unit tests for all endpoints
- [ ] Add CORS middleware
- [ ] Implement rate limiting (10 requests/min for unauthenticated)
- [ ] Add request logging
- [ ] Integration tests

**Files to create:**
```python
backend/api/middleware.py
backend/tests/test_api.py
```

**Rate limiting strategy:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, body: PredictionRequest):
    ...
```

**Decision points:**
- ❓ Rate limit strategy?
  - **Recommendation:** IP-based for MVP, API key-based later
- ❓ Caching predictions?
  - **Recommendation:** Not for MVP (adds complexity), add Redis later

**⚠️ TODO:**
- [ ] Decide on error code standards (400 vs 422 for validation)
- [ ] Define monitoring strategy (what to log)
- [ ] Plan for model versioning (how to handle model updates)

---

### Week 3: Frontend Development

#### Day 1-2: React Setup & Basic Components
**Tasks:**
- [ ] Initialize Vite + React + TypeScript project
- [ ] Set up Tailwind CSS
- [ ] Create basic layout
- [ ] Implement MoleculeInput component
- [ ] Add example molecules dropdown

**Files to create:**
```typescript
frontend/src/main.tsx
frontend/src/App.tsx
frontend/src/components/MoleculeInput.tsx
frontend/src/components/ExampleMolecules.tsx
```

**UI mockup (text representation):**
```
┌─────────────────────────────────────────────────┐
│  ADME Predictor                        [About]  │
├─────────────────────────────────────────────────┤
│                                                  │
│  Enter molecule (SMILES):                       │
│  ┌────────────────────────────────────────────┐│
│  │ CC(=O)OC1=CC=CC=C1C(=O)O              [×]  ││
│  └────────────────────────────────────────────┘│
│  [Examples ▼] [Draw Molecule] [Predict]        │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │     [2D Molecule Structure Preview]      │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Decision points:**
- ❓ Molecule drawer library?
  - **Options:** Ketcher (full-featured, heavy), ChemDoodle (commercial), custom with RDKit.js
  - **Recommendation:** Start with SMILES input only, add Ketcher later if needed
- ❓ Real-time SMILES validation?
  - **Recommendation:** Yes, using RDKit.js client-side

---

#### Day 3-4: API Integration & Results Display
**Tasks:**
- [ ] Create API client service
- [ ] Implement usePrediction hook
- [ ] Create PredictionResults component
- [ ] Create PropertyCard component
- [ ] Add loading states

**Files to create:**
```typescript
frontend/src/services/api.ts
frontend/src/hooks/usePrediction.ts
frontend/src/components/PredictionResults.tsx
frontend/src/components/PropertyCard.tsx
```

**API client:**
```typescript
export async function predictADME(smiles: string): Promise<PredictionResponse> {
  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ smiles })
  });
  
  if (!response.ok) {
    throw new Error(await response.text());
  }
  
  return response.json();
}
```

**Results display design:**
```
┌─────────────────────────────────────────────────┐
│  Results for Aspirin                            │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐            │
│  │ Solubility   │  │ Permeability │            │
│  │ -2.3 log M   │  │ -5.1 log cm/s│            │
│  │ [████░░░░░░] │  │ [███░░░░░░░] │            │
│  │ Good         │  │ Moderate     │            │
│  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ CYP3A4       │  │ hERG         │            │
│  │ Non-inhibitor│  │ Non-blocker  │            │
│  │ 12% risk     │  │ 5% risk      │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│  [Export JSON] [Export CSV] [New Prediction]   │
└─────────────────────────────────────────────────┘
```

**Decision points:**
- ❓ Visualization library?
  - **Recommendation:** CSS for MVP (simpler), add Chart.js if needed
- ❓ Color coding for properties?
  - **Recommendation:** Yes (green/yellow/red for ranges)

---

#### Day 5: Molecule Visualization
**Tasks:**
- [ ] Integrate RDKit.js for molecule rendering
- [ ] Create MoleculeViewer component
- [ ] Show 2D structure preview
- [ ] Highlight problematic substructures (if validation fails)

**Files to create:**
```typescript
frontend/src/components/MoleculeViewer.tsx
```

**RDKit.js integration:**
```typescript
import initRDKitModule from '@rdkit/rdkit';

const RDKit = await initRDKitModule();

function MoleculeViewer({ smiles }: { smiles: string }) {
  const svgRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const mol = RDKit.get_mol(smiles);
    const svg = mol.get_svg();
    if (svgRef.current) {
      svgRef.current.innerHTML = svg;
    }
  }, [smiles]);
  
  return <div ref={svgRef} />;
}
```

**Decision points:**
- ❓ Client-side vs server-side rendering?
  - **Recommendation:** Client-side with RDKit.js (reduces backend load)

**⚠️ BLIND SPOT:**
- RDKit.js is ~8MB (large bundle size)
- May need code splitting or lazy loading

---

#### Day 6-7: Polish & Error Handling
**Tasks:**
- [ ] Add comprehensive error messages
- [ ] Implement proper loading states
- [ ] Add input validation feedback
- [ ] Mobile responsive design
- [ ] Accessibility (keyboard navigation, ARIA labels)
- [ ] Add "About" page with documentation

**Decision points:**
- ❓ Show model version/confidence?
  - **Recommendation:** Yes, builds trust
- ❓ User feedback mechanism?
  - **Recommendation:** Simple "Was this helpful?" buttons for MVP

**⚠️ TODO:**
- [ ] Decide on error message tone (technical vs friendly)
- [ ] Plan analytics (what user actions to track)

---

### Week 4: Deployment & Launch

#### Day 1-2: Backend Deployment
**Tasks:**
- [ ] Create Dockerfile for backend
- [ ] Test Docker build locally
- [ ] Deploy to Railway.app or Render.com
- [ ] Set up environment variables
- [ ] Configure custom domain (optional)
- [ ] Test deployed API with Postman

**Dockerfile optimization:**
```dockerfile
# Multi-stage build to reduce image size
FROM python:3.10-slim as builder
# ... install dependencies

FROM python:3.10-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
# ... copy app
```

**Decision points:**
- ❓ Railway vs Render vs Fly.io?
  - **Railway:** Easiest, good free tier, auto-scaling
  - **Render:** Similar to Railway, good docs
  - **Fly.io:** More control, global CDN
  - **Recommendation:** Railway for MVP

**⚠️ BLIND SPOTS:**
- Docker image size (estimate: 1-2GB with PyTorch + RDKit)
- May need to optimize dependencies
- Cold start time on free tier (30-60 seconds)

---

#### Day 3: Frontend Deployment
**Tasks:**
- [ ] Build production bundle
- [ ] Deploy to Vercel
- [ ] Configure environment variables (API URL)
- [ ] Set up custom domain
- [ ] Test production build

**Vercel config:**
```json
{
  "build": {
    "env": {
      "VITE_API_URL": "https://adme-api.railway.app"
    }
  }
}
```

---

#### Day 4-5: End-to-End Testing
**Tasks:**
- [ ] Test complete user flows
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile testing
- [ ] Performance testing (Lighthouse)
- [ ] Load testing (Apache Bench or k6)
- [ ] Fix bugs

**Test scenarios:**
- ✅ Valid SMILES → successful prediction
- ✅ Invalid SMILES → clear error message
- ✅ Very large molecule → handles gracefully
- ✅ Batch upload → processes correctly
- ✅ Rate limiting → blocks after threshold

---

#### Day 6-7: Launch Preparation & Soft Launch
**Tasks:**
- [ ] Write launch blog post
- [ ] Create demo video (3-5 minutes)
- [ ] Prepare social media posts
- [ ] Set up analytics (Plausible or Google Analytics)
- [ ] Soft launch to small group (email 20-30 researchers from validation)
- [ ] Collect initial feedback
- [ ] Fix critical issues

**Launch checklist:**
- [ ] API is live and responding
- [ ] Frontend loads properly
- [ ] No console errors
- [ ] Mobile works
- [ ] Example molecules work
- [ ] Error handling works
- [ ] Analytics tracking works
- [ ] Landing page has clear value prop

**Soft launch platforms:**
- r/cheminformatics
- r/datascience (if framed well)
- Personal blog/Twitter
- Direct emails to researchers

**Success metrics for soft launch:**
- Target: 50-100 users in first week
- Positive feedback from >80%
- <5% error rate
- Average session >2 minutes

---

## Architecture Decision Records (ADRs)

### ADR-001: Multi-task Learning for GNN
**Status:** Accepted

**Context:** We need to predict multiple ADME properties. Options:
1. Train separate model per property
2. Multi-task learning (single model, multiple outputs)

**Decision:** Multi-task learning

**Rationale:**
- Properties are correlated (shared molecular features)
- Better regularization (prevents overfitting)
- Faster inference (one forward pass)
- Easier deployment (one model file)

**Consequences:**
- Need to handle missing labels during training
- All properties must use same featurization
- Model size is slightly larger

---

### ADR-002: Client-side Molecule Rendering
**Status:** Accepted

**Context:** Need to show 2D molecular structures. Options:
1. Server-side rendering (generate SVG on backend)
2. Client-side rendering (RDKit.js)

**Decision:** Client-side with RDKit.js

**Rationale:**
- Reduces backend load
- Faster for user (no API call needed)
- Can validate SMILES client-side before API call

**Consequences:**
- Larger JavaScript bundle (~8MB)
- Need to handle RDKit.js initialization
- Browser compatibility concerns (use WebAssembly)

---

### ADR-003: Free Tier Rate Limiting
**Status:** Accepted

**Context:** Need to prevent abuse while allowing legitimate use

**Decision:** 10 predictions per minute per IP (unauthenticated)

**Rationale:**
- Allows normal usage (try 5-10 molecules)
- Prevents bulk scraping
- Simple to implement
- Can be increased with API key

**Consequences:**
- May frustrate power users
- Need clear messaging about limits
- Plan for API key system later

---

## Blind Spots & Unknowns

### Technical Unknowns
- ❓ **Model performance on real-world molecules**: Trained on clean data, but users may input unusual structures
  - **Mitigation:** Test with diverse molecules, add warning for out-of-distribution detection
  
- ❓ **Inference latency under load**: Untested with concurrent requests
  - **Mitigation:** Load test before launch, add request queuing if needed

- ❓ **Model file size in production**: May be larger than expected
  - **Mitigation:** Benchmark, consider model quantization or pruning

### Product Unknowns
- ❓ **Actual user demand**: Validation conversations != real usage
  - **Mitigation:** Soft launch, iterate based on feedback
  
- ❓ **Most valuable property**: Which ADME property do users care about most?
  - **Mitigation:** Track usage analytics, ask users

- ❓ **Price sensitivity**: Will users pay $20-50/month?
  - **Mitigation:** Test different price points, offer free tier

### Data Unknowns
- ❓ **Dataset quality**: Public datasets may have errors
  - **Mitigation:** Cross-validate against multiple sources, manual spot-checks

- ❓ **Domain applicability**: Models trained on drug-like molecules may fail on non-drugs
  - **Mitigation:** Add applicability domain checker

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Poor model performance | Medium | High | Use proven architectures, benchmark against baselines |
| Low user adoption | Medium | High | Validate demand first, make UX great |
| Infrastructure costs too high | Low | Medium | Start with cheap hosting, scale gradually |
| Can't train models (no GPU) | Low | Medium | Use Google Colab, or rent cheap GPU |
| RDKit compatibility issues | Low | Low | Test on multiple browsers, provide fallback |
| Competition launches similar tool | Low | Medium | Move fast, focus on UX and content |

## Success Criteria

### Technical Milestones
- ✅ Models achieve target performance (R² > 0.65 for regression)
- ✅ API latency <200ms (p95)
- ✅ Frontend loads in <3 seconds
- ✅ 99% uptime after launch week

### Product Milestones
- ✅ 100 users in first month
- ✅ 500 predictions made
- ✅ Positive feedback from >75% of users
- ✅ <5% error rate

### Business Milestones (Post-Monetization)
- ✅ 20 paying users by month 6
- ✅ $500 MRR by month 6
- ✅ 50% user retention (month 1 to month 2)

## Open Questions & Decisions Needed

### Before Week 1
- [ ] Which cloud GPU provider for training? (Colab Pro vs Lambda Labs vs Paperspace)
- [ ] Exact ADME properties to include? (currently: 4 core properties)
- [ ] Dataset: ADMET-AI vs custom collection from ChEMBL?

### Before Week 2
- [ ] Hosting provider selection (Railway vs Render vs Fly.io)
- [ ] Domain name (suggestions: adme-predict.com, molprop.io, chempredict.app)
- [ ] Error response format (JSON structure)

### Before Week 3
- [ ] UI framework: Tailwind vs Material-UI vs custom CSS?
- [ ] Color scheme and branding
- [ ] Molecule drawer: Ketcher vs simple SMILES input only

### Before Week 4
- [ ] Analytics tool (Plausible vs Google Analytics vs PostHog)
- [ ] Monitoring/observability (Sentry vs LogRocket vs none for MVP)
- [ ] Launch strategy: Broad (HN, Reddit) vs targeted (email list only)

## Next Steps

1. **Immediate (this week):**
   - Set up development environment
   - Download ADMET-AI dataset
   - Run baseline experiments

2. **Short-term (next 2 weeks):**
   - Train models
   - Build API MVP
   - Create basic frontend

3. **Medium-term (next month):**
   - Deploy and launch
   - Collect feedback
   - Iterate based on usage

4. **Long-term (months 2-3):**
   - Add paid tiers
   - Expand features
   - Build content/community

---

**Document Status:** Living document, update as decisions are made and architecture evolves.

**Last Updated:** [Date]
**Version:** 0.1 (pre-development)
