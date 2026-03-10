/**
 * 2D molecule structure viewer.
 * TODO: integrate RDKit.js for client-side SVG rendering.
 * For now renders canonical SMILES as a placeholder.
 */

interface Props {
  smiles: string
  canonicalSmiles: string | null
}

export function MoleculeViewer({ smiles, canonicalSmiles }: Props) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center text-sm text-gray-500">
      <p className="font-mono text-xs break-all">{canonicalSmiles ?? smiles}</p>
      <p className="mt-2 italic">2D structure viewer coming soon (RDKit.js)</p>
    </div>
  )
}
