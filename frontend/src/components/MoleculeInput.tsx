import { ChangeEvent } from 'react'

interface Props {
  smiles: string
  onChange: (smiles: string) => void
  onSubmit: () => void
  loading: boolean
  valid: boolean | null
}

export function MoleculeInput({ smiles, onChange, onSubmit, loading, valid }: Props) {
  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    onChange(e.target.value)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter') onSubmit()
  }

  const borderClass =
    valid === null ? 'border-gray-300' :
    valid         ? 'border-green-500' :
                    'border-red-400'

  return (
    <div className="flex gap-2 w-full">
      <input
        type="text"
        value={smiles}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Enter SMILES (e.g. CC(=O)OC1=CC=CC=C1C(=O)O)"
        className={`flex-1 border-2 rounded-lg px-4 py-2 font-mono text-sm focus:outline-none ${borderClass}`}
      />
      <button
        onClick={onSubmit}
        disabled={loading || !smiles.trim()}
        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
      >
        {loading ? 'Predicting…' : 'Predict'}
      </button>
    </div>
  )
}
