import { EXAMPLE_MOLECULES } from '../utils/chemistry'

interface Props {
  onSelect: (smiles: string) => void
}

export function ExampleMolecules({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-sm text-gray-500 self-center">Examples:</span>
      {EXAMPLE_MOLECULES.map(({ name, smiles }) => (
        <button
          key={name}
          onClick={() => onSelect(smiles)}
          className="text-sm px-3 py-1 rounded-full border border-blue-200 text-blue-700 hover:bg-blue-50 transition"
        >
          {name}
        </button>
      ))}
    </div>
  )
}
