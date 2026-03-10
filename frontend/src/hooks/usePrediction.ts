import { useState } from 'react'
import { predict, PredictionResponse } from '../services/api'

interface PredictionState {
  data: PredictionResponse | null
  loading: boolean
  error: string | null
}

export function usePrediction() {
  const [state, setState] = useState<PredictionState>({
    data: null,
    loading: false,
    error: null,
  })

  async function run(smiles: string) {
    setState({ data: null, loading: true, error: null })
    try {
      const data = await predict(smiles)
      setState({ data, loading: false, error: null })
    } catch (err) {
      setState({ data: null, loading: false, error: (err as Error).message })
    }
  }

  function reset() {
    setState({ data: null, loading: false, error: null })
  }

  return { ...state, run, reset }
}
