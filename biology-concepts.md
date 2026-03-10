# ADME Biology & Chemistry Concepts

> A comprehensive guide to the biological and chemical principles behind ADME Predictor for software engineers entering drug discovery.

---

## Table of Contents

1. [What is ADME?](#what-is-adme)
2. [Why ADME Matters in Drug Discovery](#why-adme-matters)
3. [The Four Properties We Predict](#the-four-properties)
4. [Molecular Representations](#molecular-representations)
5. [Structure-Property Relationships](#structure-property-relationships)
6. [Drug-Likeness Rules](#drug-likeness-rules)
7. [Common Pitfalls & Edge Cases](#common-pitfalls)

---

## What is ADME?

**ADME** stands for **Absorption, Distribution, Metabolism, and Excretion** - the four key processes that determine what happens to a drug in the body.

Think of drug development like software deployment:
- **Absorption**: Can the code reach the server? (Can the drug get into the bloodstream?)
- **Distribution**: Does it reach all the right services? (Does the drug reach target tissues?)
- **Metabolism**: How does the system process it? (How does the body chemically modify the drug?)
- **Excretion**: How is it cleaned up? (How is the drug eliminated from the body?)

### The Journey of a Drug

```
1. ABSORPTION
   Pill swallowed → Dissolves in stomach → Crosses intestinal wall → Enters bloodstream
   
2. DISTRIBUTION  
   Bloodstream → Travels through body → Crosses barriers → Reaches target organ
   
3. METABOLISM
   Liver enzymes → Chemical modification → Active/inactive metabolites
   
4. EXCRETION
   Kidneys filter → Urine → Eliminated from body
   OR
   Liver → Bile → Feces → Eliminated
```

**The problem:** Most synthesized molecules fail at one of these steps, even if they're biologically active against the disease target.

**Example failure:**
- Molecule X kills cancer cells in a petri dish (great!)
- But it can't be absorbed from the gut (can't become a pill)
- And it's rapidly metabolized by the liver (won't last in the body)
- **Result:** Molecule X is worthless as a drug, despite being active

**Why prediction matters:** Testing ADME experimentally is expensive and time-consuming. If we can predict these properties computationally, we can filter out bad candidates before synthesis.

---

## Why ADME Matters in Drug Discovery

### The 80% Rule

**~80% of drug candidates fail in clinical trials due to poor ADME or toxicity.**

Only ~20% fail due to lack of efficacy (not working against the disease).

**Translation:** If you have a molecule that works perfectly against your target in a test tube, you still have <20% chance it becomes a drug.

### The Cost of Failure

**Stages of drug development:**

| Stage | Cost | Time | Success Rate |
|-------|------|------|--------------|
| Discovery (finding active molecules) | $1-5M | 1-2 years | N/A |
| Preclinical (animal testing, ADME) | $5-20M | 1-3 years | ~30% |
| Phase I (safety in humans) | $10-30M | 1-2 years | ~70% |
| Phase II (efficacy in patients) | $30-100M | 2-3 years | ~35% |
| Phase III (large trials) | $100-500M | 3-5 years | ~60% |

**If a drug fails in Phase III due to ADME issues that could have been predicted:**
- Wasted: $150-650M
- Wasted: 7-13 years
- Opportunity cost: thousands of patients who could have been treated

**Computational ADME prediction:**
- Cost: ~$0.01 per molecule
- Time: <1 second per molecule
- Can screen millions of molecules before synthesis

### Real-World Example: Why Pfizer Failed to Make a Better Viagra

**Background:** Viagra (sildenafil) has poor oral bioavailability (~40%) because of first-pass metabolism.

**What Pfizer tried:** Design a better PDE5 inhibitor (Viagra's target) with improved ADME.

**What happened:**
- Made dozens of more potent compounds (better activity in cells)
- But all had worse ADME (poor solubility, or rapid metabolism, or poor permeability)
- **None made it to market**

**The lesson:** You can't optimize activity and ADME separately. You need to predict ADME early and design molecules with good ADME from the start.

---

## The Four Properties We Predict

### 1. Solubility (Aqueous)

**What it is:** How well a molecule dissolves in water.

**Why water?** Your body is ~60% water. Blood is mostly water. Drugs must dissolve to be transported.

**Units:** LogS (log of molar solubility)
- LogS = -2 means solubility of 10^-2 M = 0.01 M = "moderately soluble"
- LogS = -6 means solubility of 10^-6 M = 0.000001 M = "poorly soluble"

**The chemistry:**

Molecules have both **hydrophilic** (water-loving) and **hydrophobic** (water-fearing) parts:

```
Aspirin: CC(=O)OC1=CC=CC=C1C(=O)O

Hydrophilic parts:
- C(=O)O  (carboxylic acid, can donate H-bonds)
- C(=O)O  (ester, can accept H-bonds)

Hydrophobic parts:
- Benzene ring (aromatic, oily)
- Methyl group (CH3, oily)

Balance: Moderately soluble (LogS ≈ -2.3)
```

**What makes molecules more soluble:**
- ✅ Polar functional groups (OH, COOH, NH2)
- ✅ Charges (NH3+, COO-)
- ✅ Smaller size
- ✅ Fewer aromatic rings

**What makes molecules less soluble:**
- ❌ Long hydrocarbon chains
- ❌ Many aromatic rings
- ❌ Large, flat molecules (stack together)
- ❌ Hydrophobic functional groups

**Why it matters for drugs:**

**Poor solubility → problems:**
1. Can't formulate as a pill (powder won't dissolve)
2. Variable absorption (depends on stomach contents)
3. Can crystallize in body (kidney stones, gout)
4. Hard to manufacture (can't purify if won't dissolve)

**Example:** Paclitaxel (cancer drug) has very poor solubility. Required special formulation with toxic solvents. Billions spent on better formulations.

---

### 2. Permeability (Membrane Crossing)

**What it is:** How easily a molecule crosses cell membranes.

**Why it matters:** Drugs must cross membranes to:
- Get from gut into bloodstream (intestinal wall)
- Get from blood into tissues (capillary walls)
- Get into cells (cell membrane)
- Cross blood-brain barrier (if targeting brain)

**The biology of membranes:**

Cell membranes are **lipid bilayers** - two layers of fatty molecules:

```
Outside cell
    |
    ↓
[Phospholipid heads (polar, hydrophilic)]
[Fatty acid tails (nonpolar, hydrophobic)]
[Fatty acid tails (nonpolar, hydrophobic)]
[Phospholipid heads (polar, hydrophilic)]
    ↓
    |
Inside cell
```

**Two ways to cross:**

1. **Passive diffusion** (no energy needed):
   - Molecule dissolves in the lipid layer
   - Diffuses through
   - Exits on other side
   - **Requirements:** Small, uncharged, moderately lipophilic

2. **Active transport** (uses cellular machinery):
   - Protein transporters carry molecule across
   - Requires energy (ATP)
   - **Not predictable** from structure alone (we don't predict this)

**Caco-2 permeability assay:**

Lab measurement using cultured intestinal cells:
- Grow cells on membrane filter
- Add drug on one side
- Measure how much crosses to other side
- **Units:** cm/s (centimeters per second)
- Typical range: 10^-7 to 10^-4 cm/s (we use log scale: -7 to -4)

**The chemistry:**

**Good permeability requires balance:**
- Not too polar (won't dissolve in membrane)
- Not too nonpolar (won't dissolve in water on either side)
- Not charged (charged molecules can't cross lipid layer)
- Not too large (big molecules diffuse slowly)

**Sweet spot:** LogP (lipophilicity) between 1 and 3

**Lipophilicity (LogP):**
- Measure of how much molecule prefers oil (octanol) vs water
- LogP = log([concentration in octanol] / [concentration in water])
- LogP = 2 means 100× more in oil than water
- Too low (<0): Won't cross membranes
- Too high (>5): Won't dissolve in water, might be toxic

**Example molecules:**

```
Ethanol (CH3CH2OH): LogP ≈ -0.3
- Very polar (OH group)
- High water solubility
- Poor membrane permeability
- Needs high doses (shots of vodka!)

Testosterone (steroid hormone): LogP ≈ 3.3
- Moderately lipophilic
- Good membrane permeability
- Can be absorbed through skin (patches work)

DDT (pesticide): LogP ≈ 6.9
- Very lipophilic
- Excellent membrane permeability
- Accumulates in fat tissue
- Toxic!
```

---

### 3. CYP3A4 Inhibition (Drug Metabolism)

**What it is:** Whether a molecule blocks the enzyme that metabolizes most drugs.

**The biology:**

**Cytochrome P450 enzymes (CYPs):** Family of enzymes in the liver that chemically modify drugs.

**Why metabolism exists:**
- Body sees drugs as foreign chemicals
- Tries to make them easier to excrete
- Adds oxygen, hydroxyl groups, etc.
- Makes molecules more water-soluble → easier to pee out

**CYP3A4 specifically:**
- Metabolizes ~50% of all drugs
- Located mainly in liver (some in intestines)
- Very important for drug clearance

**The problem: Drug-Drug Interactions**

**Scenario:**
1. Patient takes Drug A (metabolized by CYP3A4)
2. Patient takes Drug B (inhibits CYP3A4)
3. CYP3A4 is blocked
4. Drug A isn't metabolized
5. Drug A accumulates to toxic levels
6. **Patient has serious side effects or dies**

**Real example: Terfenadine (antihistamine)**
- Normally metabolized quickly by CYP3A4
- Safe at normal doses
- **But:** If taken with grapefruit juice or certain antibiotics (CYP3A4 inhibitors)
- Terfenadine accumulates
- Causes cardiac arrest
- **Withdrawn from market in 1998**

**The chemistry of inhibition:**

CYP3A4 has an active site (pocket) where drugs bind and get metabolized.

**Inhibitors:**
- Bind tightly to active site
- Block other drugs from binding
- Prevent metabolism

**Structural features of CYP3A4 inhibitors:**
- Often large, flat molecules (fit in active site)
- Aromatic rings (π-stacking with heme group)
- Basic nitrogen (coordinates with iron in heme)
- Moderate lipophilicity (LogP 2-4)

**Why we predict this:**
- Avoid drug-drug interactions
- Design safer drugs
- Understand metabolism pathways

---

### 4. hERG Blocking (Cardiotoxicity)

**What it is:** Whether a molecule blocks a potassium channel in the heart.

**The biology:**

**hERG channel (human Ether-à-go-go-Related Gene):**
- Potassium channel in heart muscle cells
- Critical for normal heartbeat rhythm
- Controls repolarization of heart cells

**Normal heart rhythm:**
```
1. Electrical signal triggers contraction
2. Sodium channels open → Na+ flows in → depolarization
3. Calcium channels open → Ca2+ flows in → contraction
4. Potassium channels (hERG) open → K+ flows out → repolarization
5. Heart relaxes
6. Repeat 60-100 times per minute
```

**When hERG is blocked:**
```
1-3. Same as normal
4. hERG blocked → K+ can't flow out → delayed repolarization
5. Heart can't relax properly
6. Next beat comes before heart is ready
7. Arrhythmia (irregular heartbeat)
8. Can progress to Torsades de Pointes (deadly arrhythmia)
9. Sudden cardiac death
```

**Why this is a huge problem:**

**Many drugs block hERG:**
- Antiarrhythmics (ironically)
- Antipsychotics
- Antibiotics
- Antihistamines
- Antidepressants

**Historical failures:**
- **Terfenadine** (antihistamine) - withdrawn 1998
- **Cisapride** (GI drug) - withdrawn 2000
- **Astemizole** (antihistamine) - withdrawn 1999

**FDA requirement:** All new drugs must be tested for hERG inhibition.

**The chemistry:**

**hERG blockers typically have:**
- Basic nitrogen (pKa 7-10)
  - Protonated at physiological pH
  - Positively charged
  - Interacts with negative residues in channel
- Two or more aromatic rings
- Lipophilic (LogP > 2)
- Specific distance between charged nitrogen and aromatic rings (~5-7 Å)

**Why we predict this:**
- Screen out cardiotoxic compounds early
- Save millions in failed drug development
- Most important safety filter in early discovery

---

## Molecular Representations

### SMILES (Simplified Molecular Input Line Entry System)

**What it is:** A way to represent molecules as text strings.

**Why it's useful:**
- Easy to type
- Works in databases
- No special characters (just ASCII)
- Can be canonicalized (unique representation)

**Basic rules:**

```
Atoms: C, N, O, S, P, etc.
Bonds: 
  - Single bond (default, can omit)
  = Double bond
  # Triple bond
  
Rings: Use numbers to close rings
Branches: Use parentheses

Examples:
Methane: C
Ethanol: CCO  (or CC(O), same thing)
Benzene: c1ccccc1  (lowercase = aromatic)
Aspirin: CC(=O)OC1=CC=CC=C1C(=O)O
```

**Reading SMILES:**

Let's decode aspirin: `CC(=O)OC1=CC=CC=C1C(=O)O`

```
CC          - Methyl group (CH3-C)
  (=O)      - Carbonyl (C=O) attached to previous C
     O      - Oxygen (ester linkage)
      C1    - Carbon (start of ring, labeled "1")
        =CC - Double bond to C, then C
           =CC - Another double bond to C, then C
              =C1 - Double bond to C, close ring (back to "1")
                 C(=O)O - Carboxylic acid group
```

**Canonical SMILES:**

Same molecule can have multiple valid SMILES:
- `CCO` and `OCC` both represent ethanol

**Canonical SMILES:** Unique representation using algorithm
- RDKit canonicalization is standard
- `CCO` is canonical, `OCC` is not

**Why this matters for ML:**
- Need consistent representation for training
- Always canonicalize SMILES before prediction

### Molecular Graphs

**What it is:** Representing molecules as mathematical graphs.

**Graph theory basics:**
- **Nodes (vertices):** Atoms
- **Edges:** Bonds
- **Node features:** Atom properties (element, charge, hybridization)
- **Edge features:** Bond properties (type, stereochemistry)

**Example: Water (H2O)**

```
Atoms (nodes):
  O: oxygen
  H: hydrogen
  H: hydrogen

Bonds (edges):
  O-H (single bond)
  O-H (single bond)

Graph:
  H
   \
    O
   /
  H
```

**For ML:**

Convert to adjacency matrix + feature matrix:

```python
# Adjacency matrix (3×3 for 3 atoms)
# 1 = connected, 0 = not connected
[[0, 1, 1],   # O connected to both H
 [1, 0, 0],   # H connected to O
 [1, 0, 0]]   # H connected to O

# Node features (one vector per atom)
O: [8, 2, 0, ...]  # atomic number, valence, charge, ...
H: [1, 1, 0, ...]
H: [1, 1, 0, ...]
```

**Why graphs for molecules?**
- Captures molecular structure directly
- No arbitrary ordering (unlike SMILES)
- Can use graph neural networks
- Naturally handles symmetry

---

## Structure-Property Relationships

### The Central Dogma of Medicinal Chemistry

**"Structure determines properties"**

Change the structure (atoms, bonds) → properties change predictably

### Key Concepts

#### 1. Lipophilicity (LogP)

**Partition coefficient:** Ratio of concentrations in octanol vs water

**Equation:** 
```
LogP = log([concentration in octanol] / [concentration in water])
```

**Rules of thumb:**
- Each CH2 group: +0.5 LogP
- Each OH group: -1.0 LogP
- Each aromatic ring: +1.5 LogP
- Charged groups: -3 to -4 LogP

**Example: Homologous series (alcohols)**
```
Methanol (CH3OH):      LogP = -0.77
Ethanol (CH3CH2OH):    LogP = -0.31  (+1 CH2)
Propanol (CH3CH2CH2OH): LogP = 0.25  (+1 CH2)
Butanol (CH3(CH2)2CH2OH): LogP = 0.88  (+1 CH2)
```

Pattern: Each CH2 adds ~0.5 to LogP

#### 2. Hydrogen Bonding

**Hydrogen bond:** Weak interaction between H on electronegative atom and lone pair

```
Example:
  O-H···O=C
  |      |
(donor)(acceptor)
```

**Donors:** OH, NH, SH (H attached to O, N, S)
**Acceptors:** O, N (with lone pairs)

**Effect on properties:**
- More H-bond donors → more soluble in water
- More H-bond acceptors → more soluble in water
- Too many H-bonds → can't cross membranes (too polar)

**Sweet spot for oral drugs:**
- H-bond donors: 0-5
- H-bond acceptors: 2-10

#### 3. Molecular Weight

**Effect on properties:**

**Small molecules (<200 Da):**
- Often gases or very volatile
- Hard to formulate
- Might lack specificity

**Medium molecules (200-500 Da):**
- Sweet spot for oral drugs
- Can cross membranes
- Still specific enough

**Large molecules (>500 Da):**
- Poor oral bioavailability
- Might need injection
- Often very specific

**Why size matters:**
1. **Permeability:** Large molecules diffuse slowly
2. **Solubility:** Large molecules have lower molar solubility
3. **Specificity:** Larger molecules can bind more specifically

#### 4. Polar Surface Area (PSA)

**Definition:** Sum of surface areas of polar atoms (O, N)

**Units:** Ų (square angstroms)

**Rules:**
- PSA < 60 Ų: Can cross blood-brain barrier
- PSA < 140 Ų: Can be orally bioavailable
- PSA > 140 Ų: Likely poor oral bioavailability

**Why it matters:**
- Polar groups can't cross lipid membranes easily
- PSA quantifies "how polar" a molecule is
- Better predictor than counting atoms

---

## Drug-Likeness Rules

### Lipinski's Rule of Five

**The most famous rule in medicinal chemistry**

**Statement:** An orally bioavailable drug should satisfy:
1. Molecular weight ≤ 500 Da
2. LogP ≤ 5
3. H-bond donors ≤ 5
4. H-bond acceptors ≤ 10

**Mnemonic:** All numbers are multiples of 5 (hence "Rule of Five")

**Origin:** 
- Christopher Lipinski (Pfizer)
- Analyzed 2,245 drugs in 1997
- Found >90% followed these rules

**Interpretation:**
- **Not a law of nature** - many exceptions exist
- **Guideline for oral drugs** - doesn't apply to injected drugs
- **Helps filter compound libraries**

**Violations:**
- 0 violations: ~80% oral bioavailability
- 1 violation: ~60% oral bioavailability
- 2+ violations: Often poor oral bioavailability

**Famous exceptions:**
- **Antibiotics** - often violate (need different properties)
- **Natural products** - evolved for different purposes
- **Atorvastatin (Lipitor)** - bestselling drug, violates MW rule

### Veber's Rules

**Additional rules for oral bioavailability:**
1. Rotatable bonds ≤ 10
2. PSA ≤ 140 Ų

**Rotatable bonds:** Single bonds that can rotate freely
- More rotatable bonds → more flexible
- Too flexible → multiple conformations → entropic penalty
- Affects both permeability and solubility

**Why these matter:**
- More specific than Lipinski
- Better predictors of oral bioavailability
- Used alongside Lipinski

### PAINS (Pan-Assay Interference Compounds)

**Definition:** Chemical structures that cause false positives in biological assays

**Common PAINS:**
- Quinones (reactive, oxidize)
- Rhodanines (promiscuous binders)
- Catechols (metal chelators)
- Alkylidene rhodanines
- Hydroxyphenyl hydrazones

**Why they're problematic:**
- Look active in assays but aren't really
- Waste time and money
- Never become drugs

**What to do:**
- Filter out PAINS early
- Use structural alerts
- RDKit has PAINS filters built-in

---

## Common Pitfalls & Edge Cases

### 1. Salts and Ionization

**Problem:** SMILES might represent salt form, not neutral form

```
Example:
Aspirin as sodium salt: CC(=O)OC1=CC=CC=C1C(=O)[O-].[Na+]
Aspirin neutral:        CC(=O)OC1=CC=CC=C1C(=O)O
```

**Solution:**
- Strip salts before prediction
- Predict on neutral form
- Use RDKit `RemoveHs()` and salt stripping

### 2. Tautomers

**Problem:** Same molecule, different proton positions

```
Example - Imidazole:
Form 1: c1[nH]cnc1
Form 2: c1nc[nH]c1

Same molecule, different SMILES!
```

**Solution:**
- Canonicalize tautomers
- Use dominant tautomer at pH 7.4
- RDKit `CanonicalTautomer()`

### 3. Stereochemistry

**Problem:** Same atoms/bonds, different 3D arrangement

```
Example - Thalidomide:
(R)-enantiomer: Treats morning sickness
(S)-enantiomer: Causes birth defects

But SMILES might not specify: c1cccc2C(=O)NC(=O)C(c3ccccc3)N12
```

**Solution:**
- Most ADME properties similar for enantiomers
- Metabolism might differ (CYP3A4 can be stereoselective)
- Include stereochemistry in SMILES if known: @ and @@

### 4. Metal-Containing Compounds

**Problem:** Organic molecules sometimes contain metals

```
Example - Cisplatin (cancer drug):
[Pt](Cl)(Cl)(N)N

Model trained on organic molecules might fail
```

**Solution:**
- Check for metals: `mol.GetAtoms()` and filter by atomic number
- Warn user if metal detected
- Have separate models for organometallics (future work)

### 5. Very Large Molecules

**Problem:** Biologics (proteins, antibodies) can't be represented well as SMILES

```
Insulin: 51 amino acids, MW ~5800 Da
SMILES: Would be thousands of characters
Not drug-like by any rule
```

**Solution:**
- Filter by size: reject if >100 heavy atoms or MW >1000 Da
- These need different prediction methods

### 6. Mixtures

**Problem:** Sometimes SMILES contains multiple molecules

```
Example: Drug with excipient
CC(=O)O.CCO  (acetic acid + ethanol)
```

**Solution:**
- Split on `.` to get components
- Either:
  - Predict largest component only
  - Warn user about mixture
  - Reject mixture

### 7. Out-of-Domain Molecules

**Problem:** Molecule very different from training data

**Signs:**
- Unusual functional groups
- Elements not in training (B, Si, Se)
- Very different size distribution
- Non-drug-like structure

**Solution:**
- Compute applicability domain
- Warn user if molecule is out-of-domain
- Lower confidence scores

---

## Further Reading

### Books
- **"The Organic Chemistry of Drug Design and Drug Action"** - Richard Silverman
- **"Drug-like Properties: Concepts, Structure Design and Methods"** - Kerns & Di

### Papers
- Lipinski et al. (1997) "Experimental and computational approaches to estimate solubility"
- Veber et al. (2002) "Molecular properties that influence oral bioavailability"
- Baell & Holloway (2010) "New substructure filters for PAINS"

### Online Resources
- **RDKit Documentation:** https://www.rdkit.org/docs/
- **DrugBank:** https://www.drugbank.ca/ (database of approved drugs)
- **PubChem:** https://pubchem.ncbi.nlm.nih.gov/ (chemical database)

---

**Next:** See [walkthrough.md](walkthrough.md) for a complete usage scenario from problem to solution.
