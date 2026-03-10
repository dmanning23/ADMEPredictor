import { useMolecule } from './hooks/useMolecule'
import { usePrediction } from './hooks/usePrediction'
import { MoleculeInput } from './components/MoleculeInput'
import { MoleculeViewer } from './components/MoleculeViewer'
import { PredictionResults } from './components/PredictionResults'
import { ExampleMolecules } from './components/ExampleMolecules'

export default function App() {
  const { smiles, setSmiles, validation } = useMolecule()
  const { data, loading, error, run } = usePrediction()

  function handleSubmit() {
    if (smiles.trim()) run(smiles.trim())
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 py-4 px-6">
        <h1 className="text-xl font-bold text-gray-900">ADME Predictor</h1>
        <p className="text-sm text-gray-500">Predict drug-like ADME properties from SMILES</p>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 flex flex-col gap-6">
        <ExampleMolecules onSelect={setSmiles} />

        <MoleculeInput
          smiles={smiles}
          onChange={setSmiles}
          onSubmit={handleSubmit}
          loading={loading}
          valid={validation ? validation.valid : null}
        />

        {validation?.valid && (
          <MoleculeViewer smiles={smiles} canonicalSmiles={validation.canonical_smiles} />
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {data && <PredictionResults result={data} />}
      </main>
    </div>
  )
}
