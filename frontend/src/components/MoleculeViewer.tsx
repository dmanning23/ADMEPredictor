// frontend/src/components/MoleculeViewer.tsx
import { useEffect, useState } from 'react'
import { getRDKit } from '../services/rdkit'

interface Props {
  smiles: string
  canonicalSmiles: string | null
}

type ViewerState =
  | { status: 'loading' }
  | { status: 'ready'; dataUrl: string }
  | { status: 'error' }

export function MoleculeViewer({ smiles, canonicalSmiles }: Props) {
  const [state, setState] = useState<ViewerState>({ status: 'loading' })

  useEffect(() => {
    let cancelled = false

    async function render() {
      const input = canonicalSmiles ?? smiles
      try {
        const rdkit = await getRDKit()
        const mol = rdkit.get_mol(input)
        if (!mol) {
          // get_mol returns null for invalid SMILES — treat as error, not loading
          if (!cancelled) setState({ status: 'error' })
          return
        }
        let svg: string
        try {
          svg = mol.get_svg(288, 192)
        } finally {
          mol.delete()
        }
        const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
        if (!cancelled) setState({ status: 'ready', dataUrl })
      } catch (err) {
        console.error('RDKit render error:', err)
        if (!cancelled) setState({ status: 'error' })
      }
    }

    render()
    return () => { cancelled = true }
  }, [smiles, canonicalSmiles])

  const display = canonicalSmiles ?? smiles

  if (state.status === 'error') {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center text-sm text-gray-500">
        <p className="font-mono text-xs break-all">{display}</p>
        <p className="mt-2 italic text-amber-600">Structure preview unavailable</p>
      </div>
    )
  }

  if (state.status === 'ready') {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-col items-center gap-2">
        <img
          src={state.dataUrl}
          alt={`2D structure of ${display}`}
          className="w-72 h-48 object-contain"
        />
        <p className="font-mono text-xs text-gray-400 break-all">{display}</p>
      </div>
    )
  }

  // loading state — matches existing placeholder behaviour
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center text-sm text-gray-500">
      <p className="font-mono text-xs break-all">{display}</p>
      <p className="mt-2 italic">Loading structure…</p>
    </div>
  )
}
