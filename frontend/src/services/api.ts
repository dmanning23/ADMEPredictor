const BASE = '/api'

export interface RegressionResult {
  value: number
  unit: string
  confidence: number | null
}

export interface ClassificationResult {
  probability: number
  prediction: boolean
}

export interface PropertyResults {
  solubility: RegressionResult | null
  permeability: RegressionResult | null
  logp: RegressionResult | null
  cyp3a4_inhibitor: ClassificationResult | null
  herg_blocker: ClassificationResult | null
}

export interface RuleOfFive {
  passes: boolean
  violations: string[]
}

export interface PredictionResponse {
  smiles: string
  properties: PropertyResults
  warnings: string[]
  molecular_weight: number | null
  rule_of_five: RuleOfFive | null
}

export interface ValidationResponse {
  smiles: string
  valid: boolean
  canonical_smiles: string | null
  molecular_weight: number | null
  num_atoms: number | null
  error: string | null
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body?.detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export async function predict(smiles: string): Promise<PredictionResponse> {
  return request('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ smiles }),
  })
}

export async function predictBatch(smilesList: string[]): Promise<PredictionResponse[]> {
  return request('/predict/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ smiles_list: smilesList }),
  })
}

export async function validateSmiles(smiles: string): Promise<ValidationResponse> {
  const params = new URLSearchParams({ smiles })
  return request(`/validate?${params}`)
}
